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

import asyncio
import logging
import time
from enum import Enum
from typing import Dict, List

from prometheus_client.metrics_core import Metric
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from infoblox_exporter.api import InfoBlox
from infoblox_exporter.exceptions import InfobloxException
from infoblox_exporter.infoblox_status import InfobloxStatus
from infoblox_exporter.node_info import NodeInfo
from infoblox_exporter.dhcp_utilization import DHCPUtilization

disable_warnings(InsecureRequestWarning)


class Modules(Enum):
    MEMBER_SERVICES = 'member_services'
    DHCP_UTILIZATION = 'dhcp_utilization'


def to_list(metric_generator):
    metrics = []
    for metric in metric_generator:
        if metric.samples:
            # Only append if the metric has a list of Samples
            metrics.append(metric)
    return metrics


class InfobloxCollector:
    def __init__(self, connection: Dict[str, str], target: str, module: str = Modules.MEMBER_SERVICES.value):
        self.target = target
        self.module = module
        self.connector = InfoBlox(connection)

    async def collect(self):
        start = time.perf_counter()
        all_module_metrics = []
        status = {"up": 1}
        try:
            all_tasks = []

            if self.module == Modules.MEMBER_SERVICES.value:
                all_tasks.append(asyncio.create_task(self._collect_node_info()))
            elif self.module == Modules.DHCP_UTILIZATION.value:
                all_tasks.append(asyncio.create_task(self._collect_dhcp_ranges()))
            else:
                raise InfobloxException(message=f"Not a valid module {self.module}", status=400)

            await asyncio.gather(*all_tasks)
            for task in all_tasks:
                all_module_metrics.extend(task.result())

        except InfobloxException as err:
            status['up'] = 0
            logging.error(f"Request to exporter",
                          extra={'target': self.target, 'error': err.message, 'status': err.status})
        except Exception as err:
            status['up'] = 0
            logging.error(f"Logic error to error", extra={'target': self.target, 'error': err})

        end = time.perf_counter()
        status['scrape_time_seconds'] = end - start
        transformer = InfobloxStatus(status)
        transformer.parse()
        all_module_metrics.extend(to_list(transformer.metrics()))

        return all_module_metrics

    async def _collect_node_info(self) -> List[Metric]:

        metrics = []
        service_data, node_info_data = await self.connector.get_infoblox_member(self.target)

        transformer = NodeInfo(service_data, node_info_data)
        transformer.parse()
        metrics.extend(to_list(transformer.metrics()))
        return metrics

    async def _collect_dhcp_ranges(self) -> List[Metric]:

        metrics = []

        utilization = await self.connector.get_infoblox_dhcp_utilization(self.target)

        transformer = DHCPUtilization(self.target, utilization)
        transformer.parse()
        metrics.extend(to_list(transformer.metrics()))
        return metrics
