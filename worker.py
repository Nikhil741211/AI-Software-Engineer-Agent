from agent import run_agent

def process_issue(issue):
    print("⚙️ Processing issue:", issue)

    result = run_agent(issue)

    print("\n🤖 Agent Reasoning:\n")

    for step in result["reasoning"]:
        print(step)

    print("\n✅ Finished processing")