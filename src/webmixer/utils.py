#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
Auxiliary functions.
"""

import os, sys, re, stat, platform

from .consts import HOME_PATH_RE, ALLOWED_DYNAMIC_URLS


def is_win_form():
    if "win" in sys.platform.lower():
        if "darwin" not in sys.platform.lower():
            return True
    return False


def is_linux_like():
    os_descs = [platform.system(), sys.platform]
    for one_desc in os_descs:
        if ("linux" in one_desc.lower()) or ("bsd" in one_desc.lower()):
            return True
    return False


def is_hidden(path, subpath, allow_dot=False, check_tilde=False):
    if check_tilde and path.endswith("~"):
        return True
    if not os.access(path, os.R_OK):
        return True
    stat_res = os.stat(path)

    if (
        hasattr(stat_res, "st_file_attributes")
        and hasattr(stat, "FILE_ATTRIBUTE_HIDDEN")
    ):
        if bool(stat_res.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN):
            return True

    if (hasattr(stat_res, "st_flags") and hasattr(stat, "UF_HIDDEN")):
        if bool(stat_res.st_flags & stat.UF_HIDDEN):
            return True

    if (subpath.startswith(".") and (not allow_dot)):
        return True

    return False


def trim_subpath(subpath):
    return subpath.strip("/")


def is_dotted_inner(path_end):
    for path_part in path_end.split("/"):
        if path_part.startswith(".") and (path_part != "."):
            return True
    return False


def shorten_home_dir(path):
    match = HOME_PATH_RE.match(path)
    if match is None:
        return path
    return "~/" + path[match.end():]


def is_url_session_wise(url):
    return ALLOWED_DYNAMIC_URLS.match(url) is not None


def take_mapping(file_path, is_session):
    mapping = []
    if not file_path:
        return mapping

    first_path = None
    with open(file_path, "r", encoding="utf-8") as file_hnd:
        for line in file_hnd.readlines():
            line = line.strip()
            if ((not line) or (line[0] == "#")):
                continue
            if first_path is None:
                first_path = line
            else:
                if not first_path.endswith("/"):
                    first_path += "/"
                if not line.endswith("/"):
                    line += "/"
                if is_session:
                    if not is_url_session_wise(first_path):
                        first_path = None
                        continue
                mapping.append({
                    "url": first_path,
                    "url_re": re.compile(re.escape(first_path)),
                    "dir": line,
                    "dir_re": re.compile(re.escape(line)),
                })
                first_path = None

    return mapping


def normalize_path(path):
    return os.path.abspath(os.path.expanduser(path)).replace(os.sep, '/')
