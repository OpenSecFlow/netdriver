#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from netdriver.utils.string import is_blank


def test_is_blank():
    assert is_blank("") == True
    assert is_blank(" ") == True
    assert is_blank("  ") == True
    assert is_blank(" \n") == True
    assert is_blank(" \n ") == True
    assert is_blank(" \r\n") == True
    assert is_blank(" \r\n ") == True
    assert is_blank(" \r\n 123") == False
