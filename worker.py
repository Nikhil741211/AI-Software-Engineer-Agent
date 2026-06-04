from agent import run_agent
from repo_manager import clone_or_update_repo


def process_issue(job_payload):
    if isinstance(job_payload, dict):
        issue = job_payload.get("issue_title", "")
        repo_name = job_payload.get("repo_name", "real_repo")
        repo_full_name = job_payload.get("repo_full_name", "")
        clone_url = job_payload.get("clone_url", "")
    else:
        issue = job_payload
        repo_name = "real_repo"
        repo_full_name = ""
        clone_url = ""

    print("⚙️ Processing issue:", issue)
    print("📦 Repository:", repo_full_name)
    print("🔗 Clone URL:", clone_url)
    print("📌 Status: running")

    if clone_url:
        repo_path = clone_or_update_repo(clone_url, repo_name)
        print("✅ Repository ready at:", repo_path)
    else:
        repo_path = "workspace/test_repo"
        print("⚠️ No clone URL found. Using fallback repo:", repo_path)

    result = run_agent(issue, repo_path)

    print("\n🤖 Agent Reasoning:\n")

    for step in result["reasoning"]:
        print(step)

    print("\n✅ Finished processing")