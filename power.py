#!/usr/bin/env python3
import http
import json
import subprocess
import datetime
import math
import traceback
import urllib.request, urllib.error, urllib.parse
import time
import serial
import threading
from queue import Queue
import re
from pprint import pprint

# init serial connection 
#ser = serial.Serial("/dev/ttyAMA0",9600,xonxoff=False)


# ----- serial read process, running in background ---------------------------------------------------
import config

eol_char = b'\n'									# this is the character at the end of a complete input line
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
            if s == eol_char:
                lines.put(input_line.strip())
                #print("input:", input_line.strip())
                input_line = ""
                break
            elif ord(s) > 31:
                input_line = input_line + s.decode("utf-8")
                if len(input_line) > max_buffer_length:
                    lines.put(input_line.strip())
                    input_line = ""
                    break
        time.sleep(0.01)
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
    "96.5.5*255": "status-hex",
}

def parse_line(line, context):
    match = line_regex.match(line)
    if not match:
        #print("not matched: '"+line+"'")
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
current_data = None

def do_stuff(data):
    global last_post_time
    time_now = time.monotonic()
    if last_post_time + config.post_every_n_sec > time_now:
        return
    last_post_time = time_now
    try:
        post(data)
    except Exception as e:
        print("post connection err:", repr(e))

first = True

def post(data):
    num = 0
    print("posting", len(config.post_mapping.items()), "attributes")
    #print(data)
    conn = http.client.HTTPSConnection(config.server, timeout=config.timeout)

    items = []
    for key, post in config.post_mapping.items():
        if key not in data:
            print("warn: key '%s' not in data" % key)
            continue

        item = {
            "SensorType": post['type'],
            "Location": post['location'],
            "Value": data[key],
        }
        global first
        if first:
            first = False
            item["Unit"] = post['unit']
            item["Description"] = post['desc']
        items.append(item)

    try:
        conn.request("PUT", config.path, body=json.dumps(items))
        res = conn.getresponse()
        res_text = res.read().decode('utf-8')
        print(res.status, res.reason, ":", res_text)

        if res.status != 200:
            print("post return code:", res.status, res.reason, "text:", res_text)
    except urllib.error.URLError as e:
        print("post err:", e)

def setup_urllib():
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, config.server, config.server_user, config.server_pass)
    authhandler = urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)

def parse_queue():
    global current_data
    new_context = {}
    while True:
        try:
            line = lines.get().strip()
            if line == "!":
                data = process(new_context)
                current_data = new_context
                new_context = {}
            else:
                parse_line(line, new_context)
        except Exception as e:
            print("exception:", repr(e))
            traceback.print_exc()
        time.sleep(0.01)


def main(serial=True):
    setup_urllib()
    t = threading.Thread(target=readserial, args=(eol_char, max_buffer_length))
    t.setDaemon(True)
    if serial:
        t.start()

    t = threading.Thread(target=parse_queue)
    t.setDaemon(True)
    t.start()

    global current_data
    while True:
        if current_data is not None:
            d = current_data
            current_data = None
            do_stuff(d)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
