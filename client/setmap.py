#!/usr/bin/env python
#
# A simple client for Webmixer.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
Tests of setting the dynamic mapping of Webmixer.
"""

import sys, re, socket

MAPPING_PORT = 12001
MAPPING_DOMAIN = "localhost"
MAP_REQUEST_STAGE1 = "MAP/1.0 SET DIR\r\n"
MAP_ANSWER_STAGE1 = "MAP/1.0 CHALLENGE"
MAP_REQUEST_STAGE2 = "MAP/1.0 ANSWER\r\n"
MAP_ANSWER_STAGE2 = "MAP/1.0 OK 201"
MAP_ERROR_START = re.compile(re.escape("MAP/1.0 KO"))


def ask_to_map(local_dir):
    """
    Asks the Webmixer server to map the directory provided as the parameter.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((MAPPING_DOMAIN, MAPPING_PORT))
        sock.sendall((MAP_REQUEST_STAGE1 + local_dir + "\r\n").encode("utf-8"))
        response = str(sock.recv(4096), "utf-8").splitlines()
        if (
            (len(response) > 0)
            and (MAP_ERROR_START.match(response[0].upper()) is not None)
        ):
            sys.stderr.write("".join((
                "server disagrees at stage 1 for '",
                local_dir,
                "'\n",
                str(response),
                "\n")))
            return None
        if (
            (len(response) < 2) or (len(response[1].strip()) == 0)
            or (response[0].upper().strip() != MAP_ANSWER_STAGE1)
        ):
            sys.stderr.write("".join((
                "unrecognized response on request for '",
                local_dir,
                "'\n",
                str(response),
                "\n")))
            return None

        challenge_answer = ""
        with open(response[1].strip(), encoding="utf8") as fh:
            challenge_answer = fh.readline().strip()
        sock.sendall("".join((
            MAP_REQUEST_STAGE2,
            challenge_answer,
            "\r\n")).encode("utf-8"))

        response = str(sock.recv(4096), "utf-8").splitlines()
        if (
            (len(response) > 0)
            and (MAP_ERROR_START.match(response[0].upper()) is not None)
        ):
            sys.stderr.write("".join((
                "server disagrees at stage 2 for '",
                local_dir,
                "'\n",
                str(response),
                "\n")))
            return None
        if (
            (len(response) < 2) or (len(response[1].strip()) == 0)
            or (response[0].upper().strip() != MAP_ANSWER_STAGE2)
        ):
            sys.stderr.write("".join((
                "unrecognized response on answer for '",
                local_dir,
                "'\n",
                str(response),
                "\n")))
            return None
        return str(response[1]).strip()


if __name__ == "__main__":
    for item in sys.argv[1:]:
        try:
            res = ask_to_map(item)
            if res is not None:
                sys.stdout.write("".join((
                    "the dir '",
                    item,
                    "' is mapped to:\n",
                    str(res),
                    "\n")))
        except (OSError, ValueError) as exc:
            sys.stderr.write("".join((
                "an issue while communicating with the server:\n",
                str(exc),
                "\n")))
