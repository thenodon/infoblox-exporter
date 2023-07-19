# -*- coding: utf-8 -*-
"""
    Copyright (C) 2023 Anders Håål

    This file is part of infoblox_exporter.

    infoblox_exporter is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    infoblox_exporter is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with infoblox_exporter.  If not, see <http://www.gnu.org/licenses/>.

"""

import logging
import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    basic_auth_username: str = os.getenv("BASIC_AUTH_USERNAME")
    basic_auth_password: str = os.getenv("BASIC_AUTH_PASSWORD")
    infoblox = {"master": os.getenv("INFOBLOX_MASTER"),
                "wapi_version": os.getenv("INFOBLOX_WAPI_VERSION"),
                "username": os.getenv("INFOBLOX_USERNAME"),
                "password": os.getenv("INFOBLOX_PASSWORD")}


@lru_cache()
def get_settings() -> BaseSettings:
    logging.info("Loading config settings from the environment...")
    return Settings()
