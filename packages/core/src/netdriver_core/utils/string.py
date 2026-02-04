#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def is_blank(input: str) -> bool:
    """ Check if input is blank
    :param input: str
    :return bool
    """
    if not input:
        return True

    # check all lines are blank
    input = input.replace("\r", "\n")
    for line in input.split("\n"):
        x = line.strip()
        if x:
            return False
    return True


