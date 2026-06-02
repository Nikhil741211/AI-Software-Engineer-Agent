MAX_ATTEMPTS = 3
MAX_TOKENS = 5000
MAX_COST = 1.00


def check_attempt_limit(attempts):
    return attempts < MAX_ATTEMPTS


def estimate_tokens(text):
    return len(text.split())


def estimate_cost(tokens):
    return tokens * 0.00001


def check_cost_limit(text):
    tokens = estimate_tokens(text)
    cost = estimate_cost(tokens)

    if tokens > MAX_TOKENS:
        return False, tokens, cost

    if cost > MAX_COST:
        return False, tokens, cost

    return True, tokens, cost
