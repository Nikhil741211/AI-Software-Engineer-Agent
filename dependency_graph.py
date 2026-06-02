import ast

def get_imports(file_path):
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    return imports
