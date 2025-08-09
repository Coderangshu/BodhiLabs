#!/bin/bash
if [ -f "/opt/check.txt" ]; then
    echo "No Need!"
else
    cp -r /home/.evaluationScripts/studentDirectory/* /home/labDirectory/
    chmod -R a+rw /home/labDirectory/forms/style.css
    chmod -R a+rw /home/labDirectory/cursor/style.css
    chmod -R a+rw /home/labDirectory/images/style.css
    echo Done > /opt/check.txt
fi

# Start the bash shell
exec /bin/bash
