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

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_ai(issue, code, files):
    prompt = f"""
You are an expert Python software engineer.

BUG:
{issue}

RELEVANT FILES:
{files}

CODE CONTEXT:
{code}

Fix the bug.

IMPORTANT:
Return ONLY valid JSON.
Do NOT use markdown.
Do NOT explain anything.

Return JSON exactly in this format:

{{
  "files": [
    {{
      "path": "workspace/test_repo/sample_code.py",
      "content_b64": "base64_encoded_full_updated_file_content"
    }}
  ]
}}

Rules:
- Only modify files listed in RELEVANT FILES.
- Encode full updated file content using base64 and put it in content_b64.
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


def run_agent(issue):
    reasoning = []
    original_files = {}

    reasoning.append(f"📩 Received issue: {issue}")

    files = get_file_tree()
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

    matches = search_relevant_files(issue)
    reasoning.append(f"🔍 RAG relevant files: {matches}")

    matches = filter_safe_files(matches)
    reasoning.append(f"🛡️ Safe editable files: {matches}")

    if not matches:
        reasoning.append("⛔ No safe editable files found. Agent stopped.")
        save_reasoning_log(reasoning)
        init_db()
        save_issue(issue, "\n\n".join(reasoning), "stopped_no_safe_files")
        return {"reasoning": reasoning}

    can_continue, loop_message = check_loop(1)
    reasoning.append(f"🔁 Loop Check: attempt=1, status={loop_message}")

    if not can_continue:
        reasoning.append("⛔ Loop detected. Agent stopped.")
        save_reasoning_log(reasoning)
        init_db()
        save_issue(issue, "\n\n".join(reasoning), "stopped_loop_detected")
        return {"reasoning": reasoning}

    combined_code = ""

    for file in matches:
        code = read_file(file)
        combined_code += f"\n\n# FILE: {file}\n"
        combined_code += code

    allowed, tokens, cost = check_cost_limit(issue + combined_code)
    reasoning.append(f"💰 Cost Check: tokens={tokens}, estimated_cost=${cost}")

    if not allowed:
        reasoning.append("⛔ Cost limit exceeded. Agent stopped.")
        save_reasoning_log(reasoning)
        init_db()
        save_issue(issue, "\n\n".join(reasoning), "stopped_cost_limit")
        return {"reasoning": reasoning}

    ai_output = ask_ai(issue, combined_code, matches)
    ai_output = clean_json_output(ai_output)

    reasoning.append("🤖 AI generated patch JSON")
    reasoning.append(ai_output)

    patches = parse_patch(ai_output)

    if not patches:
        reasoning.append("⛔ AI did not return valid patch JSON. Agent stopped.")
        save_reasoning_log(reasoning)
        init_db()
        save_issue(issue, "\n\n".join(reasoning), "stopped_invalid_patch")
        return {"reasoning": reasoning}

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
        save_reasoning_log(reasoning)
        init_db()
        save_issue(issue, "\n\n".join(reasoning), "stopped_no_valid_patch")
        return {"reasoning": reasoning}

    test_results = run_tests()
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

    save_reasoning_log(reasoning)
    init_db()
    save_issue(issue, "\n\n".join(reasoning), approval_status)

    return {"reasoning": reasoning}
