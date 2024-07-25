import os
from codecarbon.core.cpu import IntelRAPL


def is_intel_rapl_supported() -> bool:
    """
    Checks if Intel RAPL (Running Average Power Limit) is supported on the system.

    This function performs the following checks:
    1. Verifies the existence of the Intel RAPL directory in the `/sys/class/powercap` filesystem.
    2. Attempts to initialize an `IntelRAPL` instance and checks if the platform is supported.
    3. Handles exceptions that may occur during initialization and setup.

    Returns:
        bool: True if Intel RAPL is supported and successfully initialized, False otherwise.

    Side Effects:
        Prints messages indicating whether Intel RAPL is supported or if an error occurred during setup.

    Example:
        >>> is_intel_rapl_supported()
        Intel RAPL is supported on this system.
        True
        
        >>> is_intel_rapl_supported()
        Intel RAPL is not supported on this system. Falling back to TDP values.
        False

    Notes:
        - Requires the presence of the `IntelRAPL` class or module to perform the initialization check.
        - Relies on the existence of the Intel RAPL directory in the system’s `/sys/class/powercap` path.
    """
    intel_rapl_supported: bool = os.path.exists('/sys/class/powercap/intel-rapl')
    
    if intel_rapl_supported:
        try:
            intel_rapl = IntelRAPL()
            intel_rapl_supported = intel_rapl._is_platform_supported()
            print("Intel RAPL is supported on this system.")
        except Exception as e:
            print(f"Intel RAPL is supported, but could not be setup. Error: {e}")
            intel_rapl_supported = False

    else: 
        print("Intel RAPL is not supported on this system. Falling back to TDP values.")

    return intel_rapl_supported


def intel_rapl_workaround():
    """
    Applies a workaround to enable CodeCarbon to read Intel RAPL (Running Average Power Limit) CPU values until the next system reboot.

    This function performs the following actions:
    1. Checks if Intel RAPL is supported and properly initialized using the `is_intel_rapl_supported` function.
    2. If Intel RAPL is not supported, prompts the user for root credentials to change the permissions of the Intel RAPL directory.
    3. Uses `sudo` to modify the permissions of the `/sys/class/powercap/intel-rapl` directory, allowing read access to the Intel RAPL data.

    Side Effects:
        - Prints a message indicating that Intel RAPL is not ready to be used and prompts for root credentials.
        - Executes a shell command to change the permissions of the Intel RAPL directory.

    Notes:
        - The permission change only affects the current system session and will revert to default permissions upon reboot.

    Example:
        >>> intel_rapl_workaround()
        Intel RAPL not ready to be used, enter root credentials:
        (sudo command is executed to change permissions)
    """

    if not is_intel_rapl_supported():
        print('Intel RAPL not ready to be used, enter root credentials:')
        os.system('sudo chmod -R a+r /sys/class/powercap/intel-rapl')