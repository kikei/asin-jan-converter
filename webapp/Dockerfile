FROM ubuntu:latest

WORKDIR /usr/src/app
VOLUME ["/usr/src/app"]
VOLUME ["/mnt"]

COPY requirements.txt .

RUN apt-get update -y --fix-missing
RUN apt-get install -y python3 python3-pip

# Python3
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENV LANG C.UTF-8