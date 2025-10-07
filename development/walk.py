#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os


def tree(dir: str):
    for root, dirs, files in os.walk(dir):
        level = root.replace(dir, '').count(os.sep)
        indent = ' ' * 2 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 2 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")


def main():
    tree("/srv/workspace/netdriver/components/netdriver/plugins")


if __name__ == "__main__":
    sys.exit(main())
