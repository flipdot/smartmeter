#!/usr/bin/env python3

import unittest

import sys
from concurrent.futures import thread
from pprint import pprint

import time

import power

test_lines = [
"/HAG5eHZ010C_EHZ1ZA22",
"",
"1-0:0.0.0*255(1095110000140890)",  # Eigentumsnr
"1-0:1.8.1*255(001720.4816)",       # Zaehlerstand bezug
"1-0:2.8.1*255(000001.9160)",       # Zaehlerstand Lieferg.
"1-0:96.5.5*255(82)",               # Status, hex
"0-0:96.1.255*255(0000140890)",     # Fabriknummer
"1-0:32.7.0*255(238.39*V)",         # Spannung L1
"1-0:52.7.0*255(235.92*V)",         # Spannung L2
"1-0:72.7.0*255(234.91*V)",         # Spannung L3
"1-0:31.7.0*255(000.67*A)",         # Strom L1
"1-0:51.7.0*255(000.98*A)",         # Strom L2
"1-0:71.7.0*255(011.18*A)",         # Strom L3
"1-0:21.7.0*255(+00115*W)",         # Wirkleistung L1
"1-0:41.7.0*255(+00141*W)",         # Wirkleistung L2
"1-0:61.7.0*255(+02568*W)",         # Wirkleistung L3
"1-0:96.50.0*0(EE)",    # Netzstatus (bitmask: Drehfeld, Anlaufschwelle, Energierichtung?)
"1-0:96.50.0*1(07CE)",  # Netzperiode, Hex (1/100ms)
"1-0:96.50.0*2(19)",    # aktuelle Chiptemperatur (hex, in C)
"1-0:96.50.0*3(07)",    # minimale Chiptemperatur
"1-0:96.50.0*4(26)",    # gemittelte Chiptemperatur
"1-0:96.50.0*5(09)",    # maximale Chiptemperatur
"1-0:96.50.0*6(003D381B2C0AE75093FF5D0200009F80)",  # Kontrollnummer
"1-0:96.50.0*7(00)",                                # Diagnose
"!",
]

class ParseTest(unittest.TestCase):
    def test_parse(self):
        context = {}
        for line in test_lines:
            power.parse_line(line, context)
        data = power.process(context)
        self.assertTrue('wattage' in data)
        self.assertGreater(data['wattage'], 0)

        pprint(data)

    def test_post(self):
        thread.start_new_thread(power.main)
        time.sleep(2)
        context = {}
        for line in test_lines:
            power.parse_line(line, context)
        data = power.process(context)
        power.post(data)

if __name__ == "__main__":
    sys.exit(unittest.main())