#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
Web server that serves the mapped directories.
"""

import os, pathlib, random, http.server, urllib.parse, html

from .utils import is_hidden, trim_subpath, is_dotted_inner

from .consts import (
    APPLICATION_NAME,
    APPLICATION_VERSION,
    SERVER_DOMAIN,
    SERVER_SERVING_PORT_MIN,
    SERVER_SERVING_PORT_MAX,
    HEADER_RCV_HOST,
    HEADER_RCV_HOST_VAL,
    HEADER_RCV_REFERER,
    HEADER_RCV_REFERER_VAL,
    HEADER_RCV_ORIGIN,
    HEADER_RCV_ORIGIN_VAL,
    HEADER_RCV_SFS,
    HEADER_RCV_SFS_VAL,
    SRV_FT_WITHOUT_REF,
    SRV_SC_OK,
    SRV_SC_NA,
    SRV_SC_NF,
    SRV_SC_REDIRECT,
    HEADER_SND_REDIRECT,
    HEADER_SND_TYPE,
    HEADER_SND_TYPE_DIR,
    HEADER_SND_TYPE_TURN_CMF,
    HEADER_SND_TYPE_TURN_HTML,
    HEADERS_SND_SEC,
    SRV_DIR_VIS,
    SRV_DIR_TOP,
    SRV_DIR_BTM,
)
from .texts import (
    SRV_MSG_NA,
    SRV_MSG_NF_MAP,
    SRV_MSG_NF_PATH,
    SRV_MSG_NR_PATH,
    SRV_DIR_DIRS,
    SRV_DIR_FILES,
)


class ServingRHBase(http.server.BaseHTTPRequestHandler):
    """
    Handler of HTTP requests.
    """
    extensions_map = http.server.SimpleHTTPRequestHandler.extensions_map
    server_version = APPLICATION_NAME + "/" + str(APPLICATION_VERSION)

    def _check_request_allowed(self, requires_referrer):
        host = self.headers.get(HEADER_RCV_HOST, None)
        if host is None:
            return False
        if self.server.envelope.localhost_host.match(host) is None:
            return False
        referrer = self.headers.get(HEADER_RCV_REFERER, None)
        if requires_referrer and (referrer is None):
            return False
        if referrer is not None:
            if self.server.envelope.localhost_referrer.match(referrer) is None:
                return False
        # Chrome consideres some (e.g. JS modules) requests to be CORS
        # even when they are requests within the same domain and port;
        # thus have to send the "Origin" request too;
        # by that, requests with this header filled cannot be immediately
        # discarded, sigh;
        origin = self.headers.get(HEADER_RCV_ORIGIN, None)
        if origin is not None:
            if self.server.envelope.localhost_origin.match(origin) is None:
                return False
            # they at least seem to send this info (on Sec-Fetch-Site)
            # alongside the spurious CORS headers;
            if self.headers.get(HEADER_RCV_SFS, None) != HEADER_RCV_SFS_VAL:
                return False
        return True

    def _unescape_url_path(self):
        return urllib.parse.unquote_plus(self.path)

    def _translate_to_dir(self):
        path = None
        path_to_use = self._unescape_url_path()
        path_to_test = path_to_use
        if not path_to_test.endswith("/"):
            path_to_test += "/"
        envelope = self.server.envelope
        path_start = ""
        path_end = ""
        with envelope.maplock:
            for mapset in [envelope.session, envelope.mapping]:
                for rule in mapset:
                    match = rule["url_re"].match(path_to_test)
                    if match is not None:
                        path_start = rule["dir"]
                        path_end = path_to_use[match.end():]
                        path = path_start + path_end
                        break
                if path is not None:
                    break
        if path is not None:
            if is_hidden(path, trim_subpath(path_end), True, True):
                path = None
        if (path is not None) and path_end:
            if is_dotted_inner(path_end):
                path = None
        return path

    def _escape_html_link(self, link):
        return html.escape(link, True).replace(" ", "%20")

    def _escape_html_name(self, name):
        return html.escape(name, False)

    def _list_directory(self, path):
        dirs = []
        files = []
        if not path.endswith("/"):
            path += "/"
        path_object = pathlib.Path(path)
        base_path = str(path_object)
        base_path_len = len(base_path)
        if not base_path.endswith("/"):
            base_path += "/"
        for item in sorted(path_object.glob("*")):
            rel_path = str(item)[base_path_len:]
            sub_path = trim_subpath(rel_path)
            if not sub_path:
                continue
            if is_hidden(str(item), sub_path, False, item.is_file()):
                continue
            if item.is_dir():
                dirs.append({
                    "rel_path": rel_path,
                    "escaped_link": self._escape_html_link(sub_path) + "/",
                    "escaped_view": self._escape_html_name(sub_path) + "/"})
            if item.is_file():
                name_parts = (
                    rel_path.rsplit("/", maxsplit=1)[-1]
                    .rsplit(".", maxsplit=1))
                if (
                    (len(name_parts) != 2)
                    or (name_parts[-1] not in SRV_DIR_VIS)
                ):
                    continue
                files.append({
                    "rel_path": rel_path,
                    "escaped_link": self._escape_html_link(sub_path),
                    "escaped_view": self._escape_html_name(sub_path)})
        return {"dirs": dirs, "files": files}

    def _redirect_path(self, path):
        self.send_response(SRV_SC_REDIRECT)
        self.send_header(HEADER_SND_REDIRECT, path)
        for header in HEADERS_SND_SEC:
            self.send_header(header[0], header[1])
        self.end_headers()

    def _write_html_dir_list(self, path):
        self.send_response(SRV_SC_OK)
        for header in HEADERS_SND_SEC:
            self.send_header(header[0], header[1])
        self.send_header(HEADER_SND_TYPE, HEADER_SND_TYPE_DIR)
        self.end_headers()
        dir_content = self._list_directory(path)
        self.wfile.write(SRV_DIR_TOP)
        self.wfile.write((SRV_DIR_DIRS + ":\n").encode("utf-8"))
        self.wfile.write("\n".join([
            f"<a href=\"{item['escaped_link']}\">{item['escaped_view']}</a>"
            for item in dir_content["dirs"]
        ]).encode("utf-8"))
        self.wfile.write(("\n" + SRV_DIR_FILES + ":\n").encode("utf-8"))
        self.wfile.write("\n".join([
            f"<a href=\"{item['escaped_link']}\">{item['escaped_view']}</a>"
            for item in dir_content["files"]
        ]).encode("utf-8"))
        self.wfile.write(SRV_DIR_BTM)

    def _write_file_content(self, path):
        mimetype = http.server.SimpleHTTPRequestHandler.guess_type(self, path)
        if (
            (mimetype == HEADER_SND_TYPE_TURN_CMF["from"])
            and (path.endswith(HEADER_SND_TYPE_TURN_CMF["path_end"]))
        ):
            mimetype = HEADER_SND_TYPE_TURN_CMF["to"]
        if mimetype == HEADER_SND_TYPE_TURN_HTML["from"]:
            mimetype = HEADER_SND_TYPE_TURN_HTML["to"]
        self.send_response(SRV_SC_OK)
        for header in HEADERS_SND_SEC:
            self.send_header(header[0], header[1])
        self.send_header(HEADER_SND_TYPE, mimetype)
        self.end_headers()
        with open(path, "rb") as file_hnd:
            self.wfile.write(file_hnd.read())

    def do_GET(self):
        has_to_have_referrer = True
        last_path_part = self.path.split("/")[-1].split(".")
        if (
            (len(last_path_part) > 1)
            and (last_path_part[-1] in SRV_FT_WITHOUT_REF)
        ):
            has_to_have_referrer = False
        if len(last_path_part) == 1:
            has_to_have_referrer = False
        if not self._check_request_allowed(has_to_have_referrer):
            try:
                self.send_error(SRV_SC_NA, SRV_MSG_NA)
            except OSError:
                pass
            return
        path = self._translate_to_dir()
        if not path:
            try:
                self.send_error(SRV_SC_NF, SRV_MSG_NF_MAP)
            except OSError:
                pass
            return
        if not os.path.exists(path):
            try:
                self.send_error(SRV_SC_NF, SRV_MSG_NF_PATH)
            except OSError:
                pass
            return
        if not os.access(path, os.R_OK):
            try:
                self.send_error(SRV_SC_NA, SRV_MSG_NR_PATH)
            except OSError:
                pass
            return
        if os.path.isdir(path):
            try:
                if self.path.endswith("/"):
                    self._write_html_dir_list(path)
                else:
                    self._redirect_path(self.path + "/")
            except (OSError, ValueError):
                pass
        else:
            try:
                self._write_file_content(path)
            except OSError:
                pass


class ServingRHQuiet(ServingRHBase):
    def log_message(self, format, *args):
        return

    def log_request(self, code='-', size='-'):
        return


ServingRH = {
    True: ServingRHBase,
    False: ServingRHQuiet,
}


class ServingServerEnvelope():
    """
    Container with the web server along with linked structures used by it.
    """
    def __init__(self, port, mapping, session, maplock, logging):
        self.mapping = mapping
        self.session = session
        self.maplock = maplock
        self.logging = logging
        self.wx_frame = None
        self.localhost_host = HEADER_RCV_HOST_VAL
        self.localhost_referrer = HEADER_RCV_REFERER_VAL
        self.localhost_origin = HEADER_RCV_ORIGIN_VAL
        self.port = port
        self.server = None
        self.error_occurred = False

    def prepare(self):
        serving_rh_class = ServingRH[self.logging]

        if self.port is not None:
            has_bound = False
            try:
                self.server = http.server.ThreadingHTTPServer(
                    (SERVER_DOMAIN, self.port), serving_rh_class)
                self.server.envelope = self
                has_bound = True
            except OSError:
                has_bound = False
            if has_bound:
                self.server.envelope = self
            elif self.server is not None:
                try:
                    self.server.server_close()
                except OSError:
                    pass
                self.server = None
            return has_bound

        while True:
            self.port = random.randint(
                SERVER_SERVING_PORT_MIN, SERVER_SERVING_PORT_MAX)
            has_bound = False
            try:
                self.server = http.server.ThreadingHTTPServer(
                    (SERVER_DOMAIN, self.port), serving_rh_class)
                has_bound = True
            except OSError:
                has_bound = False
            if has_bound:
                self.server.envelope = self
                break
            if self.server is not None:
                try:
                    self.server.server_close()
                except OSError:
                    pass
                self.server = None
        return True

    def run(self):
        try:
            self.server.serve_forever()
        except OSError:
            self.error_occurred = True
        finally:
            self.server.server_close()


def run_serving_server(serving_envelope):
    serving_envelope.run()


def prepare_serving_server(port, mapping, session, maplock, logging):
    serving_envelope = ServingServerEnvelope(
        port, mapping, session, maplock, logging)
    success = serving_envelope.prepare()
    if success:
        return serving_envelope
    del serving_envelope
    return None
