import subprocess
import json
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
lab_dir = os.path.abspath(os.path.join(base_dir, "../labDirectory"))
output_file = os.path.join(base_dir, "evaluate.json")

def run_autograder(form_name, script_name):
    form_dir = os.path.join(lab_dir, form_name)
    grader_script = os.path.join(base_dir, script_name)

    subprocess.run(["python3", grader_script], cwd=form_dir)

    partial_result_file = os.path.join(base_dir, "evaluate.json")
    if os.path.exists(partial_result_file):
        with open(partial_result_file) as f:
            data = json.load(f)
        os.remove(partial_result_file)
        return data.get("data", [])
    return []

combined_data = []

combined_data += run_autograder("links", "autograder-links.py")
combined_data += run_autograder("lists", "autograder-lists.py")
combined_data += run_autograder("tables", "autograder-tables.py")

with open(output_file, "w") as f:
    json.dump({"data": combined_data}, f, indent=4)

