#!/usr/bin/env python3

import os, subprocess, json, difflib, copy, shutil

# Base Paths
base = "/home/.evaluationScripts/.bodhiFiles"
student_dir = os.path.join("/home", "labDirectory")
expected_dir = os.path.join(base, "expected")
original_story = os.path.join(base, "original_story.txt")
output_json = os.path.join("/home/.evaluationScripts", "evaluate.json")

# Template
template = {
    "testid": 1,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed"
}
results = {"data": []}

total_steps = 7
story_path = os.path.join(student_dir, "story.txt")

# Reset story.txt at the beginning
shutil.copyfile(original_story, story_path)

# --- Logic for deciding whether to use normal! ---
def needs_normal_prefix(command: str) -> bool:
    command = command.strip()

    if command.startswith(':'):
        return False

    # Known ex command starters
    ex_keywords = ['wq', 'q', 'w', 'set', 'map', 'syntax', 'file', 's/', '%s/', 'g/', 'v/', 'let', 'if', 'endif']
    if any(command.startswith(kw) for kw in ex_keywords):
        return False

    # Normal mode operators that modify content or move cursor
    normal_prefixes = [
        'gg', 'G', 'dd', 'yy', 'p', 'P', 'x', 'u', '0', '$', '^', '/', '?', 'n',
        'O', 'o', 'A', 'I', 'C', 'S', 'J', '>>', '<<'
    ]

    for key in normal_prefixes:
        if command == key or command.startswith(key):
            return True

    return True  # default to True for safety

print("Starting autograder...")

# --- Main Evaluation Loop ---
for step in range(1, total_steps + 1):
    print("Step ", step)
    test = copy.deepcopy(template)
    test["testid"] = step
    student_answer_file = os.path.join(student_dir, f"answer{step}.txt")
    expected_step_file = os.path.join(expected_dir, f"step{step}.txt")

    if not os.path.exists(student_answer_file):
        test["message"] = f"answer{step}.txt not found"
        results["data"].append(test)
        continue

    # Read student commands
    with open(student_answer_file) as f:
        raw_commands = [line.strip() for line in f if line.strip()]

    # Skip and mark pass for undo/redo test cases
    if step==4:
        if raw_commands == ['u']:
            test["status"] = "success"
            test["score"] = 1
            test["message"] = f"Task {step}: PASS (undo)"
            results["data"].append(test)
            continue
        else:
            test["message"] = f"Task {step}: FAIL"
            results["data"].append(test)
            continue
    elif step==5:
        if raw_commands == ['<C-r>']:
            test["status"] = "success"
            test["score"] = 1
            test["message"] = f"Task {step}: PASS (redo)"
            results["data"].append(test)
            continue
        else:
            test["message"] = f"Task {step}: FAIL"
            results["data"].append(test)
            continue

    # Build the complete Vim shell command
    vim_cmd_parts = ["vim", "-es"]
    for cmd in raw_commands:
        cmd = cmd.strip()
        if not cmd:
            continue
        if cmd.startswith(":"):
            vim_cmd_parts.append(f'-c "{cmd[1:]}"')
        elif needs_normal_prefix(cmd):
            vim_cmd_parts.append(f'-c "normal! {cmd}"')
        else:
            vim_cmd_parts.append(f'-c "{cmd}"')

    vim_cmd_parts.append('-c "wq"')
    vim_cmd_parts.append('story.txt')

    final_cmd = " ".join(vim_cmd_parts)

    print(final_cmd)
    # Run Vim in silent mode on story.txt with script
    try:
        subprocess.run(
            final_cmd,
            shell=True,
            cwd=student_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except subprocess.CalledProcessError:
        test["message"] = f"Task {step}: Error running vim commands"
        results["data"].append(test)
        continue

    # Compare story.txt with expected step output
    if not os.path.exists(expected_step_file):
        test["message"] = f"Expected step{step}.txt not found"
        results["data"].append(test)
        continue

    with open(story_path) as f:
        student_lines = [line.strip() for line in f.readlines()]
    with open(expected_step_file) as f:
        expected_lines = [line.strip() for line in f.readlines()]

    diff_lines = []
    for i, (e_line, s_line) in enumerate(zip(expected_lines, student_lines), 1):
        if e_line != s_line:
            diff_lines.append(f"Line {i}:\n  Expected: {e_line}\n  Found:    {s_line}")

    # Handle extra or missing lines
    if len(expected_lines) > len(student_lines):
        for i in range(len(student_lines)+1, len(expected_lines)+1):
            diff_lines.append(f"Line {i}:\n  Expected: {expected_lines[i-1]}\n  Found:    <missing>")
    elif len(student_lines) > len(expected_lines):
        for i in range(len(expected_lines)+1, len(student_lines)+1):
            diff_lines.append(f"Line {i}:\n  Expected: <missing>\n  Found:    {student_lines[i-1]}")

    if not diff_lines:
        test["status"] = "success"
        test["score"] = 1
        test["message"] = f"Task {step}: PASS"
    else:
        test["message"] = f"Task {step}: FAIL\n" + '\n'.join(diff_lines[:5])

    results["data"].append(test)

# Write results to evaluate.json
with open(output_json, "w") as f:
    json.dump(results, f, indent=4)

# Print the results
with open(output_json) as f:
    print(f.read())
