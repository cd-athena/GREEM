# Installation

- [Installation](#installation)
  - [On System Installation](#on-system-installation)
    - [1. Anaconda Environment](#1-anaconda-environment)
    - [2. Environment Setup](#2-environment-setup)
    - [3. Use Encoding/Decoding Benchmarks](#3-use-encodingdecoding-benchmarks)
      - [3.1 Install FFMPEG for Encoding/Decoding](#31-install-ffmpeg-for-encodingdecoding)
      - [3.2 Download and Add Videos to Benchmarks](#32-download-and-add-videos-to-benchmarks)
      - [3.3 Install NVIDIA GPU Hardware Acceleration for FFMPEG](#33-install-nvidia-gpu-hardware-acceleration-for-ffmpeg)
    - [4. Install CUDA for NVIDIA GPUs (optional)](#4-install-cuda-for-nvidia-gpus-optional)
    - [5. Installing Prerequisites on AWS Instance](#5-installing-prerequisites-on-aws-instance)
  - [Docker](#docker)
    - [Prerequisites](#prerequisites)
    - [Run the Docker Container](#run-the-docker-container)

## On System Installation

This section has instructions to install the necessary tools and libraries to run GREEM directly on the system.

### 1. Anaconda Environment

The Python dependencies can be installed using `Anaconda` with help of the `environment.yml` file that is located at the root folder of this repository.

The `environment.yml` is used to create a Python environment called `gaia-tools`.
To do so, use the command: `conda env create -f environment.yml`.
This will install the Anaconda environment that is used for GAIATools.

Once the environment is installed, activate it with `conda activate gaia-tools`.

### 2. Environment Setup

After successfully installing the Anaconda environment, it is required to locally install GAIATools using the command `pip install -e .` at the root level of this repository. This will install the project as a module that can then be easily important inside the project itself.

### 3. Use Encoding/Decoding Benchmarks

In order to use the encoding/decoding benchmark Python scripts, it is required to follow the installation steps below.

#### 3.1 Install FFMPEG for Encoding/Decoding

If you plan to use the encoding/decoding benchmarks of this project, it is required that FFMPEG is installed on the system.

It is possible to test if FFMPEG is properly installed by executing the command: `ffmpeg -version`.

#### 3.2 Download and Add Videos to Benchmarks

Within the `benchmark` folder, two Python scripts can be found to download video files.

The `download_full_input_files.py` script can be used to download input videos from Youtube.

The `download_segments.py` script downloads 500 video segments with a length of 4 seconds each from the **Alpen-Adria University** servers.

#### 3.3 Install NVIDIA GPU Hardware Acceleration for FFMPEG

*Note: Some encoding/decoding benchmarks require an NVIDIA GPU and CUDA installed at the moment.*

To be able to use CUDA hardware acceleration for FFMPEG, if is necessary to install the required NVIDIA codec headers for FFMPEG.
A guide how to do so can be found at [NVIDIA docs](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html).

### 4. Install CUDA for NVIDIA GPUs (optional)

In order to be able to utilize NVIDIA GPUs for the benchmarks, it has to be ensured that CUDA drivers are installed on the system.

### 5. Installing Prerequisites on AWS Instance

[How to install FFMPEG with NVIDIA GPU Acceleration on Linux](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/)

## Docker

This section has the necessary instructions to create a Docker container with all necessary dependencies to execute benchmarks within GREEM.

### Prerequisites

- Docker
- Docker Compose
- NVIDIA Container Toolkit (or Runtime)

In order to use the Docker container with NVIDIA GPU support, the `NVIDIA Container Toolkit/Runtime` has to be installed.
This toolkit installs drivers that enable the access of NVIDIA GPUs within Docker containers.
*Note: When running a Docker container, it is required to set the container runtime to nvidia*.

[Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/1.14.4/install-guide.html) is the official guide by NVIDIA to install the required packages.

If you prefer to install [NVIDIA Container Runtime](https://docs.docker.com/config/containers/resource_constraints/#gpu) you need to provide the flag `--gpus` instead of `--runtime=nvidia` to the `docker run <cmd>`.

To test if NVIDIA Container Tookkit is properly installed, use this sample container:

 ```bash
# NVIDIA Container Toolkit  
sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi

#  NVIDIA Container Runtime
sudo docker run --rm --gpus all ubuntu nvidia-smi
 ```

This should output something similar to:

```bash
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.86.10    Driver Version: 535.86.10    CUDA Version: 12.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla T4            On   | 00000000:00:1E.0 Off |                    0 |
| N/A   34C    P8     9W /  70W |      0MiB / 15109MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```

### Run the Docker Container

Finally, to run the Docker container, execute the following command:

```bash
docker run --rm --runtime=nvidia -it gaiatools-greem bash
```

This will start the container with the entry point of it being the root of GREEM.
