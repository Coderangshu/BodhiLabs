#!/bin/bash

# Check if exactly one argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <Lab Name>"
    exit 1
fi

lab=$1
fullLab="Lab1"
studentDirectory="$lab/.bodhiFiles/studentDirectory"

# Step 1: Copy the user's lab to .evaluationScripts (excluding node_modules and .solutions)
rsync -a \
    --exclude="node_modules" \
    --exclude=".bodhiFiles/.solutions" \
    "$lab/" ".evaluationScripts/"

# Step 2: Copy only files from Lab1 that are NOT in $lab, but skip .bodhiFiles/studentDirectory if present in both
student_subdir=".bodhiFiles/studentDirectory"
exclude_student_dir=""

if [ -d "$lab/$student_subdir" ] && [ -d "$fullLab/$student_subdir" ]; then
    exclude_student_dir="--exclude=$student_subdir"
fi

rsync -a \
    --exclude="node_modules" \
    --exclude=".bodhiFiles/.solutions" \
    $exclude_student_dir \
    --ignore-existing \
    "$fullLab/" ".evaluationScripts/"

# Step 3: Create instructor archive
tar -czvf instructor.tgz .evaluationScripts

# Step 4: Copy studentDirectory to labDirectory
rsync -a --exclude="node_modules" "$studentDirectory/" "labDirectory/"

# Step 5: Create student archive
tar -czvf student.tgz labDirectory

# Step 6: Clean up
rm -rf .evaluationScripts labDirectory
