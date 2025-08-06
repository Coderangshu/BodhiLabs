#!/usr/bin/python3
import json, os, copy, subprocess

os.system('clear')

# The data Structure for final results to be stored in evaluate.json
overall = {
    "data": []
}

# Template
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

path = '/home/.evaluationScripts/'

inputFile = path + '.bodhiFiles/answer.txt'
jsonPath = path + 'evaluate.json'
goToWorkDir = "cd /home/labDirectory && "

# Define the correct command and expected output
correct_commands = ["ls -RSa", "ls -lhRS | grep -v '^total' | grep -v ':$' | head -n 1"]  # replace with expected commands
correct_outputs = []
try:
    for command in correct_commands:
        # Run the command and capture the output
        command = goToWorkDir + command  # Ensure the command runs in the correct directory
        output = subprocess.check_output(command, shell=True, text=True).strip()
        correct_outputs.append(output)
except Exception as e:
    correct_output = ""
    print("Error running correct command:", e)

if os.path.isfile(inputFile):
    with open(inputFile, 'r') as file:
        lines = file.readlines()

    student_commands = []
    for i, line in enumerate(lines):
        line = line.strip()
        student_commands.append(line)

    for i, correct_output in enumerate(correct_outputs):
        line = student_commands[i] if i < len(student_commands) else ""
        student_command = goToWorkDir + line
        entry = copy.deepcopy(template)
        entry["testid"] = i
        try:
            student_output = subprocess.check_output(student_command, shell=True, text=True).strip()
            if student_output == correct_output:
                entry["message"] = f"{line}: PASS"
                entry["score"] = 1
                entry["status"] = "success"
            else:
                entry["message"] = f"{line}: FAIL - Output mismatch"
        except subprocess.CalledProcessError as e:
            entry["message"] = f"{line}: FAIL - Command not found"

        overall["data"].append(entry)
else:
    entry = copy.deepcopy(template)
    entry['message'] = f"answer.txt not found. Evaluation result not generated."
    overall["data"].append(entry)

# Store evaluation results
with open(jsonPath, 'w', encoding='utf-8') as f:
    json.dump(overall, f, indent=4)

# Show evaluation results
with open(jsonPath, 'r', encoding='utf-8') as f:
    for line in f.readlines():
        print(line)

