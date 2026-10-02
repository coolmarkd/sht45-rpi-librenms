#!/usr/bin/env python3
import glob
import json
import os
import sys
import tempfile
import time


PORT = None
BAUD = 115200            
READ_TIMEOUT = 5.0       
CACHE_SECONDS = 30
CACHE_FILE = os.path.join(tempfile.gettempdir(), "sht45-trinkey.json")



def find_port():
    if PORT:
        return PORT
    for pattern in ("/dev/serial/by-id/*Trinkey*", "/dev/serial/by-id/*SHT4*",
                    "/dev/serial/by-id/*Adafruit*", "/dev/ttyACM*"):
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[0]
    raise RuntimeError("no SHT serial port found")


def _num(text):
    try:
        return float(text)
    except ValueError:
        return None


def parse_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    fields = [f.strip() for f in line.split(",")]
    if len(fields) == 2:
        temp, rh = _num(fields[0]), _num(fields[1])
    elif len(fields) >= 3:
        temp, rh = _num(fields[1]), _num(fields[2])    # field 0 is the serial number
    else:
        return None
    if temp is None or rh is None or not (-40 <= temp <= 125) or not (0 <= rh <= 100):
        return None
    return temp, rh


def read_serial():
    import serial

    deadline = time.monotonic() + READ_TIMEOUT

    with serial.Serial(find_port(), BAUD, timeout=1) as ser:
        ser.reset_input_buffer()
        ser.readline()      # throw away a possibly partial first line
        while time.monotonic() < deadline:
            raw = ser.readline().decode("ascii", errors="replace")
            parsed = parse_line(raw)
            if parsed:
                return parsed
    raise RuntimeError("no response from SHT within %.0fs" % READ_TIMEOUT)


def read_cached():
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
        if time.time() - data["ts"] < CACHE_SECONDS:
            return data["temp"], data["rh"]
    except (OSError, ValueError, KeyError):
        pass
    temp, rh = read_serial()
    try:
        tmp = CACHE_FILE + ".%d" % os.getpid()
        with open(tmp, "w") as f:
            json.dump({"ts": time.time(), "temp": temp, "rh": rh}, f)
        os.replace(tmp, CACHE_FILE)
    except OSError:
        pass
    return temp, rh


def main():
    name = os.path.basename(sys.argv[0])
    if "temperature" in name:
        what = "temperature"
    elif "humidity" in name:
        what = "humidity"
    else:
        what = sys.argv[1] if len(sys.argv) > 1 else "both"

    if what == "raw":
        import serial
        port = find_port()
        print("# port:", port)
        with serial.Serial(port, BAUD, timeout=1) as ser:
            for _ in range(5):
                line = ser.readline().decode("ascii", errors="replace").rstrip()
                print(repr(line), "->", parse_line(line))
        return 0

    try:
        temp, rh = read_cached()
    except Exception as err:
       
        print(err, file=sys.stderr)
        return 1

    if what == "temperature":
        print("%.2f" % temp)
    elif what == "humidity":
        print("%.2f" % rh)
    else:
        print("temperature=%.2f humidity=%.2f" % (temp, rh))
    return 0


if __name__ == "__main__":
    sys.exit(main())
