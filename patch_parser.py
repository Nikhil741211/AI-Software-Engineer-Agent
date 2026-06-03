import json
import base64


def parse_patch(ai_output):
    text = ai_output.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        data = json.loads(text)
    except Exception:
        return []

    patches = []

    for item in data.get("files", []):
        path = item.get("path")
        content_b64 = item.get("content_b64")

        if not path or not content_b64:
            continue

        try:
            content = base64.b64decode(content_b64).decode("utf-8")
        except Exception:
            continue

        patches.append({
            "path": path,
            "content": content
        })

    return patches
