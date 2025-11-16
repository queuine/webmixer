#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
The server that provides dynamic mapping.
"""

import os, sys, re, random, tempfile, socketserver, time, unicodedata

from .utils import is_hidden, trim_subpath, is_dotted_inner

from .consts import (
    SERVER_DOMAIN,
    SERVER_SETTING_TIMEOUT,
    RANDOM_STRING_LENGTH,
    HEXDIGITS,
    SET_MAP_DIR,
    SET_MAP_CHG,
    SET_MAP_ANS,
    SET_MAP_201_SC,
    SET_MAP_201,
    SET_MAP_400_SC,
    SET_MAP_400,
    SET_MAP_401_SC,
    SET_MAP_401,
    SET_MAP_500_SC,
    SET_MAP_500,
)
from .texts import (
    SET_LOG_MSG,
    SET_LOG_ERR,
    SET_ERR_RQ_LINE,
    SET_ERR_RQ_PATH,
    SET_ERR_PREP_CHG,
    SET_ERR_SEND_READ,
    SET_ERR_ANSWER,
    SET_ERR_SEND_URL,
)


class SettingRH(socketserver.BaseRequestHandler):
    """
    Handler of requests to set mapping dynamically.
    """
    def _generate_random_string(self):
        return "".join(
            [random.choice(HEXDIGITS) for ind in range(RANDOM_STRING_LENGTH)])

    def _check_can_descend(self, dir_check, dir_end):
        if is_hidden(dir_check, trim_subpath(dir_end), True, False):
            return False
        if is_dotted_inner(dir_end):
            return False
        return True

    def _update_setting(self, dir_check):
        envelope = self.server.envelope
        if not dir_check.endswith("/"):
            dir_check += "/"
        dir_check_re = re.compile(re.escape(dir_check))
        present_link = None
        generated_item = None
        with envelope.maplock:
            for mapset in [envelope.session, envelope.mapping]:
                for rule in mapset:
                    match = rule["dir_re"].match(dir_check)
                    if match is not None:
                        dir_end = dir_check[match.end():]
                        if not trim_subpath(dir_end):
                            present_link = rule["url"]
                            break
                        if self._check_can_descend(dir_check, dir_end):
                            if (
                                (not rule["url"].endswith("/"))
                                and (not dir_end.startswith("/"))
                            ):
                                dir_end = "/" + dir_end
                            elif (
                                (rule["url"].endswith("/"))
                                and (dir_end.startswith("/"))
                            ):
                                dir_end = dir_end.lstrip("/")
                            present_link = rule["url"] + dir_end
                            break
                if present_link is not None:
                    break
            if present_link is not None:
                return {"url": present_link, "is_new": False}

            while True:
                test_url_dir = "/" + self._generate_random_string() + "/"
                test_url_dir_re = re.compile(re.escape(test_url_dir))
                test_passed = True
                for item in envelope.session:
                    if (
                        item["url_re"].match(test_url_dir)
                        or test_url_dir_re.match(item["url"])
                    ):
                        test_passed = False
                        break
                if test_passed:
                    for item in envelope.mapping:
                        if test_url_dir_re.match(item["url"]):
                            test_passed = False
                            break
                if test_passed:
                    generated_item = {
                        "url": test_url_dir,
                        "url_re": test_url_dir_re,
                        "dir": dir_check,
                        "dir_re": dir_check_re,
                    }
                    envelope.session.append(generated_item)
                    break
        return {"url": generated_item["url"], "is_new": True}

    def _check_challenge(self, challenge, challenge_answer):
        answer_lines = challenge_answer.splitlines()
        if len(answer_lines) < 2:
            return False
        if answer_lines[0].upper().strip() != SET_MAP_ANS:
            return False
        answer = answer_lines[1].strip()
        if answer != challenge["challenge_answer_expected"]:
            return False
        return True

    def _prepare_challenge(self):
        challenge = self._generate_random_string()
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            self.challenge_file_path = fh.name
            fh.write((challenge + "\r\n").encode("utf-8"))
        return {
            "challenge_question": self.challenge_file_path,
            "challenge_answer_expected": challenge,
        }

    def _remove_challenge(self):
        if self.challenge_file_path is None:
            return
        try:
            os.remove(self.challenge_file_path)
        except OSError:
            pass
        self.challenge_file_path = None

    def _parse_mapping_request(self, mapping_request):
        req_lines = mapping_request.splitlines()
        if len(req_lines) < 2:
            return None
        if req_lines[0].upper().strip() != SET_MAP_DIR:
            return None
        req_path = req_lines[1].strip()
        if not req_path:
            return None
        if (not os.path.exists(req_path)) or (not os.path.isdir(req_path)):
            return None
        if not os.access(req_path, os.R_OK):
            return None
        return req_path

    def setup(self):
        self.challenge_file_path = None
        self.status_code = None
        self.request_lines = ""
        self.error_messages = []
        self.to_do_logging = self.server.to_do_logging

    def _sanitize_message(self, message):
        message = message.replace("\t", "    ")
        return "".join(
            ch for ch in message if unicodedata.category(ch)[0] != "C")

    def finish(self):
        self._remove_challenge()
        if self.to_do_logging:
            request_lines = self.request_lines.splitlines()
            request_start = self._sanitize_message(
                request_lines[0] if (len(request_lines) > 0) else "")
            request_dir = self._sanitize_message(
                request_lines[1] if (len(request_lines) > 1) else "")
            try:
                sys.stderr.write("".join((
                    SET_LOG_MSG,
                    " - - - [",
                    time.strftime("%d/%b/%Y %H:%M:%S", time.localtime()),
                    "] \"",
                    request_start,
                    "\" ",
                    str(self.status_code),
                    " - ")))
                sys.stderr.write(request_dir + "\n")
                for message in self.error_messages:
                    sys.stderr.write(SET_LOG_ERR + ": " + message + "\n")
            except (OSError, ValueError):
                pass

    def handle(self):
        self.request.setblocking(True)
        self.request.settimeout(SERVER_SETTING_TIMEOUT)
        try:
            mapping_request = str(self.request.recv(4096), "utf-8")
        except (OSError, ValueError):
            self.error_messages.append(SET_ERR_RQ_LINE)
            return
        self.request_lines = mapping_request
        asked_path = self._parse_mapping_request(mapping_request)
        if asked_path is None:
            self.status_code = SET_MAP_400_SC
            self.error_messages.append(SET_ERR_RQ_PATH)
            try:
                self.request.sendall((SET_MAP_400 + "\r\n").encode("utf-8"))
            except (OSError, ValueError):
                pass
            return
        challenge = self._prepare_challenge()
        if challenge is None:
            self.status_code = SET_MAP_500_SC
            self.error_messages.append(SET_ERR_PREP_CHG)
            try:
                self.request.sendall((SET_MAP_500 + "\r\n").encode("utf-8"))
            except (OSError, ValueError):
                pass
            return
        error_occurred = False
        try:
            self.request.sendall("".join((
                SET_MAP_CHG,
                "\r\n",
                challenge["challenge_question"],
                "\r\n")).encode("utf-8"))
            challenge_answer = str(self.request.recv(4096), "utf-8")
        except (OSError, ValueError):
            error_occurred = True
            self.error_messages.append(SET_ERR_SEND_READ)
        if error_occurred:
            return
        if not self._check_challenge(challenge, challenge_answer):
            self.status_code = SET_MAP_401_SC
            self.error_messages.append(SET_ERR_ANSWER)
            try:
                self.request.sendall((SET_MAP_401 + "\r\n").encode("utf-8"))
            except (OSError, ValueError):
                pass
        else:
            item = self._update_setting(asked_path)
            if item["is_new"] and (self.server.envelope.wx_frame is not None):
                self.server.envelope.wx_frame.ask_for_list_update()
            self.status_code = SET_MAP_201_SC
            try:
                port_web = str(self.server.envelope.port_web)
                self.request.sendall("".join((
                    SET_MAP_201,
                    "\r\n",
                    "http://",
                    SERVER_DOMAIN,
                    ":",
                    port_web,
                    item["url"],
                    "\r\n")).encode("utf-8"))
            except (OSError, ValueError):
                self.error_messages.append(SET_ERR_SEND_URL)


class SettingServerEnvelope():
    """
    Container with the mapping server along with linked structures used by it.
    """
    def __init__(self, port, mapping, session, maplock, logging):
        self.mapping = mapping
        self.session = session
        self.maplock = maplock
        self.logging = logging
        self.wx_frame = None
        self.port = port
        self.port_web = 0
        self.server = None
        self.error_occurred = False

    def prepare(self):
        try:
            self.server = socketserver.ThreadingTCPServer(
                (SERVER_DOMAIN, self.port), SettingRH, False)
            self.server.to_do_logging = self.logging
            self.server.allow_reuse_address = True
            self.server.server_bind()
            self.server.server_activate()
            self.server.envelope = self
        except OSError:
            self.error_occurred = True
        if self.error_occurred:
            if self.server is not None:
                try:
                    self.server.server_close()
                except OSError:
                    pass
                self.server = None
        return not self.error_occurred

    def run(self):
        if self.error_occurred:
            return
        try:
            self.server.serve_forever()
        except OSError:
            self.error_occurred = True
        finally:
            self.server.server_close()


def run_setting_server(setting_envelope):
    setting_envelope.run()


def remove_setting_server(setting_envelope):
    if setting_envelope.server is not None:
        try:
            setting_envelope.server.server_close()
        except OSError:
            pass
    del setting_envelope


def prepare_setting_server(port, mapping, session, maplock, logging):
    setting_envelope = SettingServerEnvelope(
        port, mapping, session, maplock, logging)
    success = setting_envelope.prepare()
    if success:
        return setting_envelope
    del setting_envelope
    return None
