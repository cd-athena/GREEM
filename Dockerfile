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
  apt-get install --quiet --yes python3 locales && \
  rm -rf /var/lib/apt/lists/*

# Setup locale
ENV LC_ALL=C.UTF-8
RUN update-locale LC_ALL="C.UTF-8"

# install all dependencies
RUN apt-get update && apt-get install -yq pkg-config libc6 wget curl automake nano cmake \
      libnuma-dev libass-dev unzip libxcb-xfixes0-dev libva-dev git-core libc6-dev libnuma1 libvorbis-dev libx265-dev \
      libsdl2-dev libtool libfreetype6-dev libx264-dev zlib1g-dev libopus-dev libtheora-dev libxcb1-dev \
      texinfo nasm libvdpau-dev libaom-dev git libgpac-dev yasm jq build-essential autoconf libunistring-dev \
      libxcb-shm0-dev libvpx-dev libmp3lame-dev texi2html libsdl1.2-dev

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Update and upgrade aptitude
RUN apt-get update -y && apt-get upgrade -y

# install miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
ENV PATH="/root/miniconda3/bin:$PATH"
RUN mkdir /root/.conda && bash Miniconda3-latest-Linux-x86_64.sh -b

WORKDIR /app

# Copy the source code into the container.
COPY . .

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/conda to speed up subsequent builds.
# Leverage a bind mount to environment.yml to avoid having to copy them into
# into this layer.
# https://stackoverflow.com/a/62674910/13334047
# https://stackoverflow.com/a/69878344/13334047
RUN --mount=type=cache,target=/root/.cache/conda \
    --mount=type=bind,source=environment.yml,target=environment.yml \
    conda init bash \
    && . ~/.bashrc \
    && conda env create -f environment.yml \
    && conda activate gaia-tools && pip install -e .


# Start with FFmpeg Installation

# adding nvidia headers for FFmpeg
# https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html
RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git && \
    cd nv-codec-headers && make && make install && cd ..

ARG CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
RUN export PATH=/usr/local/cuda/bin:${PATH}
RUN apt-get install ffmpeg -y

# Add strings to bashrc to ensure they get executed when starting the image
RUN echo "conda activate gaia-tools" >> ~/.bashrc
RUN echo "pip install -e ." >> ~/.bashrc



