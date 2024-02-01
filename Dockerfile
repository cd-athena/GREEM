# syntax=docker/dockerfile:1

ARG UBUNTU_VER=20.04
ARG CONDA_VER=latest
ARG OS_TYPE=x86_64
ARG PYTHON_VERSION=3.10.13

FROM nvidia/cuda:11.6.2-base-ubuntu"${UBUNTU_VER}"

ENV NVIDIA_DISABLE_REQUIRE=true
ENV DEBIAN_FRONTEND=noninteractive

# Update APT sources
RUN . /etc/os-release && [ "${NAME}" = "Ubuntu" ] && \
  echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu ${UBUNTU_CODENAME} main universe" > /etc/apt/sources.list && \
  echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu ${UBUNTU_CODENAME}-updates main universe" >> /etc/apt/sources.list && \
  echo "deb [arch=amd64] http://archive.ubuntu.com/ubuntu ${UBUNTU_CODENAME}-security main universe" >> /etc/apt/sources.list

# Install Python 3
RUN apt-get update && \
  apt-get install --quiet --yes --no-install-recommends python3-dev locales && \
  rm -rf /var/lib/apt/lists/*

# Setup locale
ENV LC_ALL=C.UTF-8
RUN update-locale LC_ALL="C.UTF-8"

RUN apt-get update && apt-get install -yq curl wget jq

RUN apt-get update \
    && apt-get install -y wget \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Update and upgrade aptitude
RUN apt-get update -y && apt-get upgrade -y

# Install Nvidia and CUDA libraries and drivers
RUN apt-get -y install cuda-toolkit-12-3
RUN apt-get install -y nvidia-kernel-open-545
RUN apt-get install -y cuda-drivers-545


# install miniconda
ENV PATH="/root/miniconda3/bin:$PATH"
RUN mkdir /root/.conda && bash Miniconda3-latest-Linux-x86_64.sh -b

WORKDIR /app

# Copy the source code into the container.
COPY . .

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/conda to speed up subsequent builds.
# Leverage a bind mount to environment.yml to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/conda \
    --mount=type=bind,source=environment.yml,target=environment.yml \
    conda init bash \
    && . ~/.bashrc \
    && conda env create -f environment.yml \
    && conda activate gaia-tools

# Finish setup of GREEM project
RUN pip install -e .

# Run the application.
# CMD [ "pip install -e ." ]
# ENTRYPOINT [ "python3", "-m", "nvitop" ]

# RUN python3 -m nvitop



