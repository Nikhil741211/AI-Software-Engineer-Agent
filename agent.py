from issue_classifier import classify_issue
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

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_ai(issue, code):
    prompt = f"""
You are an expert Python software engineer.

BUG:
{issue}

CODE:
{code}

Fix the bug.

IMPORTANT:
- Return ONLY Python code
- Do NOT use markdown
- Do NOT use ```python
- Do NOT use ```
- Do NOT explain anything
- Output raw Python code only
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


def clean_code(code):
    code = code.replace("```python", "")
    code = code.replace("```", "")
    return code.strip()


def run_agent(issue):
    reasoning = []
    issue_type = classify_issue(issue)
    reasoning.append(f"🧩 Issue classified as: {issue_type}")

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

    attempts = 0

    for file in matches:
        attempts += 1

        can_continue, loop_message = check_loop(attempts)
        reasoning.append(
            f"🔁 Loop Check: attempt={attempts}, status={loop_message}"
        )

        if not can_continue:
            reasoning.append("⛔ Loop detected. Agent stopped.")
            save_reasoning_log(reasoning)

            init_db()
            save_issue(
                issue_title=issue,
                reasoning_log="\n\n".join(reasoning),
                approval_status="stopped_loop_detected"
            )

            return {
                "reasoning": reasoning
            }

        if not file.endswith(".py"):
            continue

        code = read_file(file)
        reasoning.append(f"📖 Reading file: {file}")

        allowed, tokens, cost = check_cost_limit(issue + code)

        reasoning.append(
            f"💰 Cost Check: tokens={tokens}, estimated_cost=${cost}"
        )

        if not allowed:
            reasoning.append("⛔ Cost limit exceeded. Agent stopped.")
            save_reasoning_log(reasoning)

            init_db()
            save_issue(
                issue_title=issue,
                reasoning_log="\n\n".join(reasoning),
                approval_status="stopped_cost_limit"
            )

            return {
                "reasoning": reasoning
            }

        fixed_code = ask_ai(issue, code)
        fixed_code = clean_code(fixed_code)

        reasoning.append("🤖 AI generated fix")
        reasoning.append(fixed_code)

        write_file(file, fixed_code)
        reasoning.append(f"✅ Fixed code written to: {file}")

        test_results = run_tests()
        reasoning.append("🧪 Test Results:")
        reasoning.append(test_results)

        if "passed" in test_results:
            reasoning.append("✅ Tests passed, stopping further file edits")
            break

    reasoning.append("✅ Agent completed")

    save_reasoning_log(reasoning)

    init_db()

    save_issue(
        issue_title=issue,
        reasoning_log="\n\n".join(reasoning),
        approval_status="waiting_for_review"
    )

    return {
        "reasoning": reasoning
    }
