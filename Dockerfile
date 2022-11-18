#FROM python:3.8
#
#WORKDIR ./
#
#COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt
#
#COPY . .




#FROM python:3.8-slim
#
## Install OS-level dependencies
#RUN apt-get update \
# && DEBIAN_FRONTEND=noninteractive \
#    apt-get install --assume-yes --no-install-recommends \
#      curl \
#      unzip
#
## Download and unpack the Amass zip file, saving only the binary
#RUN cd /usr/local \
# && curl -LO https://github.com/OWASP/Amass/releases/download/v3.20.0/amass_linux_amd64.zip \
# && unzip amass_linux_amd64.zip \
# && mv amass_linux_amd64/amass bin \
# && rm -rf amass_linux_amd64 amass_linux_amd64.zip
#
## Install your application the same way you have it already
#WORKDIR ./
#COPY requirements.txt ./
#RUN pip3 install --no-cache-dir -r requirements.txt
#
#COPY . .


FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y upgrade && \
    apt-get -y install python3.8 && \
    apt update && apt install python3-pip -y

# Method1 - installing LibreOffice and java
RUN apt-get --no-install-recommends install libreoffice -y
RUN apt-get install -y libreoffice-java-common
RUN apt-get install -y libenchant1c2a

# Method2 - additionally installing unoconv
RUN apt-get install unoconv

ARG CACHEBUST=1

ADD . .

# copying input doc/docx files to the docker's linux
COPY . .

RUN pip install -r requirements.txt