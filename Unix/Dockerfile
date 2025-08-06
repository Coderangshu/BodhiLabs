# Step 1: Use  Ubuntu image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Step 2: Add necessary binaries
RUN apt update -y && apt install -y vim python3 sudo file && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Step 3: Set the working directory inside the container
WORKDIR /home/labDirectory

# Step 4: Create home directory and all the folders inside it
RUN mkdir /home/.evaluationScripts

# Global Settings
RUN echo "cd /home/labDirectory" >> /root/.bashrc && \
    echo "alias ls='ls --color=always'" >> /root/.bashrc && \
    echo "rm -f \$(find /home -type f -name \"._*\")" >> /root/.bashrc

# Step 5: Setup the directories
CMD [ "/bin/bash", "-c", "bash /home/.evaluationScripts/.bodhiFiles/init.sh; while :; do sleep 10; done" ]
