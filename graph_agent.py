from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from rag_tools import search_relevant_files
from tools import read_file, write_file, run_tests
from agent import ask_ai, clean_code


class AgentState(TypedDict):
    issue: str
    files: List[str]
    selected_file: str
    code: str
    fixed_code: str
    test_results: str
    status: str


def analyze_issue(state: AgentState):
    print("🔍 Analyze Issue")
    state["status"] = "issue_analyzed"
    return state


def rag_search_node(state: AgentState):
    print("🧠 RAG Search")
    files = search_relevant_files(state["issue"])
    state["files"] = files
    state["selected_file"] = files[0]
    return state


def read_code_node(state: AgentState):
    print("📖 Read Code")
    code = read_file(state["selected_file"])
    state["code"] = code
    return state


def generate_fix_node(state: AgentState):
    print("🤖 Generate Fix")
    fixed_code = ask_ai(state["issue"], state["code"])
    fixed_code = clean_code(fixed_code)
    state["fixed_code"] = fixed_code
    return state


def write_fix_node(state: AgentState):
    print("✍️ Write Fix")
    write_file(state["selected_file"], state["fixed_code"])
    return state


def run_tests_node(state: AgentState):
    print("🧪 Run Tests")
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
        "fixed_code": "",
        "test_results": "",
        "status": ""
    })

    print(result)
