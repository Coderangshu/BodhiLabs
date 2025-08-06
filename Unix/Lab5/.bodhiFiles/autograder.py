#!/usr/bin/python3
import json, os, copy, subprocess, time
from datetime import datetime

# Constants
lab_dir = "/home/labDirectory"
jsonPath = "/home/.evaluationScripts/evaluate.json"
expected_txt_path = "/tmp/expected_combined.txt"
answer_path = os.path.join(lab_dir, "answer.txt")
combined_txt = "combined.txt"
expected_files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "combined.txt"]
X_time = "2024-06-15 14:00:00"
Y_time = "2024-06-15 10:00:00"

# Result structure
overall = {"data": []}
template = {
    "testid": 0,
    "status": "failure",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed!"
}

def add_result(testid, passed, message):
    entry = copy.deepcopy(template)
    entry["testid"] = testid
    entry["message"] = message
    entry["status"] = "success" if passed else "failure"
    entry["score"] = 1 if passed else 0
    overall["data"].append(entry)

def safe_read_lines(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
    except PermissionError:
        fd = os.open(path, os.O_RDONLY)
    with os.fdopen(fd, 'r') as f:
        return f.readlines()

# Step 1: Move to lab directory
os.chdir(lab_dir)
testid = 1

# Step 2: Run the student's commands from answer.txt
if os.path.exists(answer_path):
    try:
        subprocess.run(f"bash {answer_path}", shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError as e:
        # Do not continue testing if script failed
        with open(jsonPath, 'w') as f:
            json.dump(overall, f, indent=4)
        exit(1)
else:
    with open(jsonPath, 'w') as f:
        json.dump(overall, f, indent=4)
    exit(1)

# Test 1: Check all required files exist
missing_files = [f for f in expected_files if not os.path.isfile(f)]
add_result(testid, not missing_files, f"Missing files: {', '.join(missing_files)}" if missing_files else "All required files are present")
testid += 1

# Test 2: Check for newline in one of the first 3 files
newline_found = False
for f in ["file1.txt", "file2.txt", "file3.txt"]:
    try:
        lines = safe_read_lines(f)
        if len(lines) > 1:
            newline_found = True
            break
    except:
        pass
add_result(testid, newline_found, "One file has a newline" if newline_found else "No newline found in any file")
testid += 1

# Test 3: No blank lines in combined.txt
try:
    lines = safe_read_lines("combined.txt")
    has_blank = any(line.strip() == '' for line in lines)
    add_result(testid, not has_blank, "No blank lines in combined.txt" if not has_blank else "Blank lines found in combined.txt")
except Exception as e:
    add_result(testid, False, f"Error reading combined.txt: {e}")
testid += 1

# Test 4: Content match
try:
    with open(expected_txt_path, 'w') as out:
        for f in ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]:
            with open(f, 'r') as infile:
                for line in infile:
                    if line.strip():
                        out.write(line)
    expected = safe_read_lines(expected_txt_path)
    actual = safe_read_lines("combined.txt")
    passed = expected == actual
    msg = "combined.txt content matches expected" if passed else "combined.txt content mismatch"
    add_result(testid, passed, msg)
except Exception as e:
    add_result(testid, False, f"Error comparing content: {e}")
testid += 1

# Test 5: Timestamp check
try:
    stat_info = os.stat(combined_txt)
    atime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_atime))
    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_mtime))
    passed = (atime == Y_time and mtime == X_time)
    msg = f"Timestamps correct (Modify={mtime}, Access={atime})" if passed else f"Timestamps incorrect (Modify={mtime}, Access={atime})"
    add_result(testid, passed, msg)
except Exception as e:
    add_result(testid, False, f"Error checking timestamps: {e}")
testid += 1

# Final: Write and print results
with open(jsonPath, 'w') as f:
    json.dump(overall, f, indent=4)

with open(jsonPath, 'r') as f:
    print(f.read())
