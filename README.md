# GAIA-Tools

A repository that contains different tools related to energy monitoring extracted from GAIA projects.

- [GAIA-Tools](#gaia-tools)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [1. Anaconda Environment](#1-anaconda-environment)
    - [2. Environment Setup](#2-environment-setup)
    - [3. Use Encoding/Decoding Benchmarks](#3-use-encodingdecoding-benchmarks)
      - [3.1 Install FFMPEG for Encoding/Decoding](#31-install-ffmpeg-for-encodingdecoding)
      - [3.2 Download and Add Videos to Benchmarks](#32-download-and-add-videos-to-benchmarks)
      - [3.3 Install NVIDIA GPU Hardware Acceleration for FFMPEG](#33-install-nvidia-gpu-hardware-acceleration-for-ffmpeg)
    - [4. Install CUDA for NVIDIA GPUs (optional)](#4-install-cuda-for-nvidia-gpus-optional)
  - [Installing Prerequisites on AWS Instance](#installing-prerequisites-on-aws-instance)
  - [Benchmarks](#benchmarks)
    - [Encoding](#encoding)
    - [Decoding](#decoding)
  - [Troubleshoot](#troubleshoot)
    - [CUDA Hardware Acceleration not Working Properly](#cuda-hardware-acceleration-not-working-properly)
    - [ffmpeg - cuda encode - OpenEncodeSessionEx failed: out of memory](#ffmpeg---cuda-encode---openencodesessionex-failed-out-of-memory)

## Prerequisites

- Python
- Anaconda or Miniconda
- FFMPEG

## Installation

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

## Installing Prerequisites on AWS Instance

[How to install FFMPEG with NVIDIA GPU Acceleration on Linux](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/)

## Benchmarks

Inside the `benchmarks` folder, benchmarks are located to measure the energy impact in various scenarios.

### Encoding

### Decoding

## Troubleshoot

This section contains information about some issues encountered during creation and execution of this library.

### CUDA Hardware Acceleration not Working Properly

In order to fully utilise a CUDA GPU, it is necessary that not only the `-hwaccel cuda` flag is set, but also all other operations need to be specified to use CUDA instead of a CPU, see [StackOverflow](https://stackoverflow.com/questions/44510765/gpu-accelerated-video-processing-with-ffmpeg).

How to fully use CUDA, please refer to the [NVIDIA documentation](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html).

### ffmpeg - cuda encode - OpenEncodeSessionEx failed: out of memory

This issue is likely occuring during the *multi-video* encoding/decoding process with a GPU.
The error states that the used GPU is 'non-qualified' and only supports a fixed amount of sessions (videos encoded at once) [see StackOverflow](https://stackoverflow.com/questions/46393526/ffmpeg-cuda-encode-openencodesessionex-failed-out-of-memory).

The number of videos that can be encoded/decoded at once can be looked up at: [GPU Support Matrix](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new#Encoder) with the *Max \# of concurrent sessions* column corresponding to the GPU.

There exists a [repository](https://github.com/keylase/nvidia-patch) to *fix* this restriction, but we did not test its functionality.
