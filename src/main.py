#!/usr/bin/env python3
import sys
from src.xrandr import XRandr
from src.config import parse_yaml_to_tree, yaml_data, verify_tree


def split_primary():
    if len(sys.argv[1:]) > 1:
        ratio = []
        for value in sys.argv[1:]:
            ratio.append(int(value))
    else:
        ratio = [70, 30]

    tree = parse_yaml_to_tree(yaml_data)
    if verify_tree(tree):
        xrandr = XRandr()
        xrandr.split_primary_monitor(tree)
    else:
        print("The tree is invalid.")


def restore_primary():
    xrandr = XRandr()
    print(xrandr.restore_primary_monitor())


if __name__ == "__main__":
    pass
