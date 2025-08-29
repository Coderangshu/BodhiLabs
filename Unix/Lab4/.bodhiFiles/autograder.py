#!/usr/bin/python3
import json, os, copy, subprocess, filecmp

os.system('clear')

overall = {"data": []}
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

# Paths
base_path = '/home/.evaluationScripts/'
input_file = base_path + '.bodhiFiles/answer.txt'
json_path = base_path + 'evaluate.json'
lab_path = '/home/labDirectory'
expected_output_file = os.path.join(lab_path, 'expected.txt')
student_output_file = os.path.join(lab_path, 'output.txt')  # students must redirect here

# Generate expected output
try:
    command = f"cd {lab_path} && head -n 50 example.txt | tail -n 10 > expected.txt"
    subprocess.run(command, shell=True, check=True)
except Exception as e:
    print("Error generating expected output:", e)

# Check if student's answer.txt exists
if os.path.isfile(input_file):
    with open(input_file, 'r') as file:
        student_commands = [line.strip() for line in file if line.strip()]

    entry = copy.deepcopy(template)
    entry["testid"] = 1

    try:
        # Combine all commands into one script
        combined_script = " && ".join(student_commands)

        # Run all commands in sequence
        full_command = f"cd {lab_path} && {combined_script}"
        subprocess.run(full_command, shell=True, check=True)

        # Validate final output
        if not os.path.isfile(student_output_file):
            entry["message"] = f"FAIL - output.txt not created"
        else:
            if filecmp.cmp(expected_output_file, student_output_file, shallow=False):
                entry["message"] = f"PASS"
                entry["score"] = 1
                entry["status"] = "success"
            else:
                entry["message"] = f"FAIL - output mismatch"

    except subprocess.CalledProcessError:
        entry["message"] = "FAIL - Command execution failed"

    overall["data"].append(entry)

else:
    entry = copy.deepcopy(template)
    entry['message'] = f"answer.txt not found. Evaluation result not generated."
    overall["data"].append(entry)

# Write evaluation results
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(overall, f, indent=4)

# Show evaluation results
with open(json_path, 'r', encoding='utf-8') as f:
    print(f.read())

