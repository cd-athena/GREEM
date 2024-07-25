# Installation - On System

- [Installation - On System](#installation---on-system)
  - [Prerequisites](#prerequisites)
    - [Python 3](#python-3)
    - [Anaconda/Miniconda](#anacondaminiconda)
    - [Install Miniconda from CLI](#install-miniconda-from-cli)
  - [Setting up the Python Environment](#setting-up-the-python-environment)
    - [Create Anaconda Environment](#create-anaconda-environment)
    - [NVIDIA \& CUDA Drivers](#nvidia--cuda-drivers)
    - [FFmpeg](#ffmpeg)
      - [Install FFmpeg](#install-ffmpeg)
      - [Install FFmpeg Video Codec Libraries](#install-ffmpeg-video-codec-libraries)
      - [FFmpeg with NVIDIA GPU Support](#ffmpeg-with-nvidia-gpu-support)
  - [Video Processing Testbeds](#video-processing-testbeds)
    - [Download and Add Videos to Testbeds](#download-and-add-videos-to-testbeds)
  - [(Optional) Installing Prerequisites on AWS Instance](#optional-installing-prerequisites-on-aws-instance)

This section has instructions to install the necessary tools and libraries to run GREEM directly on the system.

## Prerequisites

This section contains the required libraries for GREEM.

### Python 3

Python 3 is required to be installed on the system. To test if Python 3 is installed on the system, enter the command:

```bash
# check if Python is installed
python3 --version
```

This command should prompt the Python 3 version installed on the system.

If Python 3 is not installed, use the following command:

```bash
# install Python 3 on the system
sudo apt-get update && sudo apt-get install python3 -y
```

### Anaconda/Miniconda

To install the Python virtual environment with all required libraries, GREEM uses Anaconda/Miniconda environments.

### Install Miniconda from CLI

If Anaconda/Miniconda is not installed on the system, the following commands provide a quick installation guide to install Miniconda.

If you use a Bash shell environment:

```bash
# Bash Shell
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
```

If you use a Zsh shell environment:

```bash
# Zsh Shell
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
zsh ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init zsh
```

Miniconda is a minimal installer for `conda` that only includes the `conda` binaries, Python and the packages they depend on.

## Setting up the Python Environment

The Python dependencies can be installed using `Anaconda` with help of the `environment.yml` file that is located at the root folder of this repository.

### Create Anaconda Environment

The `environment.yml` at the root level is used to create a Python environment called `greem`.
To do so, use the command:

```bash
# create anaconda environment
conda env create -f environment.yml
```

This will install the Anaconda environment that is used for GREEM.

Once the environment is installed, activate it with

```bash
# activate anaconda environment
conda activate greem
```

After successfully installing the Anaconda environment, it is required to locally install GREEM using the command

```bash
# setup Python GREEM paths
pip install -e .
```

at the root level of this repository. This will install the projects as a module and setup the paths that can then be easily important inside the project itself.

### NVIDIA & CUDA Drivers

In order to be able to utilize NVIDIA GPUs for the benchmarks, ensure that NVIDIA and CUDA drivers are installed on the system.

### FFmpeg

To use the video processing benchmarks in the `encoding` and `decoding` folders, codec libraries need to be installed first.

#### Install FFmpeg

Use the following command to install FFmpeg if it is not already installed.

```bash
# Install FFmpeg
sudo apt-get install ffmpeg -y
```

To test if FFMPEG is properly installed by executing the command:

```bash
ffmpeg -version
```

This should prompt you with the installed version number.

Additionally, the installed codecs can be checked using `ffmpeg` in the CLI.

#### Install FFmpeg Video Codec Libraries

A command including many codec libraries is shown below.

```bash
# update aptitude
sudo apt-get update -y

# install FFmpeg libraries
sudo apt-get install -yq  libaom-dev libass-dev libc6 libc6-dev libfreetype6-dev \ 
                          libgpac-dev libmp3lame-dev libnuma-dev libnuma1 libopus-dev \
                          libsdl1.2-dev libsdl2-dev libtheora-dev libunistring-dev \
                          libva-dev libvdpau-dev libvorbis-dev libvpx-dev \
                          libx264-dev libx265-dev libxcb-shm0-dev libxcb-xfixes0-dev \
                          libxcb1-dev zlib1g-dev
```

#### FFmpeg with NVIDIA GPU Support

The guide [How to install FFmpeg with NVIDIA GPU support](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/) lists the necessary steps to install FFmpeg with NVIDIA GPU support.

---

An alternative guide how to do so can be found at [NVIDIA docs](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html).

This step is required if you plan to process videos with GPU support.


## Video Processing Testbeds

In order to use the encoding/decoding benchmark Python scripts, it is required to follow the installation steps below.

### Download and Add Videos to Testbeds

Within the `testbeds` folder, two Python scripts can be found to download video files.

The `download_full_input_files.py` script can be used to download input videos from Youtube.

---

The `download_segments.py` script downloads 500 video segments with a length of 4 seconds each from the **Alpen-Adria University** servers.

## (Optional) Installing Prerequisites on AWS Instance

[How to install FFMPEG with NVIDIA GPU Acceleration on Linux](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/)
