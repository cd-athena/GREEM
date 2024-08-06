# Testbeds

All testbeds of GREEM reside in the folder: `GREEM/greem/testbeds/`.

## Encoding

The `GREEM/greem/testbeds/encoding/` contains all testbeds that focus on encoding videos.

This folder contains different Python scripts to download publicly available video datasets such as:

- `download_inter4k.py`
  - Downloads the Inter4k dataset in the RAW HEVC video codec format.
  - This dataset resides on the AAU FTP server and will be downloaded from there.
  - The dataset size is `340GB` and consists of 1000 videos.
  - The downloaded dataset is located at `GREEM/greem/testbeds/dataset/Inter4K/60fps/HEVC`.

- `download_segments.py`
- `download_full_input_files.py`

Further, the subfolders contained in the `encoding` folder are explained:

### Sequential Encoding

### Parallel Encoding

Parallel encoding testbeds are located in the folder `GREEM/greem/testbeds/encoding/parallel_encoding/`.

The main testbed for parallel encoding is `parallel_encoding.py` that provides two encoding variants:

- One Video, Multiple Representations (OVMR) and
- Multiple Videos, One Representation

## Decoding
