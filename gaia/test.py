from codecarbon import track_emissions
from codecarbon.core.cpu import IntelPowerGadget, IntelRAPL
from time import sleep

@track_emissions()
def sleep_function(secs: int = 5):
    sleep(secs)
    
    
sleep_function()

# IntelRAPL()