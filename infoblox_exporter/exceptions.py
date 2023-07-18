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


class InfobloxException(Exception):
    def __init__(self, message: str = "", status: int = 503, exp: Exception = None):
        self.message = message
        self.status = status
        self.exp = exp
