#!/usr/bin/python3
import json, os, subprocess, copy, filecmp

os.system('clear')

# ---------- Common Settings ----------
overall = {"data": []}
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

base_path = '/home/.evaluationScripts/'
json_path = base_path + 'evaluate.json'

lab_path = '/home/labDirectory'
input_file = '/home/labDirectory/answer.txt'

# For Test 1 (head | tail)
expected_output_file = os.path.join(lab_path, 'expected.txt')
student_output_file = os.path.join(lab_path, 'output.txt')  # students must redirect here

# For Test 2 (MIME type)
backup_file = '/tmp/mystery_file_backup'

# ======================================================
# TEST 1: Validate head | tail command output
# ======================================================
try:
    # Generate expected output
    command = f"cd {lab_path} && head -n 50 example.txt | tail -n 10 > expected.txt"
    subprocess.run(command, shell=True, check=True)
except Exception as e:
    print("Error generating expected output:", e)

entry1 = copy.deepcopy(template)
entry1["testid"] = 1

if os.path.isfile(input_file):
    with open(input_file, 'r') as file:
        student_commands = [line.strip() for line in file if line.strip()]

    try:
        # Combine all commands into one script
        combined_script = " && ".join(student_commands)

        # Run all commands in sequence
        full_command = f"cd {lab_path} && {combined_script}"
        subprocess.run(full_command, shell=True, check=True)

        # Validate final output
        if not os.path.isfile(student_output_file):
            entry1["message"] = f"FAIL - output.txt not created"
        else:
            if filecmp.cmp(expected_output_file, student_output_file, shallow=False):
                entry1["message"] = f"PASS"
                entry1["score"] = 1
                entry1["status"] = "success"
            else:
                entry1["message"] = f"FAIL - output mismatch"

    except subprocess.CalledProcessError:
        entry1["message"] = "FAIL - Command execution failed"
else:
    entry1["message"] = f"answer.txt not found. Evaluation result not generated."

overall["data"].append(entry1)

# ======================================================
# TEST 2: Validate MIME type check
# ======================================================
entry2 = copy.deepcopy(template)
entry2["testid"] = 2

# Get correct MIME type using 'file --mime-type'
try:
    correct_mime = subprocess.check_output(
        ['file', '--mime-type', '-b', backup_file],
        text=True
    ).strip()
except Exception as e:
    correct_mime = None

if not correct_mime:
    entry2["message"] = "Failed to determine correct MIME type of file."
else:
    if os.path.isfile(input_file):
        with open(input_file, 'r') as f:
            student_command = f.read().strip()

        if student_command:
            try:
                # Run student's command in the lab directory
                student_output = subprocess.check_output(
                    student_command,
                    shell=True,
                    cwd=lab_path,
                    text=True
                ).strip()

                # Check if correct MIME type appears in student's output
                if correct_mime in student_output:
                    entry2["message"] = f"PASS: MIME type '{correct_mime}' found."
                    entry2["status"] = "success"
                    entry2["score"] = 1
                else:
                    entry2["message"] = f"FAIL: MIME type not found."
            except subprocess.CalledProcessError as e:
                entry2["message"] = f"FAIL: Error running student's command: {e}"
        else:
            entry2["message"] = "FAIL: answer.txt is empty."
    else:
        entry2["message"] = "FAIL: answer.txt not found."

overall["data"].append(entry2)

# ======================================================
# SAVE AND DISPLAY FINAL RESULT
# ======================================================
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(overall, f, indent=4)

with open(json_path, 'r', encoding='utf-8') as f:
    print(f.read())

