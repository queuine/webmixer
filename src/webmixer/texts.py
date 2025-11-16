#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
Strings that can be freely changed.
"""

from .consts import (
    APPLICATION_NAME,
    PORT_MIN,
    PORT_MAX,
)

APPLICATION_DESC = "personal webserver"

GUI_STAT_MAP = "static mapping"
GUI_NO_STAT_MAP = "no static mapping"
GUI_WEB_PORT = "web serving at port"
GUI_OPEN_WM_WEB = "Open web site of the Webmixer application"
GUI_QUIT_WM = "Quit the Webmixer application"
GUI_CTRL_B_URL = "Ctrl+B copies the whole URL of selected mapping"
GUI_URL_CTRL_CB = "URL   (Ctrl+C,B)"
GUI_DIR_S_CTRL_C = "directory   (Ctrl+Shift+C)"
GUI_DYN_MAP = "dynamic mapping"
GUI_DYN_MAP_PORT = "mapping set at port"
GUI_DYN_MAP_RE = "Restore the dynamic mapping"
GUI_DYN_MAP_CLEAR = "Clear the dynamic mapping"
GUI_NO_SAVE_SESSION = "cannot save current session into session file"

HLP_APP_DESC_L1 = (
    "local-only web server securely providing multiple directories")
HLP_APP_DESC_L2 = (
    "with both static and dynamic setting of the served directories")
HLP_SEE_WEB = "see the " + APPLICATION_NAME + " website"
HLP_DO_VERSION = "write version and exit"
HLP_DO_LICENSE = "write license and exit"
HLP_FILE_STAT_MAP = "file with default directory mapping"
HLP_FILE_DYN_MAP = "file with saved session mapping"
HLP_PORT_SETTING = "port for the setting actions"
HLP_PORT_WEB = "port for web serving"
HLP_PORT_WEB_RND = "use random port for web serving"
HLP_NO_STAT_MAP = "without static mapping"
HLP_NO_DYN_MAP = "without dynamic mapping"
HLP_NO_SESSION = "without saving the dynamic mapping"
HLP_RE_SESSION = "restore the dynamic mapping at startup"
HLP_LOG_WEB_RQ = "whether to log web requests"
HLP_LOG_SET_RQ = "whether to log setting requests"
HLP_VERSION = "version"
HLP_LICENSE = "license"
HLP_NO_RE_SESSION_MAP = (
    "session is not restored when dynamic mapping is not used")
HLP_PORT_SET_WRONG = (
    f"port-setting has to be an integer between {PORT_MIN} and {PORT_MAX}")
HLP_PORT_WEB_WRONG = (
    f"port-serving has to be an integer between {PORT_MIN} and {PORT_MAX}")
HLP_PORTS_NO_SAME = "port-setting and port-serving cannot be the same"
HLP_NO_RE_SESSION_USE = "session is not restored when session is not used"
HLP_NO_SESSION_WRITE = "cannot write to the session file"
HLP_NO_RE_SESSION_WRN_L1 = "session restore is disabled, set session file by"
HLP_NO_RE_SESSION_WRN_L2 = ["or use", "option to disable this warning"]
HLP_NO_RE_SESSION_WRN_L3 = ["or", "to disable dynamic mapping"]
HLP_NO_RE_STATIC_WRN_L1 = "cannot read from the file with static mapping"
HLP_NO_RE_STATIC_WRN_L2 = ["static mapping", "has to be a readable file"]
HLP_NO_RE_STATIC_WRN_L3 = ["use", "option to disable static mapping"]

RUN_NO_SESSION = "cannot read the file with session mapping"
RUN_NO_STATIC = "cannot read the file with static mapping"
RUN_NO_SET_PORT = "cannot start the setting server: port already in use"
RUN_NO_WEB_PORT = "cannot start the serving server: port already in use"

SET_LOG_MSG = "setting"
SET_LOG_ERR = "setting error"
SET_ERR_RQ_LINE = "could not read the request line"
SET_ERR_RQ_PATH = "could not get the requested path"
SET_ERR_PREP_CHG = "could not prepare challenge"
SET_ERR_SEND_READ = "could not send the challenge or read the answer"
SET_ERR_ANSWER = "answer on the challenge was wrong"
SET_ERR_SEND_URL = "could not send the set url"

SRV_MSG_NA = "not allowed at all"
SRV_MSG_NF_MAP = "respective mapping was not found"
SRV_MSG_NF_PATH = "mapped path does not exist"
SRV_MSG_NR_PATH = "mapped path is not readable"

SRV_DIR_DIRS = "Directories"
SRV_DIR_FILES = "Files"
