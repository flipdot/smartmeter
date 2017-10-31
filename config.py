#!/usr/bin/env python3

post_every_n_sec = 60

server = "https://api.flipdot.org"
server_user = "XXXXX"
server_pass = "XXXXX"
timeout = 5

# https://<server>sensors/<sensortype>/<location>/<value>[/<unit>[/<description>]]
post_mapping = {
    'wattage': {
        'base': 'sensors/power/wattage_total',    'unit': 'W',    'desc': 'Total power consumption',
    },
    'wattage-L1': {
        'base': 'sensors/power/wattage_L1',       'unit': 'W',    'desc': 'Power consumption on phase 1',
    },
    'wattage-L2': {
        'base': 'sensors/power/wattage_L2',       'unit': 'W',    'desc': 'Power consumption on phase 2',
    },
    'wattage-L3': {
        'base': 'sensors/power/wattage_L3',       'unit': 'W',    'desc': 'Power consumption on phase 3',
    },
    'amperage-L1': {
        'base': 'sensors/power/amperage_L1',      'unit': 'A',    'desc': 'Current on phase 1',
    },
    'amperage-L2': {
        'base': 'sensors/power/amperage_L2',      'unit': 'A',    'desc': 'Current on phase 2',
    },
    'amperage-L3': {
        'base': 'sensors/power/amperage_L3',      'unit': 'A',    'desc': 'Current on phase 3',
    },
    'voltage-L1': {
        'base': 'sensors/power/voltage_L1',       'unit': 'V',    'desc': 'Voltage on phase 1',
    },
    'voltage-L2': {
        'base': 'sensors/power/voltage_L2',       'unit': 'V',    'desc': 'Voltage on phase 2',
    },
    'voltage-L3': {
        'base': 'sensors/power/voltage_L3',       'unit': 'V',    'desc': 'Voltage on phase 3',
    },
    'frequency': {
        'base': 'sensors/power/frequency',        'unit': 'Hz',   'desc': 'Mains frequency',
    },
    'kwh': {
        'base': 'sensors/power/consumption',      'unit': 'KWh',  'desc': 'Accumulated power consumption since reset',
    },

    'temp': {
        'base': 'sensors/temperature/smartmeter', 'unit': 'C',    'desc': 'Room temperature at fuse box',
    },
}
