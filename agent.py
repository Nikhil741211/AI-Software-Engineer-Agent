import os
from groq import Groq
from dotenv import load_dotenv

from tools import read_file, write_file, run_tests, get_file_tree, save_reasoning_log
from ast_tools import get_functions
from dependency_graph import get_imports
from database import init_db, save_issue
from rag_tools import search_relevant_files
from guardrails import check_cost_limit
from loop_detector import check_loop
from diff_tools import generate_diff
from safe_file_filter import filter_safe_files, is_safe_to_edit
from patch_parser import parse_patch
from code_validator import validate_patch_files
from function_patcher import (
    extract_target_function,
    extract_function_code,
    replace_function
)
from function_agent import generate_fixed_function

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_RETRIES = 3


def ask_ai(issue, code, files, retry_note=""):
    prompt = f"""
You are an expert Python software engineer.

BUG:
{issue}

RELEVANT FILES:
{files}

CODE CONTEXT:
{code}

{retry_note}

Fix the bug.

IMPORTANT:
Return ONLY valid JSON.
Do NOT use markdown.
Do NOT explain anything.

Return JSON exactly in this format:

{{
  "files": [
    {{
      "path": "full_path_to_file.py",
      "content_b64": "base64_encoded_full_updated_file_content"
    }}
  ]
}}

Rules:
- Only modify files listed in RELEVANT FILES.
- Use the exact file paths from RELEVANT FILES.
- Encode full updated file content using base64 and put it in content_b64.
- The decoded content must be valid Python code.
- Do not modify test files.
- Do not modify agent backend files.
- Do not include explanations.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def clean_json_output(text):
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()


def rollback_files(original_files, reasoning):
    reasoning.append("🔄 Tests failed, rolling back changes")

    for path, old_content in original_files.items():
        write_file(path, old_content)
        reasoning.append(f"✅ Rolled back: {path}")

    reasoning.append("✅ Rollback completed")


def save_final_result(issue, reasoning, approval_status):
    save_reasoning_log(reasoning)
    init_db()

    save_issue(
        issue_title=issue,
        reasoning_log="\n\n".join(reasoning),
        approval_status=approval_status,
        job_status=approval_status
    )

    return {"reasoning": reasoning}


def try_function_level_patch(issue, repo_path, matches, reasoning, original_files):
    target_function = extract_target_function(issue)

    if not target_function:
        reasoning.append("⚠️ No target function detected. Using file-level patching.")
        return None

    reasoning.append(f"🎯 Function-level patch target: {target_function}")

    for file in matches:
        old_content = read_file(file)

        if f"def {target_function}" not in old_content:
            continue

        function_code = extract_function_code(
            old_content,
            target_function
        )

        if not function_code:
            reasoning.append(
                f"❌ Could not extract function {target_function}"
            )
            continue

        fixed_function, function_error = generate_fixed_function(
            issue,
            target_function,
            function_code
        )

        if function_error:
            reasoning.append(
                f"❌ Function patch generation failed: {function_error}"
            )
            continue

        updated_content = replace_function(
            old_content,
            target_function,
            fixed_function
        )

        if updated_content is None:
            reasoning.append(
                f"❌ Could not replace function {target_function} in {file}"
            )
            continue

        original_files[file] = old_content

        code_diff = generate_diff(old_content, updated_content)
        reasoning.append(f"🧾 Function-level diff for {file}:")
        reasoning.append(code_diff)

        write_file(file, updated_content)
        reasoning.append(f"✅ Function-level patch written to: {file}")

        test_results = run_tests(repo_path)
        reasoning.append("🧪 Test Results:")
        reasoning.append(test_results)

        if "passed" in test_results:
            reasoning.append("✅ Tests passed")
            approval_status = "waiting_for_review"
        else:
            reasoning.append("❌ Tests failed")
            rollback_files(original_files, reasoning)
            approval_status = "tests_failed_rolled_back"

        reasoning.append("✅ Agent completed")

        return save_final_result(issue, reasoning, approval_status)

    reasoning.append(
        f"⚠️ Function {target_function} not found in safe files. Using file-level patching."
    )

    return None


def run_agent(issue, repo_path="workspace/test_repo"):
    reasoning = []
    original_files = {}

    reasoning.append(f"📩 Received issue: {issue}")
    reasoning.append(f"📦 Target repo path: {repo_path}")

    files = get_file_tree(repo_path)
    reasoning.append(f"📁 Project files: {files}")

    for file in files:
        try:
            funcs = get_functions(file)
            imports = get_imports(file)
            reasoning.append(f"📄 File: {file}")
            reasoning.append(f"Functions: {funcs}")
            reasoning.append(f"Imports: {imports}")
        except Exception as e:
            reasoning.append(f"Could not analyze {file}: {e}")

    reasoning.append("🧠 Running RAG semantic search")

    matches = search_relevant_files(issue, repo_path=repo_path)
    reasoning.append(f"🔍 RAG relevant files: {matches}")

    matches = filter_safe_files(matches)
    reasoning.append(f"🛡️ Safe editable files: {matches}")

    if not matches:
        reasoning.append("⛔ No safe editable files found. Agent stopped.")
        return save_final_result(issue, reasoning, "stopped_no_safe_files")

    can_continue, loop_message = check_loop(1)
    reasoning.append(f"🔁 Loop Check: attempt=1, status={loop_message}")

    if not can_continue:
        reasoning.append("⛔ Loop detected. Agent stopped.")
        return save_final_result(issue, reasoning, "stopped_loop_detected")

    combined_code = ""

    for file in matches:
        code = read_file(file)
        combined_code += f"\n\n# FILE: {file}\n"
        combined_code += code

    allowed, tokens, cost = check_cost_limit(issue + combined_code)
    reasoning.append(f"💰 Cost Check: tokens={tokens}, estimated_cost=${cost}")

    if not allowed:
        reasoning.append("⛔ Cost limit exceeded. Agent stopped.")
        return save_final_result(issue, reasoning, "stopped_cost_limit")

    function_result = try_function_level_patch(
        issue,
        repo_path,
        matches,
        reasoning,
        original_files
    )

    if function_result:
        return function_result

    patches = []

    for retry in range(1, MAX_RETRIES + 1):
        reasoning.append(f"🔄 Patch generation attempt {retry}/{MAX_RETRIES}")

        retry_note = ""
        if retry > 1:
            retry_note = """
