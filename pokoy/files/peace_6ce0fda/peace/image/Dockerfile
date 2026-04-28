FROM ubuntu:24.04 AS build
RUN apt-get -y update && apt-get -y install iverilog python3-pip
RUN pip install --break-system-packages 'cocotb == 2.0.1'
COPY src /src/
WORKDIR /src
CMD ["python3", "./peace.py"]
