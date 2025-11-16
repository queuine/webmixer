#!/usr/bin/env python
#
# Webmixer: personal webserver.
# Copyright (c) 2023-2025 Martin Saturka
# Released under the MIT license.
#
"""
Loaded gets the startup function of the Webmixer application.
"""

from . import consts
from .run import start

__version__ = consts.APPLICATION_VERSION
__all__ = ['start']
