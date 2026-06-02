MAX_ATTEMPTS = 3


def should_continue(attempts):
    return attempts < MAX_ATTEMPTS


def check_loop(attempts):
    if attempts >= MAX_ATTEMPTS:
        return False, f"Loop detected after {attempts} attempts"

    return True, "Safe to continue"
