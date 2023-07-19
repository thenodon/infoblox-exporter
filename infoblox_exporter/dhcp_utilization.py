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

from prometheus_client.core import GaugeMetricFamily

from infoblox_exporter.transform import Transform


class DHCPUtilization(Transform):
    prefix = "infoblox_"

    def __init__(self, network: str, utilization: int):
        super().__init__()
        self.network = network
        self.utilization = utilization

    def metrics(self):
        metrics = {}
        try:
            metrics['dhcp_utilization'] = \
                GaugeMetricFamily(name=f"{DHCPUtilization.prefix}dhcp_utilization_ratio",
                                  documentation=f"DHCP utilization ratio",
                                  labels=['network'])
            metrics['dhcp_utilization'].add_metric([self.network], float(self.utilization)/1000)
        except Exception as err:
            logging.error("Could not create metrics", extra={'metrics': 'dhcp_utilization', 'error': err})

        for m in metrics.values():
            yield m

    def parse(self):
        pass
