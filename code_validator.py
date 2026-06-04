import ast


def validate_python(code: str):
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


def is_valid_python(code):
    valid, error = validate_python(code)

    if valid:
        return True, "Valid Python"

    return False, error


def validate_patch_files(patches):
    valid_patches = []
    errors = []

    for patch in patches:
        path = patch.get("path")
        content = patch.get("content", "")

        if path and path.endswith(".py"):
            is_valid, message = is_valid_python(content)

            if not is_valid:
                errors.append({
                    "path": path,
                    "error": message
                })
                continue

        valid_patches.append(patch)

    return valid_patches, errors
