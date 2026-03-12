#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re


def simulate_output(input: str) -> str:
    """ Simulate the terminal to handle char stream and get the compressed output
    Input:
      array-ag>enable\r\n
      \rEnable password:\r\n
      \r\n
      \rarray-ag#switch vpndg\r\n
      \r\r\n
      \rvpndg$configure terminal\r\n
      \r
      \r\n
      \rvpndg(config)$aaa map group \"                                                               \r
      \rvpndg(config)$aaa map group \"San                                                            \r
      \rvpndg(config)$aaa map group \"San F                                                         \r
      \rvpndg(config)$aaa map group \"San Fra                                                      \r
      \rvpndg(config)$aaa map group \"San Fran                                                   \r
      \rvpndg(config)$aaa map group \"San Franc                                                \r
      \rvpndg(config)$aaa map group \"San Francis                                            \r
      \rvpndg(config)$aaa map group \"San Francisco                                         \r
      \rvpndg(config)$aaa map group \"San Francisco VPN                                   \r
      \rvpndg(config)$aaa map group \"San Francisco VPN Group\" \"g-SF-VPN\"\b\b\b\b\r\n
      \rAlready has a group map for external group \"San Francisco VPN Group\". \r\n
      \rvpndg(config)$

    Output:
      array-ag>enable
      Enable password:

      array-ag#switch vpndg

      vpndg$configure terminal

      vpndg(config)$aaa map group "San Francisco VPN Group" "g-SF-VPN"
      Already has a group map for external group "San Francisco VPN Group".
      vpndg(config)$
    """
    length = len(input)
    lines = []
    line = ""
    i = 0
    while i < length:
        if is_carry_return(input[i:i+3]):
            lines.append(line)
            line = ""
            i += 3
        elif is_carry_return(input[i:i+2]):
            lines.append(line)
            line = ""
            i += 2
        elif input[i] == "\r":
            line = ""
            i += 1
        else:
            line += input[i]
            i += 1
    if line:
        lines.append(line)
    return "\n".join(lines)


def is_carry_return(escape: str) -> bool:
    return escape == "\r\r\n" or escape == "\r\n"


def oct_to_chinese(oct_str: str, encoding: str ="gbk") -> str:
    oct_parts = [p for p in oct_str.split("\\") if p]
    valid_bytes = []
    for part in oct_parts:
        dec_val = int(part, 8) % 256
        valid_bytes.append(dec_val)

    bytes_data = bytes(valid_bytes)
    return bytes_data.decode(encoding, errors="ignore")


def simulate_output_oct_to_chinese(output: str, encoding: str ="gbk") -> str:
    """ Simulate the terminal to handle octal to Chinese conversion """
    if not output:
        return output
    oct_pattern = r"(\\\d{3})+"
    start = 0
    end = 0
    result = []
    for match in re.finditer(oct_pattern, output):
        oct_str = match.group()
        start = match.start()
        if end == 0:
            result.append(output[:start])
        else:
            result.pop()
            result.append(output[end:start])
        try:
            result.append(oct_to_chinese(oct_str=oct_str, encoding=encoding))
        except Exception:
            result.append(oct_str)
        end = match.end()
        result.append(output[end:])
    return "".join(result) if result else output