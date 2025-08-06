# Instructions  
  
## General:  
1. #### To create Docker image using the Dockerfile - ```docker buildx build -t unix-lab:latest .```  
2. #### To run each Lab locally go inside that lab's folder and run - ``docker run -it --rm -v .:/home/.evaluationScripts unix-lab``  

## Upload:
1. #### To generate the upload .tgz binaries of a lab use ``./prepup.sh <lab_name>``
3. #### In Add Script section add *Name - Evaluate* and *Script - /home/.evaluationScripts/.bodhiFiles/evaluate.sh*  
