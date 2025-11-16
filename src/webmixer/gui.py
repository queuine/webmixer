#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
GUI part of the Webmixer application.
"""

import sys, types, subprocess, tempfile, io, base64, webbrowser

from .consts import (
    APPLICATION_NAME,
    SERVER_SETTING_PORT,
    APPLICATION_LINK,
    SERVER_DOMAIN,
)
from .texts import (
    APPLICATION_DESC,
    GUI_STAT_MAP,
    GUI_NO_STAT_MAP,
    GUI_WEB_PORT,
    GUI_OPEN_WM_WEB,
    GUI_QUIT_WM,
    GUI_CTRL_B_URL,
    GUI_URL_CTRL_CB,
    GUI_DIR_S_CTRL_C,
    GUI_DYN_MAP,
    GUI_DYN_MAP_PORT,
    GUI_DYN_MAP_RE,
    GUI_DYN_MAP_CLEAR,
    GUI_NO_SAVE_SESSION,
)

from .utils import shorten_home_dir

try:
    import wx
    if (int(wx.__version__.split(".")[0])) < 4:
        sys.stderr.write("wxPython has to be at major version 4\n")
        sys.exit(1)
except ModuleNotFoundError:
    sys.stderr.write("the wx package has to be installed\n")
    sys.exit(1)

# Base64 of icon in PNG format
ICONDATA = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABmJLR0QA/wD/AP+gvaeTAAAA
CXBIWXMAABDrAAAQ6wFQlOh8AAAAB3RJTUUH5wgGADAC48bCWAAAAv5JREFUWMPtV1tIFFEY
/s7szNpqipritUzCIl8yCqOQwihDQwTDhzUlQm0l6WZopoallmJekK4PXQykm5lkWqCiPRSF
BGFYdDHMdFU02bXUHXd3zulBDN3cdd0Ce9jvbf755/++/zaHA9jxvyExpzErPf9W7L+MGZ/b
ei328J21c70jMx8uXqj0qusJHxTZUniQLw1uCjG9qiD6sy2kl8pPO7wY2RL+XXStHWfujh58
/91HJVuVFgVEZrx885N6hhAwAABPDGPOrO9+fVlE0kLIM7Pz13XSmNvjBnkwhQCAAUxCmM+7
qKKMPU/nFBCf07JdPbmimTLCzXRgkMGJ9Ru9nSfj0ja9bwyNOmQwRxyrqvDhl4Wc6dd5pYCT
YzqRaSqeavtOhjYGRSjzxGnrb7JRvcMNU/KpzyRMEG++e8yvLrdtc2fK8YoNAJCaVzOregmn
mktGHHd0DE76pxBOMCGfSkXiXPxreyL2zrRyAKA621qokfwCzBeVgUEGHXVd/YlFvFbmtFzV
U7kHYyCqgqbwXenPv3VPrMqg3BJPBktRCD6qaVlXo0qYtvEAoNFoOJ55ghHFVL8shKBEjl5x
pUpgE3ExuR1qrU4ezIgg4yDNOxuUEbi5OAmXn+h8AfTMmoGiipvBzwZCqkVJsZ5CZtWwMdMp
tgAOxh/eDn01987tTDa7BV0NyUJm6+5torC8ftTorrAmK8sgABXh66R5qDD2Ha0qVvZaXMOZ
iDlWXz4uBB0QjTInQogN1BScUftho+/QwdIT0W0WJJpH2vn2APWQtnCEBiZMuZrMB6OAyeIw
cJBJGinQbWx/sOLVg8zMLN08NZof2UXVke3Dayr1xDmImZ0PAo6JE85kuP5x6ZF9hLzVW9kk
65BVeF2udwhIbR9YWUnIn5uiYCM90PWHN12J7V5IqzhrHYtzk/SJYVI7M7OmjBq+LpR8QQIA
wCAxsxUjBMSWPeGwyLALsAuwC1h0AbxNR+zf/dVtFyDIFTwZ78ZcpzPHjbrYb1V22IJfwxMZ
9KwQEjEAAAAASUVORK5CYII=
"""


