#!/usr/bin/env python3
import sys 
from src.xrandr import XRandr

def split_primary():
    if len(sys.argv[1:]) > 1:
        ratio = []
        for value in sys.argv[1:]:
            ratio.append(int(value))
    else:
        ratio = [70, 30]
    xrandr = XRandr()
    xrandr.split_primary_monitor(ratio)

def restore_primary():
    xrandr = XRandr()
    xrandr.restore_primary_monitor()

if __name__ == "__main__":
    pass
