#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
Fixed constatnts used within the application.
"""

import re, pathlib

APPLICATION_NAME = "Webmixer"
APPLICATION_LINK = "https://webmixer.tangloid.net"
APPLICATION_LICENSE = "MIT"
APPLICATION_VERSION = "0.3"

SERVER_DOMAIN = "localhost"
PORT_MIN = 1024
PORT_MAX = 65535
# default port of the server for setting the mapping
SERVER_SETTING_PORT = 12001
SERVER_SETTING_TIMEOUT = 2
# default port of the web server
SERVER_SERVING_PORT = 12000
# the port range tried for the web server when it is set to be random
SERVER_SERVING_PORT_MIN = 15000
SERVER_SERVING_PORT_MAX = 40000

LOGGING_WEB_DEFAULT = False
LOGGING_SET_DEFAULT = False

HOME_PATH_RE = re.compile(re.escape(str(pathlib.Path.home())+"/"))

# paths to saved mappings
MAPPING_STATIC = "~/.webmixer/mapping_static"
MAPPING_STATIC_WIN = "~/webmixer_mapping.ini"
MAPPING_SESSION = "~/.webmixer/mapping_session"
MAPPING_SESSION_WIN = "~/webmixer_session.ini"

RANDOM_STRING_LENGTH = 16
HEXDIGITS = "0123456789abcdef"
ALLOWED_DYNAMIC_URLS = re.compile("\\/[" + HEXDIGITS + "]{8,32}\\/$")

# directives of the dynamic mapping (with "\r\n" upended)
SET_MAP_DIR = "MAP/1.0 SET DIR"
SET_MAP_CHG = "MAP/1.0 CHALLENGE"
SET_MAP_ANS = "MAP/1.0 ANSWER"
SET_MAP_201_SC = 201
SET_MAP_201 = f"MAP/1.0 OK {SET_MAP_201_SC}"
SET_MAP_400_SC = 400
SET_MAP_400 = f"MAP/1.0 KO {SET_MAP_400_SC}"
SET_MAP_401_SC = 401
SET_MAP_401 = f"MAP/1.0 KO {SET_MAP_401_SC}"
SET_MAP_500_SC = 500
SET_MAP_500 = f"MAP/1.0 KO {SET_MAP_500_SC}"

# headers that are checked on HTTP requests
HEADER_RCV_HOST = "Host"
HEADER_RCV_HOST_VAL = re.compile(
    "localhost(\\:[\\d]*)?(\\/|$)", re.IGNORECASE)
HEADER_RCV_REFERER = "Referer"
HEADER_RCV_REFERER_VAL = re.compile(
    "http(s)?\\:\\/\\/localhost(\\:[\\d]*)?\\/", re.IGNORECASE)
HEADER_RCV_ORIGIN = "Origin"
HEADER_RCV_ORIGIN_VAL = re.compile(
    "http(s)?\\:\\/\\/localhost(\\:[\\d]*)?(\\/|$)", re.IGNORECASE)
HEADER_RCV_SFS = "Sec-Fetch-Site"
HEADER_RCV_SFS_VAL = "same-origin"
# Regarding the Sec-Fetch-Site header, see e.g.:
# https://www.w3.org/TR/fetch-metadata/
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-Fetch-Site

# direct serving (i.e. w/o set Referer header) is for html files only
SRV_FT_WITHOUT_REF = ["html", "htm"]

SRV_SC_OK = 200
SRV_SC_NA = 403
SRV_SC_NF = 404
SRV_SC_REDIRECT = 301

HEADER_SND_REDIRECT = "Location"

HEADER_SND_TYPE = "Content-type"
HEADER_SND_TYPE_DIR = "text/html; charset=utf-8"
HEADER_SND_TYPE_TURN_CMF = {
    "path_end": "manifest",
    "from": "application/octet-stream",
    "to": "text/cache-manifest"
}
HEADER_SND_TYPE_TURN_HTML = {
    "from": "text/html",
    "to": "text/html; charset=utf-8",
}

# security headers put onto HTTP answers
HEADERS_SND_SEC = (
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "same-origin"),
    ("X-Frame-Options", "SAMEORIGIN"),
    ("Cross-Origin-Resource-Policy", "same-origin"),
    ("Cross-Origin-Opener-Policy", "same-origin-allow-popups"),
)

# directory listing shows html files only
SRV_DIR_VIS = ["html", "htm"]
SRV_DIR_TOP = "\n".join((
    "<!DOCTYPE html>",
    "<html><head>",
    "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">",
    "</head>",
    "<body><pre>",
    "")).encode("utf-8")
SRV_DIR_BTM = "\n".join(("", "</pre></body></html>", "")).encode("utf-8")
