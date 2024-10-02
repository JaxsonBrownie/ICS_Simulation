FROM ubuntu:20.04

# Update
RUN apt-get update

# Install required packages for python
RUN apt-get install -y python3 \
    && apt-get install -y python3-pip 

RUN pip3 install pyModbusTCP
RUN pip3 install pymodbus
RUN pip3 install pyserial
RUN pip3 install scipy
RUN pip3 install numpy
RUN pip3 install flask
RUN pip3 install flask-cors

# Set TERM environment variable
ENV TERM xterm-256color

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