from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from rag_tools import search_relevant_files
from tools import read_file, write_file, run_tests
from agent import ask_ai, clean_code


class AgentState(TypedDict):
    issue: str
    files: List[str]
    selected_file: str
    code: str
    file_codes: Dict[str, str]
    fixed_code: str
    test_results: str
    status: str


def analyze_issue(state: AgentState):
    print("Analyze Issue")
    state["status"] = "issue_analyzed"
    return state


def rag_search_node(state: AgentState):
    print("RAG Search")

    files = search_relevant_files(state["issue"])

    state["files"] = files

    if files:
        state["selected_file"] = files[0]
    else:
        state["selected_file"] = ""

    print(f"Relevant files: {files}")

    return state


def read_code_node(state: AgentState):
    print("Read Multiple Files")

    combined_code = ""
    file_codes = {}

    for file in state["files"]:
        try:
            code = read_file(file)
            file_codes[file] = code

            combined_code += f"\n\n# FILE: {file}\n"
            combined_code += code

        except Exception as e:
            print(f"Could not read {file}: {e}")

    state["file_codes"] = file_codes
    state["code"] = combined_code

    return state


def generate_fix_node(state: AgentState):
    print("Generate Multi-file Aware Fix")

    prompt_code = state["code"]

    fixed_code = ask_ai(state["issue"], prompt_code)
    fixed_code = clean_code(fixed_code)

    state["fixed_code"] = fixed_code

    return state


def write_fix_node(state: AgentState):
    print("Write Fix")

    target_file = state["selected_file"]

    if not target_file:
        state["status"] = "no_target_file"
        return state

    write_file(target_file, state["fixed_code"])

    print(f"Fix written to {target_file}")

    return state


def run_tests_node(state: AgentState):
    print("Run Tests")

    test_results = run_tests()
    state["test_results"] = test_results

    if "passed" in test_results:
        state["status"] = "tests_passed"
    else:
        state["status"] = "tests_failed"

    return state


workflow = StateGraph(AgentState)

workflow.add_node("analyze_issue", analyze_issue)
workflow.add_node("rag_search", rag_search_node)
workflow.add_node("read_code", read_code_node)
workflow.add_node("generate_fix", generate_fix_node)
workflow.add_node("write_fix", write_fix_node)
workflow.add_node("run_tests", run_tests_node)

workflow.set_entry_point("analyze_issue")

workflow.add_edge("analyze_issue", "rag_search")
workflow.add_edge("rag_search", "read_code")
workflow.add_edge("read_code", "generate_fix")
workflow.add_edge("generate_fix", "write_fix")
workflow.add_edge("write_fix", "run_tests")
workflow.add_edge("run_tests", END)

graph = workflow.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "issue": "divide by zero bug",
        "files": [],
        "selected_file": "",
        "code": "",
        "file_codes": {},
        "fixed_code": "",
        "test_results": "",
        "status": ""
    })

    print(result)


def divide(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both inputs must be numbers")
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def safe_divide(a, b):
    try:
        return divide(a, b)
    except Exception as e:
        print(f"An error occurred in safe_divide: {e}")
        return None


def main():
    print(safe_divide(10, 0))
    print(safe_divide(10, 'a'))


if __name__ == "__main__":
    main()