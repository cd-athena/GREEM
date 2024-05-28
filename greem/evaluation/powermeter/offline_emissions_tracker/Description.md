# Powermeter - OfflineEmissionsTracker Comparison

This folder contains 7 CSV files with energy measurements of an idle system for approximately 2 minutes each.
Each of them measure the idle state of a Lenovo laptop.

## `idle_powermeter_x`

These three files contain the powermeter measurements without any of our processes running.

## `idle_omt_x`

These three files contain the powermeter measurements, but also an `OfflineEmissionsTracker` instance with a measurement interval of one second is running.
This is done to see the energy impact of the `OfflineEmissionsTracker`.

## The code used for measurement

```python
host_name: str = os.uname()[1]
measurement_interval = 1

tracker = OfflineEmissionsTracker(
    measure_power_secs=measurement_interval, 
    project_name='test test', 
    log_level='error',
    output_file=f'offline_idle_emissions_{host_name}.csv')

os.system('sleep 5')
os.system('stress -c 4 -t 1 -q')

tracker._project_name = f'sleep_{measurement_interval}s_{host_name}'
tracker.start()
os.system('sleep 120')
tracker.stop()

os.system('stress -c 4 -t 10')
```