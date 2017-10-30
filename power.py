#!/usr/bin/env python2
from __future__ import print_function
import subprocess
import datetime
import math
from time import *
import serial
from thread import start_new_thread
from Queue import Queue
import re
from pprint import pprint

# init serial connection 
#ser = serial.Serial("/dev/ttyAMA0",9600,xonxoff=False)


# ----- serial read process, running in background ---------------------------------------------------
eol_char = chr(13)									# this is the character at the end of a complete input line
max_buffer_length = 80								# max number of characters received for processing buffer
                                                    # without receiving eol_char
new_input_line = ""
stop_thread = False									# global flag, used to terminate thread if program exits

lines = Queue()

def readserial (eol_char, max_buffer_length):
    ser = serial.Serial("/dev/ttyUSB0", 9600, xonxoff=False,
                        bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN,
                        stopbits=serial.STOPBITS_ONE)
    ser.flushInput()

    input_line = ""

    while (stop_thread == False):
        while ser.inWaiting() > 0:
            s = ser.read()
            #print("input:", s)
            if s == eol_char:
                lines.put(input_line.strip())
                input_line = ""
                break
            elif ord(s) > 31:
                input_line = input_line + s
                if len(input_line) > max_buffer_length:
                    lines.put(input_line.strip())
                    input_line = ""
                    break
        sleep(0.01)
    return


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

line_regex = re.compile(r"^1-0:(?P<id>[^\(]+)\((?P<value>[^\)\*]+)(\*(?P<unit>[AWV]))?\)$")

idToKey = {
    "0.0.0*255": "idnumber-str",
    "96.1.255*255": "productnumber-str",
    "32.7.0*255": "voltage-L1",
    "52.7.0*255": "voltage-L2",
    "72.7.0*255": "voltage-L3",
    "31.7.0*255": "amperage-L1",
    "51.7.0*255": "amperage-L2",
    "71.7.0*255": "amperage-L3",
    "21.7.0*255": "wattage-L1",
    "41.7.0*255": "wattage-L2",
    "61.7.0*255": "wattage-L3",
    "96.50.0*0": "state-bits-hex",
    "96.50.0*1": "period-hex",
    "96.50.0*2": "temp-hex",
    "96.50.0*3": "temp-min-hex",
    "96.50.0*4": "temp-med-hex",
    "96.50.0*5": "temp-max-hex",
    "96.50.0*6": "control-hex-str",
    "1.8.1*255": "kwh",
    "2.8.1*255": "kwh-org",
    "96.50.0*7": "diagnostic-str",
}

def parse_line(line, context):
    match = line_regex.match(line)
    if not match:
        print("not matched: '"+line+"'")
        return
    dic = match.groupdict()
    #print(dic)
    if dic['id'] in idToKey:
        key = idToKey[dic['id']]
        value = dic['value']
        #context[key] = value
        if key.endswith("-hex"):
            context[key[:-4]] = int(value, 16)
        elif key.endswith("-str"):
            context[key] = value
        else:
            context[key] = float(value)
    else:
        print("unknown: '" + line + "'")

def process(data):
    data['wattage'] = data["wattage-L1"] + data["wattage-L2"] + data["wattage-L3"]
    pprint(data)

def main():
    start_new_thread(readserial, (eol_char, max_buffer_length))
    while True:
        context = {}
        try:
            line = lines.get().strip()
            #print("line: '" + line +"'")
            if line == "!":
                process(context)
                context = {}
            else:
                parse_line(line, context)
        except Exception as e:
            print(e)
        sleep(0.01)

if __name__ == "__main__":
    context = {}
    for line in test_lines:
        parse_line(line, context)
    process(context)
