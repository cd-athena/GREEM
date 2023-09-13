# GAIA-Tools

A repository that contains different tools related to energy monitoring extracted from GAIA projects.


## Installing Prerequisites on AWS Instance

[How to install FFMPEG with NVIDIA GPU Acceleration on Linux](https://www.cyberciti.biz/faq/how-to-install-ffmpeg-with-nvidia-gpu-acceleration-on-linux/)


## Benchmark

## Troubleshoot

This section contains information about some issues encountered during creation and execution of this library.

### ffmpeg - cuda encode - OpenEncodeSessionEx failed: out of memory

This issue is likely occuring during the *multi-video* encoding/decoding process with a GPU.
The error states that the used GPU is 'non-qualified' and only supports a fixed amount of sessions (videos encoded at once) [see StackOverflow](https://stackoverflow.com/questions/46393526/ffmpeg-cuda-encode-openencodesessionex-failed-out-of-memory).

The number of videos that can be encoded/decoded at once can be looked up at: [GPU Support Matrix](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new#Encoder) with the *Max \# of concurrent sessions* column corresponding to the GPU.

There exists a [repository](https://github.com/keylase/nvidia-patch) to *fix* this restriction, but we did not test its functionality.
