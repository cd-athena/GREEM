# Installation

## 1. Anaconda Environment

The Python dependencies can be installed using `Anaconda` with help of the `environment.yml` file that is located at the root folder of this repository.

The `environment.yml` is used to create a Python environment called `gaia-tools`.
To do so, use the command: `conda env create -f environment.yml`.
This will install the Anaconda environment that is used for GAIATools.

Once the environment is installed, activate it with `conda activate gaia-tools`.

## 2. Environment Setup

After successfully installing the Anaconda environment, it is required to locally install GAIATools using the command `pip install -e .` at the root level of this repository. This will install the project as a module that can then be easily important inside the project itself.

## 3. Use Encoding/Decoding Benchmarks

In order to use the encoding/decoding benchmark Python scripts, it is required to follow the installation steps below.

### 3.1 Install FFMPEG for Encoding/Decoding

If you plan to use the encoding/decoding benchmarks of this project, it is required that FFMPEG is installed on the system.

It is possible to test if FFMPEG is properly installed by executing the command: `ffmpeg -version`.

### 3.2 Download and Add Videos to Benchmarks

Within the `benchmark` folder, two Python scripts can be found to download video files.

The `download_full_input_files.py` script can be used to download input videos from Youtube.

The `download_segments.py` script downloads 500 video segments with a length of 4 seconds each from the **Alpen-Adria University** servers.

### 3.3 Install NVIDIA GPU Hardware Acceleration for FFMPEG

*Note: Some encoding/decoding benchmarks require an NVIDIA GPU and CUDA installed at the moment.*

To be able to use CUDA hardware acceleration for FFMPEG, if is necessary to install the required NVIDIA codec headers for FFMPEG.
A guide how to do so can be found at [NVIDIA docs](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html).

## 4. Install CUDA for NVIDIA GPUs (optional)

In order to be able to utilize NVIDIA GPUs for the benchmarks, it has to be ensured that CUDA drivers are installed on the system.

## 5. Installing Prerequisites on AWS Instance

[How to install FFMPEG with NVIDIA GPU Acceleration on Linux](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/)
