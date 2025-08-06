#!/usr/bin/python3
import os, json, copy, subprocess, shlex

os.system('clear')

###############################################################################
# CONSTANTS ­– adjust only if your folder names change
###############################################################################
LAB_ROOT      = "/home/labDirectory"                   # where the student starts
SCRIPT_ROOT   = "/home/.evaluationScripts"             # do not touch
ANS_FILE      = SCRIPT_ROOT + "/.bodhiFiles/answer.txt"
RESULT_JSON   = SCRIPT_ROOT + "/evaluate.json"

###############################################################################
# TEST DEFINITION
###############################################################################
steps = [
    {
        "minimal" : "mkdir folder",
        "check"   : lambda: os.path.isdir(f"{LAB_ROOT}/folder"),
        "msg_ok"  : "Created folder",
    },
    {
        "minimal" : "mkdir folder_copy",
        "check"   : lambda: os.path.isdir(f"{LAB_ROOT}/folder_copy"),
        "msg_ok"  : "Created folder_copy",
    },
    {
        "minimal" : "cp random.txt folder",
        "check"   : lambda: os.path.isfile(f"{LAB_ROOT}/folder/random.txt"),
        "msg_ok"  : "Copied random.txt to folder",
    },
    {
        "minimal" : "mv folder/random.txt folder_copy",
        "check"   : lambda: (os.path.isfile(f"{LAB_ROOT}/folder_copy/random.txt")
                             and not os.path.exists(f"{LAB_ROOT}/folder/random.txt")),
        "msg_ok"  : "Moved random.txt to folder_copy",
    },
    {
        "minimal" : "rmdir folder",
        "check"   : lambda: not os.path.exists(f"{LAB_ROOT}/folder"),
        "msg_ok"  : "Removed empty folder",
    },
    {
        "minimal" : "rm folder_copy/random.txt",
        "check"   : lambda: not os.path.exists(f"{LAB_ROOT}/folder_copy/random.txt"),
        "msg_ok"  : "Removed random.txt from folder_copy",
    },
]

###############################################################################
# HELPER — normalise whitespace so “mkdir   folder” ≡ “mkdir folder”
###############################################################################
def norm(cmd:str) -> str:
    return " ".join(shlex.split(cmd))

###############################################################################
# BUILD RESULT SKELETON
###############################################################################
overall = {"data": []}
TEMPLATE = {
    "testid": 0,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

###############################################################################
# READ STUDENT ANSWERS
###############################################################################
try:
    with open(ANS_FILE) as f:
        student_cmds = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    student_cmds = []

###############################################################################
# GRADE STEP-BY-STEP
###############################################################################
for idx, step in enumerate(steps):
    entry = copy.deepcopy(TEMPLATE)
    entry["testid"] = idx + 1

    student_cmd = student_cmds[idx] if idx < len(student_cmds) else ""
    entry["message"] = f"{student_cmd or '(missing)'}: FAIL"

    # execute student's command (if any)
    if student_cmd:
        try:
            subprocess.check_output(
                f"bash -c 'cd {shlex.quote(LAB_ROOT)} && {student_cmd}'",
                shell=True, stderr=subprocess.STDOUT, text=True
            )
        except subprocess.CalledProcessError as e:
            entry["message"] = f"{student_cmd}: FAIL – command error"
            overall["data"].append(entry)
            continue

    # run correctness check
    if step["check"]():
        # correct directory state ─ now decide minimal vs partial
        if norm(student_cmd) == norm(step["minimal"]):
            entry.update({"status": "success", "score": 1,
                          "message": f"{step['msg_ok']}: PASS"})
        else:
            entry.update({"status": "partial", "score": 0.5,
                          "message": f"{step['msg_ok']}: PASS but not minimal"})
    else:
        entry["message"] = f"{student_cmd or '(missing)'}: FAIL – wrong result"

    overall["data"].append(entry)

###############################################################################
# WRITE + DISPLAY RESULTS
###############################################################################
with open(RESULT_JSON, "w", encoding="utf-8") as f:
    json.dump(overall, f, indent=4)

with open(RESULT_JSON, "r", encoding="utf-8") as f:
    print(f.read())

