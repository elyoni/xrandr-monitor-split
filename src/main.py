#!/usr/bin/env python3
import sys 
from src.xrandr import XRandr

def split_primary():
    ratio = []
    for value in sys.argv[1:]:
        ratio.append(int(value))
    print(ratio)
    xrandr = XRandr()
    xrandr.split_primary_monitor(ratio)

def restore_primary():
    xrandr = XRandr()
    xrandr.restore_primary_monitor()

if __name__ == "__main__":
    pass
