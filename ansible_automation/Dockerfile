FROM python:3.10-slim

RUN apt-get update -y
RUN apt install expect -y
RUN apt install iproute2 -y
RUN apt install iputils-ping -y
RUN apt install sshpass -y
RUN apt install openssh-client -y
RUN pip3 install --upgrade pip
RUN pip3 install ansible==2.10
RUN pip3 install urllib3
RUN pip3 install requests
RUN pip3 install pexpect
RUN pip3 install cryptography

# Copy the playbooks
COPY ./ansible/playbooks /playbooks

# Copy the inventory
COPY ./ansible/inventory /etc/ansible/hosts

# Copy the roles
COPY ./ansible/roles /etc/ansible/roles

WORKDIR /

# Copy utils
COPY ./utils/ansible.py /ansible.py

# Files for modifying the API etc
COPY ./setup_eto.py /deploy/setup_eto.py
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

CMD [ "/bin/bash" ]