Previous attempt failed.
Return valid JSON only.
Use content_b64 field only.
Ensure base64 decodes to valid Python code.
Use exact file paths from RELEVANT FILES.
Do not generate syntax errors.
"""

        ai_output = ask_ai(issue, combined_code, matches, retry_note)
        ai_output = clean_json_output(ai_output)

        reasoning.append("🤖 AI generated patch JSON")
        reasoning.append(ai_output)

        patches = parse_patch(ai_output)

        if patches:
            valid_patches, validation_errors = validate_patch_files(patches)

            if valid_patches:
                patches = valid_patches
                reasoning.append(
                    f"✅ Valid patch JSON and valid Python received on attempt {retry}"
                )
                break

            reasoning.append(
                f"❌ Patch JSON valid but Python syntax invalid on attempt {retry}"
            )

            for error in validation_errors:
                reasoning.append(
                    f"❌ Syntax error in {error['path']}: {error['error']}"
                )

        else:
            reasoning.append(f"❌ Invalid patch JSON on attempt {retry}")

        patches = []

    if not patches:
        reasoning.append("⛔ Max retries reached. No valid Python patch produced.")
        return save_final_result(
            issue,
            reasoning,
            "max_retries_invalid_python_patch"
        )

    patch_written = False

    for patch in patches:
        path = patch["path"]
        new_content = patch["content"]

        if path not in matches:
            reasoning.append(f"⛔ Skipped unmatched file: {path}")
            continue

        if not is_safe_to_edit(path):
            reasoning.append(f"⛔ Skipped protected file: {path}")
            continue

        old_content = read_file(path)
        original_files[path] = old_content

        code_diff = generate_diff(old_content, new_content)
        reasoning.append(f"🧾 Code Diff for {path}:")
        reasoning.append(code_diff)

        write_file(path, new_content)
        reasoning.append(f"✅ Patch written to: {path}")
        patch_written = True

    if not patch_written:
        reasoning.append("⛔ No valid patches were written. Agent stopped.")
        return save_final_result(issue, reasoning, "stopped_no_valid_patch")

    test_results = run_tests(repo_path)
    reasoning.append("🧪 Test Results:")
    reasoning.append(test_results)

    if "passed" in test_results:
        reasoning.append("✅ Tests passed")
        approval_status = "waiting_for_review"
    else:
        reasoning.append("❌ Tests failed")
        rollback_files(original_files, reasoning)
        approval_status = "tests_failed_rolled_back"

    reasoning.append("✅ Agent completed")

    return save_final_result(issue, reasoning, approval_status)