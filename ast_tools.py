import ast

def get_functions(file_path):
    with open(file_path, "r") as f:
        code = f.read()

    tree = ast.parse(code)

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    return functions
