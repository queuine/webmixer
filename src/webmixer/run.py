#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
Starting of the Webmixer application.
"""

import os, sys, argparse, shutil, threading

from .utils import (
    is_win_form,
    is_linux_like,
    normalize_path,
    take_mapping,
)
from .server_set import (
    prepare_setting_server,
    remove_setting_server,
    run_setting_server,
)
from .server_web import (
    prepare_serving_server,
    run_serving_server,
)
from .gui import AppFrame, get_gui_app

from .consts import (
    APPLICATION_NAME,
    APPLICATION_LINK,
    APPLICATION_LICENSE,
    APPLICATION_VERSION,
    PORT_MIN,
    PORT_MAX,
    SERVER_SETTING_PORT,
    SERVER_SERVING_PORT,
    LOGGING_WEB_DEFAULT,
    LOGGING_SET_DEFAULT,
    MAPPING_STATIC,
    MAPPING_STATIC_WIN,
    MAPPING_SESSION,
    MAPPING_SESSION_WIN,
)
from .texts import (
    HLP_APP_DESC_L1,
    HLP_APP_DESC_L2,
    HLP_SEE_WEB,
    HLP_DO_VERSION,
    HLP_DO_LICENSE,
    HLP_FILE_STAT_MAP,
    HLP_FILE_DYN_MAP,
    HLP_PORT_SETTING,
    HLP_PORT_WEB,
    HLP_PORT_WEB_RND,
    HLP_NO_STAT_MAP,
    HLP_NO_DYN_MAP,
    HLP_NO_SESSION,
    HLP_RE_SESSION,
    HLP_LOG_WEB_RQ,
    HLP_LOG_SET_RQ,
    HLP_VERSION,
    HLP_LICENSE,
    HLP_NO_RE_SESSION_MAP,
    HLP_PORT_SET_WRONG,
    HLP_PORT_WEB_WRONG,
    HLP_PORTS_NO_SAME,
    HLP_NO_RE_SESSION_USE,
    HLP_NO_SESSION_WRITE,
    HLP_NO_RE_SESSION_WRN_L1,
    HLP_NO_RE_SESSION_WRN_L2,
    HLP_NO_RE_SESSION_WRN_L3,
    HLP_NO_RE_STATIC_WRN_L1,
    HLP_NO_RE_STATIC_WRN_L2,
    HLP_NO_RE_STATIC_WRN_L3,
    RUN_NO_SESSION,
    RUN_NO_STATIC,
    RUN_NO_SET_PORT,
    RUN_NO_WEB_PORT,
)


class HelpArgFormat(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    pass


def take_parameters():
    """
    Read the arguments.
    """
    params = {
        "mapping_path": (
            MAPPING_STATIC_WIN if is_win_form() else MAPPING_STATIC),
        "session_path": (
            MAPPING_SESSION_WIN if is_win_form() else MAPPING_SESSION),
        "port_setting": SERVER_SETTING_PORT,
        "port_serving": SERVER_SERVING_PORT,
        "with_static_map": True,
        "with_dynamic_map": True,
        "with_session": True,
        "logging_web": LOGGING_WEB_DEFAULT,
        "logging_map": LOGGING_SET_DEFAULT,
    }
    help_desc = "\n".join([
        "".join((APPLICATION_NAME, ": ", HLP_APP_DESC_L1, ",")),
        "".join((((len(APPLICATION_NAME) + 2) * " "), HLP_APP_DESC_L2)),
    ])
    parser = argparse.ArgumentParser(
        description=help_desc,
        epilog="".join((HLP_SEE_WEB, ":\n", APPLICATION_LINK)),
        formatter_class=HelpArgFormat
    )
    parser.add_argument(
        "--version", help=HLP_DO_VERSION, action="store_true")
    parser.add_argument(
        "--license", help=HLP_DO_LICENSE, action="store_true")
    parser.add_argument(
        "--mapping-path",
        help=HLP_FILE_STAT_MAP,
        default=params["mapping_path"])
    parser.add_argument(
        "--session-path",
        help=HLP_FILE_DYN_MAP,
        default=params["session_path"])
    parser.add_argument(
        "--port-setting",
        help=HLP_PORT_SETTING,
        type=int,
        default=SERVER_SETTING_PORT)
    parser.add_argument(
        "--port-serving",
        help=HLP_PORT_WEB,
        type=int,
        default=SERVER_SERVING_PORT)
    parser.add_argument(
        "--port-serving-random",
        help=HLP_PORT_WEB_RND,
        action="store_true")
    parser.add_argument(
        "--no-static-mapping", help=HLP_NO_STAT_MAP, action="store_true")
    parser.add_argument(
        "--no-dynamic-mapping", help=HLP_NO_DYN_MAP, action="store_true")
    parser.add_argument(
        "--no-session", help=HLP_NO_SESSION, action="store_true")
    parser.add_argument(
        "--restore-session", help=HLP_RE_SESSION, action="store_true")
    parser.add_argument(
        "--log-web",
        help=HLP_LOG_WEB_RQ,
        action="store_true",
        default=LOGGING_WEB_DEFAULT)
    parser.add_argument(
        "--log-set",
        help=HLP_LOG_SET_RQ,
        action="store_true",
        default=LOGGING_SET_DEFAULT)
    args = parser.parse_args()
    to_end = False
    if args.version:
        sys.stderr.write(HLP_VERSION + ": " + APPLICATION_VERSION + "\n")
        to_end = True
    if args.license:
        sys.stderr.write(HLP_LICENSE + ": " + APPLICATION_LICENSE + "\n")
        to_end = True
    if to_end:
        sys.exit(0)
    params["logging_web"] = args.log_web
    params["logging_map"] = args.log_set
    params["restore_session"] = args.restore_session
    if args.no_static_mapping:
        params["with_static_map"] = False
        params["mapping_path"] = None
    if args.no_dynamic_mapping:
        params["with_dynamic_map"] = False
        params["port_setting"] = None
        params["session_path"] = None
        params["with_session"] = False
        params["restore_session"] = False
        if args.restore_session:
            sys.stderr.write(HLP_NO_RE_SESSION_MAP + "\n")
    if params["with_dynamic_map"] and args.port_setting:
        if ((args.port_setting < PORT_MIN) or (args.port_setting > PORT_MAX)):
            sys.stderr.write(HLP_PORT_SET_WRONG + "\n")
            to_end = True
        else:
            params["port_setting"] = args.port_setting
    if args.port_serving:
        if ((args.port_serving < PORT_MIN) or (args.port_serving > PORT_MAX)):
            sys.stderr.write(HLP_PORT_WEB_WRONG + "\n")
            to_end = True
        else:
            params["port_serving"] = args.port_serving
    if args.port_serving_random:
        params["port_serving"] = None
    if (
        params["with_dynamic_map"] and (params["port_serving"] is not None)
        and (params["port_setting"] == params["port_serving"])
    ):
        sys.stderr.write(HLP_PORTS_NO_SAME + "\n")
        to_end = True
    if to_end:
        sys.exit(2)
    if params["with_dynamic_map"]:
        params["with_session"] = not args.no_session
        if not params["with_session"]:
            params["session_path"] = None
            params["restore_session"] = False
            if args.restore_session:
                sys.stderr.write(HLP_NO_RE_SESSION_USE + "\n")
    if params["with_dynamic_map"] and params["with_session"]:
        norm_session_path = normalize_path(args.session_path)
        session_path_dir = os.path.dirname(norm_session_path)
        try:
            if not os.path.exists(session_path_dir):
                os.makedirs(session_path_dir, mode=0o700, exist_ok=True)
        except (OSError, ValueError):
            pass
        can_write_session = False
        try:
            with open(norm_session_path, "a", encoding="utf-8"):
                can_write_session = True
        except (OSError, ValueError):
            can_write_session = False
        params["session_path"] = (
            norm_session_path if can_write_session else None)
        if params["session_path"] is None:
            params["restore_session"] = False
            sys.stderr.write(HLP_NO_SESSION_WRITE + ":\n")
            sys.stderr.write(args.session_path + "\n")
            sys.stderr.write(HLP_NO_RE_SESSION_WRN_L1 + " --session-path\n")
            sys.stderr.write("".join((
                HLP_NO_RE_SESSION_WRN_L2[0],
                " '--no-session' ",
                HLP_NO_RE_SESSION_WRN_L2[1],
                "\n")))
            sys.stderr.write("".join((
                HLP_NO_RE_SESSION_WRN_L3[0],
                " '--no-dynamic-mapping' ",
                HLP_NO_RE_SESSION_WRN_L3[1],
                "\n")))
    if params["with_static_map"]:
        norm_mapping_path = normalize_path(args.mapping_path)
        if (
            (not os.path.exists(norm_mapping_path))
            or (not os.path.isfile(norm_mapping_path))
            or (not os.access(norm_mapping_path, os.R_OK))
        ):
            sys.stderr.write(HLP_NO_RE_STATIC_WRN_L1 + ":\n")
            sys.stderr.write(args.mapping_path + "\n")
            sys.stderr.write("".join((
                HLP_NO_RE_STATIC_WRN_L2[0],
                " '--mapping-path' ",
                HLP_NO_RE_STATIC_WRN_L2[1],
                "\n")))
            sys.stderr.write("".join((
                HLP_NO_RE_STATIC_WRN_L3[0],
                " '--no-static-mapping' ",
                HLP_NO_RE_STATIC_WRN_L3[1],
                "\n")))
            to_end = True
        else:
            params["mapping_path"] = norm_mapping_path
    if to_end:
        sys.exit(2)
    return params


def start():
    """
    Start the app.
    """
    params = take_parameters()
    session = []
    session_restore = []
    if params["session_path"] is not None:
        last_session = None
        try:
            last_session = take_mapping(params["session_path"], True)
        except (OSError, ValueError):
            last_session = None
            sys.stderr.write("".join((
                RUN_NO_SESSION, ":\n", params['session_path'], "\n")))
        if last_session is not None:
            session_restore = last_session
            if params["restore_session"]:
                session = [item for item in last_session]
    mapping = []
    if params["mapping_path"] is not None:
        try:
            mapping = take_mapping(params["mapping_path"], False)
        except (OSError, ValueError):
            sys.stderr.write("".join((
                RUN_NO_STATIC, ":\n", params['mapping_path'], "\n")))
            sys.exit(3)
    maplock = threading.Condition()
    setting_envelope = None
    if params["with_dynamic_map"]:
        setting_envelope = prepare_setting_server(
            params["port_setting"],
            mapping,
            session,
            maplock,
            params["logging_map"])
        if setting_envelope is None:
            sys.stderr.write(RUN_NO_SET_PORT + "\n")
            sys.exit(3)
    serving_envelope = prepare_serving_server(
        params["port_serving"],
        mapping,
        session,
        maplock,
        params["logging_web"])
    if serving_envelope is None:
        remove_setting_server(setting_envelope)
        sys.stderr.write(RUN_NO_WEB_PORT + "\n")
        sys.exit(3)
    setting_thread = None
    if setting_envelope is not None:
        setting_envelope.port_web = serving_envelope.port
        setting_thread = threading.Thread(
            target=run_setting_server, args=(setting_envelope,))
        setting_thread.daemon = True
        setting_thread.block_on_close = False
        setting_thread.start()
    serving_thread = threading.Thread(
        target=run_serving_server, args=(serving_envelope,))
    serving_thread.daemon = True
    serving_thread.block_on_close = False
    serving_thread.start()
    use_wl_copy = False
    use_xclip = False
    wl_copy_path = None
    xclip_path = None
    if is_linux_like():
        wl_copy_path = shutil.which("wl-copy")
        xclip_path = shutil.which("xclip")
        if wl_copy_path:
            use_wl_copy = True
        elif xclip_path:
            use_xclip = True
    app = get_gui_app()
    properties = {
        "mapping_path": params["mapping_path"],
        "session_path": params["session_path"],
        "mapping": mapping,
        "session": session,
        "session_restore": session_restore,
        "maplock": maplock,
        "with_static_map": params["with_static_map"],
        "with_dynamic_map": params["with_dynamic_map"],
        "setting_envelope": setting_envelope,
        "serving_envelope": serving_envelope,
        "port_setting": params["port_setting"],
        "port_serving": serving_envelope.port,
        "setting_thread": setting_thread,
        "serving_thread": serving_thread,
        "use_wl_copy": use_wl_copy,
        "use_xclip": use_xclip,
        "wl_copy_path": wl_copy_path,
        "xclip_path": xclip_path,
    }
    frame = AppFrame(properties)
    app.SetTopWindow(frame)
    app.MainLoop()
