#!/usr/bin/env python3

#post_every_n_sec = 60
post_every_n_sec = 5

server = "api.flipdot.org"
path = "/sensors/"
server_user = "XXXXX"
server_pass = "XXXXX"
timeout = 15

# https://<server>sensors/<sensortype>/<location>/<value>[/<unit>[/<description>]]
post_mapping = {
    'wattage': {
        'type': 'power', 'location': 'wattage_total',    'unit': 'W',    'desc': 'Total power consumption',
    },
    'wattage-L1': {
        'type': 'power', 'location': 'wattage_L1',       'unit': 'W',    'desc': 'Power consumption on phase 1',
    },
    'wattage-L2': {
        'type': 'power', 'location': 'wattage_L2',       'unit': 'W',    'desc': 'Power consumption on phase 2',
    },
    'wattage-L3': {
        'type': 'power', 'location': 'wattage_L3',       'unit': 'W',    'desc': 'Power consumption on phase 3',
    },
    'amperage-L1': {
        'type': 'power', 'location': 'amperage_L1',      'unit': 'A',    'desc': 'Current on phase 1',
    },
    'amperage-L2': {
        'type': 'power', 'location': 'amperage_L2',      'unit': 'A',    'desc': 'Current on phase 2',
    },
    'amperage-L3': {
        'type': 'power', 'location': 'amperage_L3',      'unit': 'A',    'desc': 'Current on phase 3',
    },
    'voltage-L1': {
        'type': 'power', 'location': 'voltage_L1',       'unit': 'V',    'desc': 'Voltage on phase 1',
    },
    'voltage-L2': {
        'type': 'power', 'location': 'voltage_L2',       'unit': 'V',    'desc': 'Voltage on phase 2',
    },
    'voltage-L3': {
        'type': 'power', 'location': 'voltage_L3',       'unit': 'V',    'desc': 'Voltage on phase 3',
    },
    'frequency': {
        'type': 'power', 'location': 'frequency',        'unit': 'Hz',   'desc': 'Mains frequency',
    },
    'kwh': {
        'type': 'power', 'location': 'consumption',      'unit': 'KWh',  'desc': 'Accumulated power consumption since reset',
    },

    'temp': {
        'type': 'temperature', 'location': 'smartmeter', 'unit': 'C',    'desc': 'Room temperature at fuse box',
    },
}
