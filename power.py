#!/usr/bin/env python3

import subprocess
import datetime
import math
import urllib.request, urllib.error, urllib.parse
from time import *
import serial
import threading
from queue import Queue
import re
from pprint import pprint

# init serial connection 
#ser = serial.Serial("/dev/ttyAMA0",9600,xonxoff=False)


# ----- serial read process, running in background ---------------------------------------------------
import config

eol_char = chr(13)									# this is the character at the end of a complete input line
max_buffer_length = 80								# max number of characters received for processing buffer
                                                    # without receiving eol_char
new_input_line = ""
stop_thread = False									# global flag, used to terminate thread if program exits

lines = Queue()

def readserial(eol_char, max_buffer_length):
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
    "96.50.0*1": "period-10usec-hex",
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
    data['period'] = data['period-10usec'] / 100.0 / 1000.0
    data['frequency'] = 1 / data['period']
    return data

last_post_time = 0

def do_stuff(data):
    global last_post_time
    time_now = time.monotonic()
    if last_post_time + config.post_every_n_sec > time_now:
        return
    last_post_time = time_now
    pprint("posting:", data)
    post(data)

def post(data):
    for key, post in config.post_mapping.items():
        if key not in data:
            print("warn: key '%s' not in data" % key)
            continue
        url = "/".join([
            config.server, post['base'],
            urllib.parse.quote(str(data[key])),
            urllib.parse.quote(post['unit']),
            urllib.parse.quote(post['desc'])
        ])
        #print("posting:", url)
        try:
            res = urllib.request.urlopen(url, timeout=config.timeout)
            ret = res.read()
            if res.getcode() != 200:
                print("post return code:", res.getcode())
            #print("return: ", ret)
        except urllib.error.URLError as e:
            print("post err:", e)

def setup_urllib():
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, config.server, config.server_user, config.server_pass)
    authhandler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)

def main(serial=True):
    setup_urllib()
    t = threading.Thread(target=readserial, args=(eol_char, max_buffer_length))
    t.setDaemon(True)
    if serial:
        t.start()
    while True:
        context = {}
        try:
            line = lines.get().strip()
            if line == "!":
                data = process(context)
                context = {}
                do_stuff(data)
            else:
                parse_line(line, context)
        except Exception as e:
            print(e)
        sleep(0.01)

if __name__ == "__main__":
    main()
