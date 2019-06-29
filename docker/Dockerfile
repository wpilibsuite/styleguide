FROM ubuntu:18.04

RUN apt-get update && apt-get install -y tzdata && apt-get install -y \
    fakeroot \
    clang-format-6.0 \
    python3-setuptools \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install wpiformat

WORKDIR /
