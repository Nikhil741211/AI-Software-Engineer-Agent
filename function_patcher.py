import ast


def find_function_range(source_code, function_name):
    tree = ast.parse(source_code)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return node.lineno, node.end_lineno

    return None, None


def extract_function_code(source_code, function_name):
    start_line, end_line = find_function_range(source_code, function_name)

    if start_line is None or end_line is None:
        return None

    lines = source_code.splitlines()

    return "\n".join(lines[start_line - 1:end_line])


def replace_function(source_code, function_name, new_function_code):
    start_line, end_line = find_function_range(source_code, function_name)

    if start_line is None or end_line is None:
        return None

    lines = source_code.splitlines()

    before = lines[:start_line - 1]
    after = lines[end_line:]

    new_lines = new_function_code.strip().splitlines()

    return "\n".join(before + new_lines + after) + "\n"


def extract_target_function(issue_text):
    text = issue_text.lower()

    if "divide" in text or "division" in text or "zero" in text:
        return "divide"

    return None
