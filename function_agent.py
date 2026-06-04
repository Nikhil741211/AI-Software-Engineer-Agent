import os
from groq import Groq
from dotenv import load_dotenv

from code_validator import validate_python

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean_function_output(text):
    text = text.replace("```python", "")
    text = text.replace("```", "")
    return text.strip()


def generate_fixed_function(issue, function_name, function_code):
    prompt = f"""
You are an expert Python developer.

Fix ONLY this Python function.

BUG:
{issue}

FUNCTION NAME:
{function_name}

CURRENT FUNCTION:
{function_code}

Return ONLY one valid Python function definition.
Do not include markdown.
Do not include explanation.
Do not include JSON.
Do not include imports.
Do not include test code.
Do not include extra text.

Rules:
- The output must start with: def {function_name}
- The output must be valid Python syntax.
- Keep the same function name.
- Keep simple readable Python.
- For divide by zero, return None instead of crashing.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    fixed_function = clean_function_output(
        response.choices[0].message.content.strip()
    )

    if not fixed_function.startswith(f"def {function_name}"):
        return None, "LLM did not return the correct function definition"

    valid, error = validate_python(fixed_function)

    if not valid:
        return None, error

    return fixed_function, None