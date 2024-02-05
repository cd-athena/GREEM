

apt-get update && \
  apt-get install --quiet --yes python3 locales curl wget jq nano git \
  build-essential yasm pkg-config nasm autoconf automake cmake git-core && \
  rm -rf /var/lib/apt/lists/*

# Install Nvidia and CUDA libraries and drivers
apt-get -y install cuda-toolkit-12-3
apt-get install -y nvidia-kernel-open-545
apt-get install -y cuda-drivers-545

apt-get -y --force-yes install autoconf automake cmake libass-dev libfreetype6-dev libgpac-dev \
  libsdl1.2-dev libtheora-dev libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev \
  libxcb-xfixes0-dev pkg-config wget yasm texi2html zlib1g-dev nasm libx264-dev libx265-dev libnuma-dev \
  libvpx-dev libmp3lame-dev libunistring-dev libaom-dev libopus-dev libfreetype6-dev libva-dev libxcb1-dev libc6-dev libc6 libass-dev build-essential libnuma1 libsdl2-dev libvorbis-dev libopus-dev cmake texinfo libvdpau-dev pkg-config libvpx-dev libx265-dev wget libmp3lame-dev libnuma-dev unzip libxcb-shm0-dev zlib1g-dev libtool libx264-dev

git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git && \
    cd nv-codec-headers && make && make install && cd ..

apt-get install ffmpeg -y
# for docker
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/1.13.5/install-guide.html
# apt-get install -y nvidia-container-toolkit
# nvidia-ctk runtime configure --runtime=docker

# install miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# PATH="/root/miniconda3/bin:$PATH"
bash Miniconda3-latest-Linux-x86_64.sh -b