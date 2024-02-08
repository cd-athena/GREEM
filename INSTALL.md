# Installation - On System

- [Installation - On System](#installation---on-system)
  - [0. Prerequisites](#0-prerequisites)
    - [Python 3](#python-3)
    - [Anaconda/Miniconda](#anacondaminiconda)
    - [NVIDIA \& CUDA Drivers](#nvidia--cuda-drivers)
      - [FFmpeg with NVIDIA GPU Support](#ffmpeg-with-nvidia-gpu-support)
  - [1. Setting up the Python Environment](#1-setting-up-the-python-environment)
    - [Create Anaconda Environment](#create-anaconda-environment)
    - [Setup Project Paths](#setup-project-paths)
  - [2. Install FFmpeg](#2-install-ffmpeg)
    - [3.1 Install FFMPEG for Encoding/Decoding](#31-install-ffmpeg-for-encodingdecoding)
    - [3.3 Install NVIDIA GPU Hardware Acceleration for FFMPEG](#33-install-nvidia-gpu-hardware-acceleration-for-ffmpeg)
  - [3. Video Processing Benchmarks](#3-video-processing-benchmarks)
    - [3.2 Download and Add Videos to Benchmarks](#32-download-and-add-videos-to-benchmarks)
  - [5. Installing Prerequisites on AWS Instance](#5-installing-prerequisites-on-aws-instance)

This section has instructions to install the necessary tools and libraries to run GREEM directly on the system.

## 0. Prerequisites

### Python 3

Python 3 is required to be installed on the system. To test if Python 3 is installed on the system, enter the command:

```bash
python3 --version
```

This command should prompt the Python 3 version installed on the system.

If Python 3 is not installed, use the following command:

```bash
sudo apt-get update && sudo apt-get install python3 -y
```

### Anaconda/Miniconda

To install the Python virtual environment

### NVIDIA & CUDA Drivers

In order to be able to utilize NVIDIA GPUs for the benchmarks, it has to be ensured that NVIDIA and CUDA drivers are installed on the system.

#### FFmpeg with NVIDIA GPU Support

The guide [How to install FFmpeg with NVIDIA GPU support](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/) lists the necessary steps to install FFmpeg with NVIDIA GPU support.

This step is required if you plan to process videos with GPU support.

---
---

## 1. Setting up the Python Environment

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

### Setup Project Paths

After successfully installing the Anaconda environment, it is required to locally install GREEM using the command

```bash
# setup Python GREEM paths
pip install -e .
```

at the root level of this repository. This will install the projects as a module and setup the paths that can then be easily important inside the project itself.

## 2. Install FFmpeg

### 3.1 Install FFMPEG for Encoding/Decoding

If you plan to use the encoding/decoding benchmarks of this project, it is required that FFMPEG is installed on the system.

It is possible to test if FFMPEG is properly installed by executing the command: `ffmpeg -version`.

### 3.3 Install NVIDIA GPU Hardware Acceleration for FFMPEG

*Note: Some encoding/decoding benchmarks require an NVIDIA GPU and CUDA installed at the moment.*

To be able to use CUDA hardware acceleration for FFMPEG, if is necessary to install the required NVIDIA codec headers for FFMPEG.
A guide how to do so can be found at [NVIDIA docs](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html).

## 3. Video Processing Benchmarks

In order to use the encoding/decoding benchmark Python scripts, it is required to follow the installation steps below.

### 3.2 Download and Add Videos to Benchmarks

Within the `benchmark` folder, two Python scripts can be found to download video files.

The `download_full_input_files.py` script can be used to download input videos from Youtube.

The `download_segments.py` script downloads 500 video segments with a length of 4 seconds each from the **Alpen-Adria University** servers.



## 5. Installing Prerequisites on AWS Instance

[How to install FFMPEG with NVIDIA GPU Acceleration on Linux](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/)


