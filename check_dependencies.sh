#!/usr/bin/env bash

# Define colors
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
RESET='\033[0m'

# set -x
# set -eo pipefail

if ! [ -x "$(command -v python)" ]; then
    echo -e "${RED}Error: Python is not installed!${RESET}"
    echo -e "${RED}Python is mandatory to run this project!${RESET}"
    echo -e "${RED}Please install Python before you proceed.${RESET}"
    exit 1
else
    echo -e "${GREEN}- Python installed.${RESET}"
fi

if ! [ -x "$(command -v conda)" ]; then
    echo -e "${RED}Error: Anaconda/Miniconda is not installed!${RESET}"
    echo -e "Check ${BLUE}README.md${RESET} for installation instructions or execute the following:"
    echo -e "${BLUE}mkdir -p ~/miniconda3"
    echo -e "wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh"
    echo -e "bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3"
    echo -e "rm -rf ~/miniconda3/miniconda.sh"
    echo -e "~/miniconda3/bin/conda init bash${RESET}"
    exit 1
else
    echo -e "${GREEN}- Anaconda/Miniconda installed.${RESET}"
fi

if ! [ -x "$(command -v nvitop)" ]; then
    echo -e "${RED}Error: Could not access Python virtual environment command.${RESET}"
    echo >&2 "This is likely has two causes:"
    echo >&2 "1. The Anaconda Python environment is not created."
    echo >&2 "2. The Anaconda Python environment is not activated."
    exit 1
else
    echo -e "${GREEN}- conda activated.${RESET}"
fi

if ! [ -x "$(command -v ffmpeg)" ]; then
    echo -e "${RED}ffmpeg is not installed.${RESET}"
    echo -e "${RED}FFmpeg is mandatory to run this project.${RESET}"
    echo -e "Check ${BLUE}README.md/INSTALL.md${RESET} for installation instructions."
    exit 1
else
    echo -e "${GREEN}- FFmpeg installed.${RESET}"
fi

if ! [ -x "$(command -v nvidia-smi)" ]; then
    echo -e "${YELLOW}Error: nvidia-smi is not installed."
    echo -e "- If you plan to use a GPU, ensure that Nvidia drivers are installed on the system.${RESET}"
else
    echo -e "${GREEN}- nvidia-smi installed.${RESET}"
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -d "/sys/class/powercap/intel-rapl"]; then
        echo -e "${GREEN}CPU power measurements likely supported by system."
        echo -e "Ensure that the usergroup has access to /sys/class/powercap/intel-rapl."
        echo -e "Quick workaround:${RESET}"
        echo -e "${BLUE}sudo chmod -R a+r /sys/class/powercap/intel-rapl${RESET}"
    else
        echo -e "${YELLOW}CPU power measurements might not be supported by this system."
    fi
else
    echo -e "${YELLOW}CPU power measurements might not be supported by this system."
fi
