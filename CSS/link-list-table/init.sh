#!/bin/bash
if [ -f "/opt/check.txt" ]; then
    echo "No Need!"
else
    cp -r /home/.evaluationScripts/studentDirectory/* /home/labDirectory/
    chmod -R a+rw /home/labDirectory/links/style.css
    chmod -R a+rw /home/labDirectory/lists/style.css
    chmod -R a+rw /home/labDirectory/tables/style.css
    echo Done > /opt/check.txt
fi

# Start the bash shell
exec /bin/bash
