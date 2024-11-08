#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/26 18:44
# @File    : config.py
# @Software: PyCharm
import os
from pathlib import Path

FILE_HUB_URL = os.environ.get("FILE_HUB_URL", "https://bidding-assistant.staging.hithinksoft.com")

BASEDIR = Path(__file__).absolute().parent.parent
DEFAULT_FILE_PATH = BASEDIR.joinpath("data/temp")
DEFAULT_CACHE_PATH = BASEDIR.joinpath("data/cache")

# if not DEFAULT_FILE_PATH.exists():
#     DEFAULT_FILE_PATH.mkdir(exist_ok=True)

if not DEFAULT_CACHE_PATH.exists():
    DEFAULT_CACHE_PATH.mkdir(exist_ok=True)
