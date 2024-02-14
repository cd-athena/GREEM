# GREEM

## Description

We present a monitoring tool that is open-source, easy-to-use, and easy-to-set up for benchmarking video processing. The tool measures various hardware parameters, such as energy consumption and GPU metrics, including core and memory usage, temperature, and fan speed. Additionally, we offer scripts that generate sample analytic plots, which assist researchers in analyzing and understanding their benchmark results.

<!-- Explain the advantages of using this tool -->

- [GREEM](#greem)
  - [Description](#description)
  - [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Quick Setup](#quick-setup)
  - [On System Installation](#on-system-installation)
  - [Docker Installation](#docker-installation)
- [Benchmarks](#benchmarks)
- [Troubleshoot](#troubleshoot)
  - [CUDA Hardware Acceleration not Working Properly](#cuda-hardware-acceleration-not-working-properly)
  - [FFmpeg - cuda encode - OpenEncodeSessionEx failed: out of memory](#ffmpeg---cuda-encode---openencodesessionex-failed-out-of-memory)
  - [Docker - Could not select device driver "nvidia"](#docker---could-not-select-device-driver-nvidia)


## Prerequisites

- Python
- Anaconda or Miniconda
- FFmpeg
- NVIDIA & CUDA

# Installation

## Quick Setup

****
If all prerequisites are met, use the quick setup at the root of the project to get started.

```bash
conda env create -f environment.yml
conda activate greem
pip install -e .
```

## On System Installation

The [Installation README](INSTALL.md) contains the necessary steps to install all dependencies on a Linux system to run `GREEM`.

## Docker Installation

The [Docker Installation](README.Docker.md) file contains instructions to build and run a Docker container for GREEM.

# Benchmarks

Inside the [benchmark](gaia/benchmark/README.md) folder, benchmarks are located to measure the energy impact in various scenarios. Troubleshoot

This section contains information about some issues encountered during the creation and execution of this library.

## CUDA Hardware Acceleration not Working Properly

To fully utilize a CUDA GPU, it is necessary that not only the `-hwaccel cuda` flag is set, but also all other operations need to be specified to use CUDA instead of a CPU, see [StackOverflow](https://stackoverflow.com/questions/44510765/gpu-accelerated-video-processing-with-ffmpeg).

How to fully use CUDA, please refer to the [NVIDIA documentation](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html).

## FFmpeg - cuda encode - OpenEncodeSessionEx failed: out of memory

This issue is likely occurring during the *multi-video* encoding/decoding process with a GPU.
The error states that the used GPU is 'non-qualified' and only supports a fixed amount of sessions (videos encoded at once) [see StackOverflow](https://stackoverflow.com/questions/46393526/ffmpeg-cuda-encode-openencodesessionex-failed-out-of-memory).

The number of videos that can be encoded/decoded at once can be looked up at: [GPU Support Matrix](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new#Encoder) with the *Max \# of concurrent sessions* column corresponding to the GPU.

There exists a [repository](https://github.com/keylase/nvidia-patch) to *fix* this restriction, but we did not test its functionality.

## Docker - Could not select device driver "nvidia"

If the following error is encountered:

`Error response from daemon: could not select device driver "nvidia" with capabilities: [[gpu]]`

the **NVIDIA Container Toolkit** needs to be installed (see [Installation README](INSTALL.md), section Docker).
