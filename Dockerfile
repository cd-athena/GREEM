# syntax=docker/dockerfile:1

ARG UBUNTU_VER=20.04
ARG CONDA_VER=latest
ARG OS_TYPE=x86_64
ARG PYTHON_VERSION=3.10.13

FROM nvidia/cuda:11.6.2-base-ubuntu"${UBUNTU_VER}"
# ARG basetag="450-signed-ubuntu22.04"  # Ubuntu only
# FROM nvcr.io/nvidia/driver:"${basetag}"

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

RUN apt-get update && apt-get install -yq curl wget jq nano git build-essential yasm pkg-config nasm autoconf automake cmake git-core


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

RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git && \
    cd nv-codec-headers && make && make install && cd ..

ARG CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}

RUN export PATH=/usr/local/cuda/bin:${PATH}
RUN apt-get -y --force-yes install autoconf automake cmake libass-dev libfreetype6-dev libgpac-dev \
  libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev \
  libxcb-xfixes0-dev pkg-config wget yasm texi2html zlib1g-dev nasm libx264-dev libx265-dev libnuma-dev \
  libvpx-dev libmp3lame-dev libunistring-dev libaom-dev libopus-dev

RUN apt-get install -y libfreetype6-dev libva-dev libxcb1-dev libc6-dev libc6 libass-dev build-essential libnuma1 libsdl2-dev libvorbis-dev libopus-dev cmake texinfo libvdpau-dev pkg-config libvpx-dev libx265-dev wget libmp3lame-dev libnuma-dev unzip libxcb-shm0-dev zlib1g-dev libtool libx264-dev
# Compile and install ffmpeg from source
# https://stackoverflow.com/a/46005194/13334047
# RUN git clone https://github.com/FFmpeg/FFmpeg /root/ffmpeg && \
#     cd /root/ffmpeg && \
#     ./configure \
#     --libdir=/usr/lib/x86_64-linux-gnu \
#     --incdir=/usr/include/x86_64-linux-gnu \
#     --disable-filter=resample \
#     --extra-libs="-lpthread -lm" \
#     --bindir="/bin" \
#     # --bindir="$HOME/bin" \
#     # --enable-cuda-nvcc \
#     # --enable-cuda \
#     # --enable-cuvid \
#     # --enable-libnpp \
#     # --extra-cflags="-I/${CUDA_HOME}/include/" \
#     # --extra-ldflags=-L/${CUDA_HOME}/lib64/ \
#     --enable-gpl \
#     --enable-libass \
#     --enable-vaapi \
#     --enable-libfreetype \
#     --enable-libmp3lame \
#     --enable-libopus \
#     --enable-libtheora \
#     # --enable-libvorbis \
#     # --enable-libsvtav1 \
#     # --enable-libvorbis \
#     # --enable-libvpx \
#     --enable-libx264 \
#     --enable-libx265 \
#     --enable-nonfree \
#     --enable-nvenc && \
#     PATH="$HOME/bin:$PATH" make -j$(nproc) && \
#     make -j$(nproc) install
RUN apt-get install ffmpeg -y

# WORKDIR /app/gaia

# Finish setup of GREEM project
# RUN conda init bash \
#     && . ~/.bashrc \ && conda activate gaia-tools && pip install -e .

# Run the application.
# CMD [ "pip install -e ." ]
# ENTRYPOINT [ "python3", "-m", "nvitop" ]

# RUN python3 -m nvitop

RUN echo "conda activate gaia-tools" >> ~/.bashrc
RUN echo "pip install -e ." >> ~/.bashrc



