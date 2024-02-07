# Docker

This section has the necessary instructions to create a Docker container with all necessary dependencies to execute benchmarks within GREEM.

## Prerequisites

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

This will start the container with the entry point of it being the root of GREEM.

## Building and running GREEM

When you're ready, start the application by running:
`docker compose up --build`.

Finally, to run the Docker container, execute the following command:

```bash
docker run --rm --runtime=nvidia -it gaiatools-greem bash
```

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References

- [Docker's Python guide](https://docs.docker.com/language/python/)
