import os
from codecarbon.core.cpu import IntelRAPL


def is_intel_rapl_supported() -> bool:
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
    '''Intel RAPL workaround that enables CodeCarbon to read the CPU values until reboot'''

    if not is_intel_rapl_supported():
        print('Intel RAPL not ready to be used, enter root credentials:')
        os.system('sudo chmod -R a+r /sys/class/powercap/intel-rapl')