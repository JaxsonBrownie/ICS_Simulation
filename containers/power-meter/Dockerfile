FROM ubuntu:20.04

# Update
RUN apt-get update

# Install required packages
RUN apt-get install -y python3 \
    && apt-get install -y python3-pip 

RUN pip3 install pyModbusTCP
RUN pip3 install scipy

# Copy container source code
WORKDIR /src
COPY ./src/ .

#RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y tzdata
#&& apt-get install -y iputils-ping \
#&& apt-get install -y net-tools \
#&& apt-get install -y git \
#&& apt-get install -y nano \
#&& apt-get install -y telnet \
#&& apt-get install -y memcached \
#&& apt-get install -y python3-memcache \
#&& apt-get install -y ettercap-common \
#&& apt-get install -y nmap