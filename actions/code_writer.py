import os
from brain.llm_handler import generate_code_response

def generate_code(prompt):
    return generate_code_response(prompt)


def save_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"{filename} created successfully."


def create_project(project_name, structure):
    os.makedirs(project_name, exist_ok=True)

    for file_name, file_content in structure.items():
        path = os.path.join(project_name, file_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)

    return f"Project '{project_name}' created."
def fix_error(error_message, code_content):
    prompt = f"""
             You are a senior Python engineer.
             Write production-ready code only.
             Do NOT explain anything.
             Do NOT wrap code in markdown.
             Include all imports.
             Ensure the code runs without modification.
             If needed, include a main guard.
             Return only executable code.
             Review the following code as a senior software architect.
             List bugs, edge cases, improvements.
             If issues exist, rewrite improved version.
             Return full corrected code only.

             The following code has an error.


             Error:
             {error_message}

             Code:
             {code_content}

             Fix the code and return ONLY corrected version.
           """

    return generate_code(prompt)