# GAIA-Tools

A repository that contains different tools related to energy monitoring extracted from GAIA projects.

<!-- Explain the advantages of using this tool -->

- [GAIA-Tools](#gaia-tools)
  - [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Quick Setup](#quick-setup)
- [Benchmarks](#benchmarks)
- [Troubleshoot](#troubleshoot)
  - [CUDA Hardware Acceleration not Working Properly](#cuda-hardware-acceleration-not-working-properly)
  - [ffmpeg - cuda encode - OpenEncodeSessionEx failed: out of memory](#ffmpeg---cuda-encode---openencodesessionex-failed-out-of-memory)
  - [Docker - Could not select device driver "nvidia"](#docker---could-not-select-device-driver-nvidia)

## Prerequisites

- Python
- Anaconda or Miniconda
- FFMPEG

# Installation

The [Installation README](INSTALL.md) contains the necessary steps to install all dependencies in order to run `GAIATools`.

## Quick Setup

```bash
conda env create -f environment.yml
conda activate gaia-tools
pip install -e .
```

# Benchmarks

Inside the [benchmark](gaia/benchmark/README.md) folder, benchmarks are located to measure the energy impact in various scenarios.

# Troubleshoot

This section contains information about some issues encountered during creation and execution of this library.

## CUDA Hardware Acceleration not Working Properly

In order to fully utilise a CUDA GPU, it is necessary that not only the `-hwaccel cuda` flag is set, but also all other operations need to be specified to use CUDA instead of a CPU, see [StackOverflow](https://stackoverflow.com/questions/44510765/gpu-accelerated-video-processing-with-ffmpeg).

How to fully use CUDA, please refer to the [NVIDIA documentation](https://docs.nvidia.com/video-technologies/video-codec-sdk/12.0/ffmpeg-with-nvidia-gpu/index.html).

## ffmpeg - cuda encode - OpenEncodeSessionEx failed: out of memory

This issue is likely occuring during the *multi-video* encoding/decoding process with a GPU.
The error states that the used GPU is 'non-qualified' and only supports a fixed amount of sessions (videos encoded at once) [see StackOverflow](https://stackoverflow.com/questions/46393526/ffmpeg-cuda-encode-openencodesessionex-failed-out-of-memory).

The number of videos that can be encoded/decoded at once can be looked up at: [GPU Support Matrix](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new#Encoder) with the *Max \# of concurrent sessions* column corresponding to the GPU.

There exists a [repository](https://github.com/keylase/nvidia-patch) to *fix* this restriction, but we did not test its functionality.


## Docker - Could not select device driver "nvidia"

If the following error is encountered:

`Error response from daemon: could not select device driver "nvidia" with capabilities: [[gpu]]`

the **NVIDIA Container Toolkit** needs to be installed (see [Installation README](INSTALL.md), section Docker).