def get_gui_app():
    return wx.App()


class AppFrame(wx.Frame):
    """
    Complete setting of the GUI.
    """
    def __init__(self, properties):
        super().__init__(
            parent=None,
            title=(APPLICATION_NAME + ": " + APPLICATION_DESC)
        )
        self.app_properties = properties
        self.web_port_str = str(self.app_properties["port_serving"])
        self.base_serving_url = "".join((
            "http://", SERVER_DOMAIN, ":", self.web_port_str))

        self.ui = types.SimpleNamespace()
        ui = self.ui

        ui.panel = wx.Panel(self)
        ui.panel_sizer = wx.BoxSizer(wx.VERTICAL)

        ui.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ui.panel_sizer.Add(ui.top_sizer, 0, wx.ALL | wx.EXPAND, 0)

        if self.app_properties["with_static_map"]:
            label_static_mapping_txt = GUI_STAT_MAP + ":"
        else:
            label_static_mapping_txt = GUI_NO_STAT_MAP
        ui.label_static_mapping = wx.StaticText(
            ui.panel, label=label_static_mapping_txt, size=(-1, -1))
        ui.top_sizer.Add(
            ui.label_static_mapping, 0, wx.ALL | wx.EXPAND, 5)

        ui.top_spacer = wx.StaticText(
            ui.panel, label=" ", size=(-1, -1))
        ui.top_sizer.Add(
            ui.top_spacer, 1, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        ui.label_web_port = wx.StaticText(
            ui.panel,
            label=GUI_WEB_PORT + " " + self.web_port_str,
            size=(-1, -1))
        ui.top_sizer.Add(ui.label_web_port, 0, wx.ALL | wx.EXPAND, 5)

        ui.app_link_button = wx.BitmapButton(
            ui.panel,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_TIP),
            size=(32, -1))
        ui.top_sizer.Add(
            ui.app_link_button,
            0,
            wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            1)
        ui.app_link_button.Bind(wx.EVT_BUTTON, self._on_app_link_click)
        ui.app_link_button.SetToolTip(GUI_OPEN_WM_WEB)

        ui.close_button = wx.BitmapButton(
            ui.panel,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_QUIT),
            size=(32, -1))
        ui.top_sizer.Add(
            ui.close_button,
            0,
            wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            0)
        ui.close_button.Bind(wx.EVT_BUTTON, self._on_button_close)
        ui.close_button.SetToolTip(GUI_QUIT_WM)

        ui.list_static = None
        if self.app_properties["with_static_map"]:
            self._setup_static_mapping_ui(ui)

        ui.middle_sizer = None
        ui.label_dynamic_mapping = None
        ui.app_link_label = None
        ui.restore_btn = None
        ui.clear_btn = None
        ui.list_dynamic = None
        if self.app_properties["with_dynamic_map"]:
            self._setup_dynamic_mapping_ui(ui)

        key_ctrl_c_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self._on_ctrl_c, id=key_ctrl_c_id)
        key_ctrl_b_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self._on_ctrl_b, id=key_ctrl_b_id)
        key_ctrl_shift_c_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self._on_ctrl_shift_c, id=key_ctrl_shift_c_id)
        key_ctrl_r_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self._on_ctrl_r, id=key_ctrl_r_id)
        key_ctrl_k_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self._on_ctrl_k, id=key_ctrl_k_id)
        key_ctrl_q_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self._on_ctrl_q, id=key_ctrl_q_id)

        self.ui.accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('C'), key_ctrl_c_id),
            (wx.ACCEL_CTRL, ord('B'), key_ctrl_b_id),
            (wx.ACCEL_SHIFT | wx.ACCEL_CTRL, ord('C'), key_ctrl_shift_c_id),
            (wx.ACCEL_CTRL, ord('R'), key_ctrl_r_id),
            (wx.ACCEL_CTRL, ord('K'), key_ctrl_k_id),
            (wx.ACCEL_CTRL, ord('Q'), key_ctrl_q_id),
        ])
        self.SetAcceleratorTable(self.ui.accel_tbl)

        ui.panel.SetSizerAndFit(ui.panel_sizer)
        ui.sizer = wx.BoxSizer(wx.VERTICAL)
        ui.sizer.Add(ui.panel, 1, wx.ALL | wx.EXPAND | wx.CENTER, 5)
        self.SetSizerAndFit(ui.sizer)

        try:
            image_data = base64.b64decode(ICONDATA)
            image_stream = io.BytesIO(image_data)
            image = wx.Image(image_stream, wx.BITMAP_TYPE_ANY)
            bitmap = wx.Bitmap(image)
            icon = wx.Icon()
            icon.CopyFromBitmap(bitmap)
            self.SetIcon(icon)
        except wx._core.wxAssertionError:
            pass

        self.Bind(wx.EVT_CLOSE, self._on_close)
        screen_width, screen_height = wx.DisplaySize()
        cca_app_size = 480
        app_pos_horiz_default = 100
        app_pos_vert_default = 50
        app_pos_horiz = (
            app_pos_horiz_default
            if (screen_width >= (cca_app_size + 2*app_pos_horiz_default))
            else 0)
        app_pos_vert = (
            app_pos_vert_default
            if (screen_height >= (cca_app_size + 2*app_pos_vert_default))
            else 0)
        self.SetPosition(wx.Point(app_pos_horiz, app_pos_vert))
        self.Show()

    def _setup_static_mapping_ui(self, ui):
        ui.list_static = wx.ListView(
            ui.panel, size=(-1, 120), style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        ui.list_static.Bind(
            wx.EVT_KILL_FOCUS,
            lambda ev: self._on_losing_focus(ui.list_static))
        ui.list_static.Bind(
            wx.EVT_SET_FOCUS,
            lambda ev: self._on_gaining_focus(ui.list_static))
        ui.list_static.Bind(wx.EVT_RIGHT_DOWN, lambda ev: None)
        ui.list_static.Bind(wx.EVT_RIGHT_UP, lambda ev: None)
        ui.list_static.Bind(wx.EVT_RIGHT_DCLICK, lambda ev: None)
        ui.list_static.SetToolTip(GUI_CTRL_B_URL)

        ui.list_static.InsertColumn(0, GUI_URL_CTRL_CB, width=150)
        ui.list_static.InsertColumn(1, GUI_DIR_S_CTRL_C, width=300)
        ui.panel_sizer.Add(
            ui.list_static, 3, wx.ALL | wx.EXPAND | wx.CENTER, 5)

        map_index = 0
        for item in self.app_properties["mapping"]:
            ui.list_static.InsertItem(map_index, item["url"])
            ui.list_static.SetItem(map_index, 1, shorten_home_dir(item["dir"]))
            map_index += 1

    def _setup_dynamic_mapping_ui(self, ui):
        ui.middle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ui.panel_sizer.Add(ui.middle_sizer, 0, wx.ALL | wx.EXPAND, 0)

        ui.label_dynamic_mapping = wx.StaticText(
            ui.panel, label=GUI_DYN_MAP + ":", size=(-1, -1))
        ui.middle_sizer.Add(
            ui.label_dynamic_mapping, 2, wx.ALL | wx.EXPAND, 5)

        ui.app_link_label = wx.StaticText(
            ui.panel,
            label=" " + GUI_DYN_MAP_PORT + " " + str(SERVER_SETTING_PORT),
            size=(-1, -1))
        ui.middle_sizer.Add(
            ui.app_link_label,
            0,
            wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            5)

        ui.restore_btn = wx.BitmapButton(
            ui.panel,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_REDO),
            size=(32, -1))
        ui.middle_sizer.Add(
            ui.restore_btn,
            0,
            wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            1)
        ui.restore_btn.Bind(wx.EVT_BUTTON, self._on_button_restore)
        if (
            (len(self.app_properties["session"]) > 0)
            or (len(self.app_properties["session_restore"]) == 0)
        ):
            ui.restore_btn.Disable()
        ui.restore_btn.SetToolTip(GUI_DYN_MAP_RE)
        ui.clear_btn = wx.BitmapButton(
            ui.panel,
            bitmap=wx.ArtProvider.GetBitmap(wx.ART_CLOSE),
            size=(32, -1))
        ui.middle_sizer.Add(
            ui.clear_btn, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        ui.clear_btn.Bind(wx.EVT_BUTTON, self._on_button_clear)
        if len(self.app_properties["session"]) == 0:
            ui.clear_btn.Disable()
        ui.clear_btn.SetToolTip(GUI_DYN_MAP_CLEAR)

        ui.list_dynamic = wx.ListView(
            ui.panel, size=(-1, 150), style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        ui.list_dynamic.Bind(
            wx.EVT_KILL_FOCUS,
            lambda ev: self._on_losing_focus(ui.list_dynamic))
        ui.list_dynamic.Bind(
            wx.EVT_SET_FOCUS,
            lambda ev: self._on_gaining_focus(ui.list_dynamic))
        ui.list_dynamic.Bind(
            wx.EVT_RIGHT_DOWN, lambda ev: None)
        ui.list_dynamic.Bind(
            wx.EVT_RIGHT_UP, lambda ev: None)
        ui.list_dynamic.Bind(
            wx.EVT_RIGHT_DCLICK, lambda ev: None)
        ui.list_dynamic.SetToolTip(GUI_CTRL_B_URL)

        ui.list_dynamic.InsertColumn(0, GUI_URL_CTRL_CB, width=150)
        ui.list_dynamic.InsertColumn(1, GUI_DIR_S_CTRL_C, width=300)
        ui.panel_sizer.Add(
            ui.list_dynamic, 4, wx.ALL | wx.EXPAND | wx.CENTER, 5)

        with self.app_properties["maplock"]:
            self.app_properties["setting_envelope"].wx_frame = self
            self.app_properties["serving_envelope"].wx_frame = self
            map_index = 0
            for item in self.app_properties["session"]:
                ui.list_dynamic.InsertItem(map_index, item["url"])
                ui.list_dynamic.SetItem(
                    map_index, 1, shorten_home_dir(item["dir"]))
                map_index += 1

    def ask_for_list_update(self):
        """
        Ask to sync the shown list of dynamic mapping.
        """
        wx.CallAfter(self._update_session_list)

    def _update_session_list(self):
        if not self.app_properties["with_dynamic_map"]:
            return
        ui = self.ui
        with self.app_properties["maplock"]:
            map_count = len(self.app_properties["session"])
            if map_count > 0:
                ui.restore_btn.Disable()
                ui.clear_btn.Enable()
            else:
                self.ui.clear_btn.Disable()
            map_index = ui.list_dynamic.GetItemCount()
            if (map_index == 0) and (map_count > 0):
                self.app_properties["session_restore"] = []
            if map_index == map_count:
                return
            for item in self.app_properties["session"][map_index:]:
                self.app_properties["session_restore"].append(item)
                ui.list_dynamic.InsertItem(map_index, item["url"])
                ui.list_dynamic.SetItem(
                    map_index, 1, shorten_home_dir(item["dir"]))
                map_index += 1
            if self.app_properties["session_path"] is not None:
                try:
                    with open(
                        self.app_properties["session_path"],
                        "w",
                        encoding="utf-8"
                    ) as session_fh:
                        for item in self.app_properties["session_restore"]:
                            session_fh.write(item["url"] + "\n")
                            session_fh.write(item["dir"] + "\n\n")
                except (OSError, ValueError):
                    sys.stderr.write(GUI_NO_SAVE_SESSION + "\n")
                    sys.stderr.write(
                        self.app_properties["session_path"] + "\n")

    def _on_app_link_click(self, ev):
        webbrowser.open(APPLICATION_LINK)

    def _on_gaining_focus(self, widget):
        if widget in (self.ui.list_static, self.ui.list_dynamic):
            widget.Select(widget.GetFocusedItem(), True)

    def _on_losing_focus(self, widget):
        if widget in (self.ui.list_static, self.ui.list_dynamic):
            widget.Select(widget.GetFirstSelected(), False)

    def _get_focused_widget(self):
        return wx.Window.FindFocus()

    def _on_ctrl_c(self, ev):
        widget = self._get_focused_widget()
        if widget in (self.ui.list_static, self.ui.list_dynamic):
            self._copy_list_item(widget, 0, False)

    def _on_ctrl_b(self, ev):
        widget = self._get_focused_widget()
        if widget in (self.ui.list_static, self.ui.list_dynamic):
            self._copy_list_item(widget, 0, True)

    def _on_ctrl_shift_c(self, ev):
        widget = self._get_focused_widget()
        if widget in (self.ui.list_static, self.ui.list_dynamic):
            self._copy_list_item(widget, 1)

    def _on_ctrl_r(self, ev):
        if self.app_properties["with_dynamic_map"]:
            self._restore_session()

    def _on_ctrl_k(self, ev):
        if self.app_properties["with_dynamic_map"]:
            self._clear_session()

    def _on_ctrl_q(self, ev):
        self._close_app()

    def _copy_via_wl_copy(self, text):
        try:
            subprocess.run(
                args=[self.app_properties["wl_copy_path"]],
                input=text.encode("utf-8"),
                check=False)
        except subprocess.SubprocessError:
            pass

    def _copy_via_xclip(self, text):
        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(text.encode("utf-8"))
            tmpfile.flush()
            try:
                subprocess.run(
                    args=[self.app_properties["xclip_path"], tmpfile.name],
                    check=False)
            except subprocess.SubprocessError:
                pass

    def _put_to_clipboard(self, text_to_copy, external_copy):
        if text_to_copy and wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text_to_copy))
            wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            if external_copy and self.app_properties["use_wl_copy"]:
                self._copy_via_wl_copy(text_to_copy)
            elif external_copy and self.app_properties["use_xclip"]:
                self._copy_via_xclip(text_to_copy)

    def _copy_list_item(self, widget, column, prepend_server=False):
        text_to_copy = ""
        index = widget.GetFirstSelected()
        if -1 < index:
            text_to_copy = widget.GetItemText(index, column)
            if prepend_server:
                middle_slash = "" if text_to_copy.startswith("/") else "/"
                text_to_copy = "".join((
                    self.base_serving_url, middle_slash, text_to_copy))
        self._put_to_clipboard(text_to_copy, True)

    def _on_button_close(self, ev):
        self._close_app()

    def _on_close(self, ev):
        self._close_app()

    def _close_app(self):
        if self.app_properties["setting_envelope"] is not None:
            try:
                self.app_properties["setting_envelope"].server.shutdown()
            except (OSError, ValueError):
                pass
        if self.app_properties["serving_envelope"] is not None:
            try:
                self.app_properties["serving_envelope"].server.shutdown()
            except (OSError, ValueError):
                pass
        self.Destroy()

    def _on_button_restore(self, ev):
        if not self.app_properties["with_dynamic_map"]:
            return
        self._restore_session()
        self.ui.panel.SetFocus()

    def _restore_session(self):
        if not self.app_properties["with_dynamic_map"]:
            return
        with self.app_properties["maplock"]:
            ui = self.ui
            if len(self.app_properties["session_restore"]) == 0:
                return
            if len(self.app_properties["session"]) > 0:
                return
            ui.restore_btn.Disable()
            ui.clear_btn.Enable()
            map_index = 0
            for item in self.app_properties["session_restore"]:
                self.app_properties["session"].append(item)
                ui.list_dynamic.InsertItem(map_index, item["url"])
                ui.list_dynamic.SetItem(
                    map_index, 1, shorten_home_dir(item["dir"]))
                map_index += 1

    def _on_button_clear(self, ev):
        self._clear_session()
        self.ui.panel.SetFocus()

    def _clear_session(self):
        if not self.app_properties["with_dynamic_map"]:
            return
        with self.app_properties["maplock"]:
            ui = self.ui
            if len(self.app_properties["session_restore"]) > 0:
                self.ui.restore_btn.Enable()
            ui.clear_btn.Disable()
            ui.list_dynamic.DeleteAllItems()
            empty_session = []
            self.app_properties["session"] = empty_session
            self.app_properties["setting_envelope"].session = empty_session
            self.app_properties["serving_envelope"].session = empty_session
