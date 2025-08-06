#!/bin/bash
if [ -f "/opt/check.txt" ]; then
    echo "No Need!"
else
    cp -r /home/.evaluationScripts/.bodhiFiles/studentDirectory/* /home/labDirectory/
    chmod ugo+r+w /home/labDirectory/*
    touch /home/labDirectory/answer.txt
    echo Done > /opt/check.txt
fi

# Start the bash shell
exec /bin/bash
