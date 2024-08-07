# Testbeds

All testbeds of GREEM reside in the folder: `greem/testbeds/`.

## Encoding

The `greem/testbeds/encoding/` contains all testbeds that focus on encoding videos.

This folder contains different Python scripts to download publicly available video datasets such as:

- `download_inter4k.py`
  - Downloads the Inter4k dataset in RAW HEVC video codec format.
  - This dataset resides on the AAU FTP server and will be downloaded from there.
  - The dataset size is `340GB` and consists of 1000 videos.
  - The downloaded dataset is located at `greem/testbeds/dataset/Inter4K/60fps/HEVC`.

- `download_segments.py`
  - Downloads the video complexity dataset in RAW HEVC video codec format.
  - This dataset resides on the AAU FTP server and will be downloaded from there.
  - The dataset consists of 500 videos.
  - The downloaded dataset is located at `greem/testbeds/dataset/ref_265`.

- `download_full_input_files.py`
  - Downloads a subset of cablelabs 4K dataset videos.
  - This subset consists of videos available to download on YouTube.
  - To be able do download these files, `yt-dlp` needs to be installed and available on the system (comes installed with the `greem` conda environment).

Further, the subfolders contained in the `encoding` folder are explained:

### Sequential Encoding

Sequential encoding testbeds are located in the folder `greem/testbeds/encoding/sequential_encoding/`.
These testbed scenarios encode videos sequentially in the defined representations, i.e., each video is encoded with exactly one representation at a time. Once the encoding of the video is finished, the next video is encoded in similar manner.

While the encoding testbed is running, monitoring will wrap the encoding process to keep track of the system.

### Parallel Encoding

Parallel encoding testbeds are located in the folder `greem/testbeds/encoding/parallel_encoding/`.
This testbed scenario consists of encoding videos in parallel.
Parallel encoding could either be to encode **O**ne **V**ideo, but with **M**ultiple **R**epresentations (OVMR), or to encode **M**ultiple **V**ideos, but in **O**ne **R**epresentation at a time (MVOR).

The main testbed for parallel encoding is `parallel_encoding.py` that provides two encoding variants:

- One Video, Multiple Representations (OVMR)
  - Encodes videos sequentially with all defined representations at once.
  - If GPU encoding is enabled and multiple GPUs are available, one video will be encoded per GPU in parallel.
- Multiple Videos, One Representation (MVOR)
  - Encodes multiple videos in parallel with one representation each at a time.
  - If GPU encoding is enabled and multiple GPUs are available, multiple videos will be encoded per GPU.

While the encoding testbed is running, monitoring will wrap the encoding process to keep track of the system.

## Decoding

For decoding the `segment_decoding.py` testbed is available.
In order for the testbed to work, encoded videos are required to be available.

While the decoding testbed is running, monitoring will wrap the encoding process to keep track of the system.
