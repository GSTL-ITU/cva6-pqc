#!/usr/bin/env python3
"""Logs the CVA6 UART until a line contains one of the stop texts.

  uart_log.py --port /dev/ttyUSB0 --log out.log [--until "result "] [--trigger] [--timeout 3600]

--trigger answers the "Waiting for trigger" line of the older pqc_tests_fpga
programs with 'c'.
"""
import argparse
import sys
import time
import serial

ap = argparse.ArgumentParser()
ap.add_argument("--port", default="/dev/ttyUSB0")
ap.add_argument("--baud", type=int, default=57600)
ap.add_argument("--log", required=True)
ap.add_argument("--until", action="append", default=[])
ap.add_argument("--trigger", action="store_true")
ap.add_argument("--timeout", type=float, default=3600)
a = ap.parse_args()
until = a.until or ["result "]

t0 = time.time()
with serial.Serial(a.port, a.baud, timeout=0.2) as ser, open(a.log, "w") as log:
    ser.reset_input_buffer()
    line = ""
    while time.time() - t0 < a.timeout:
        d = ser.read(256).decode(errors="replace")
        if not d:
            continue
        d = d.replace("\r", "")
        log.write(d)
        log.flush()
        sys.stdout.write(d)
        sys.stdout.flush()
        line += d
        *done, line = line.split("\n")
        for l in done:
            if a.trigger and "Waiting for trigger" in l:
                ser.write(b"c")
            if any(u in l for u in until):
                sys.exit(0)
sys.exit("timeout")
