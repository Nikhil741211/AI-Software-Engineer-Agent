def classify_issue(issue_text):
    text = issue_text.lower()
    
    if any(word in text for word in ["login", "button", "ui", "page", "frontend", "react", "css"]):
        return "frontend"

    if any(word in text for word in ["api", "endpoint", "backend", "server", "fastapi", "request", "response"]):
        return "backend"

    if any(word in text for word in ["database", "migration", "postgres", "sql", "schema", "table"]):
        return "database"

    if any(word in text for word in ["docker", "kubernetes", "deployment", "redis", "worker", "devops"]):
        return "devops"

    if any(word in text for word in ["refactor", "cleanup", "restructure", "architecture"]):
        return "refactor"

    if any(word in text for word in ["test", "pytest", "failing", "assertion"]):
        return "test_failure"

    if any(word in text for word in ["security", "token", "secret", "auth", "vulnerability"]):
        return "security"

    return "bug"

def login_button_fix():
    issue = "login button not working"
    classification = classify_issue(issue)
    if classification == "frontend":
        print("Login button fix: Check frontend code")
        # Add frontend code fix here
        # For example:
        print("Login button fix: Check if the button has an onclick event")
        print("Login button fix: Check if the button is properly styled and displayed")
    elif classification == "backend":
        print("Login button fix: Check backend code")
        # Add backend code fix here
    else:
        print("Login button fix: Check other code")
        # Add other code fix here

login_button_fix()