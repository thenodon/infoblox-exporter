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

from typing import Dict, Any, List
from prometheus_client.core import GaugeMetricFamily
from infoblox_exporter.transform import Transform
import logging


class Service:
    def __init__(self, name, value):
        self.metric_name: str = name
        self.metrics_value: float = value
        self.labels: Dict[str: str] = {}


class NodeHWInfo(Service):
    def __init__(self, name='info', value=1.0):
        super().__init__(name, value)


class NodeService(Service):
    def __init__(self, node_ip, name, value):
        super().__init__(name, value)
        self.node_ip: str = node_ip
        self.identity: str = None


class NodeInfo(Transform):
    node_service_prefix = "infoblox_node_service_status_"
    service_prefix = "infoblox_service_status_"
    node_hw_info_prefix = "infoblox_node_"

    def __init__(self, service_data: List[Any], node_info_data: Dict[str, Any]):
        super().__init__()
        self.service_data = service_data
        self.node_info_data = node_info_data
        self.services: List[Service] = []
        self.node_services: List[NodeService] = []
        self.node_hw_info: List[NodeHWInfo] = []

    def metrics(self):
        metrics = {}

        try:
            for service in self.node_services:
                if service.identity:
                    if service.metric_name not in metrics:
                        metrics[service.metric_name] = \
                            GaugeMetricFamily(name=f"{NodeInfo.node_service_prefix}{service.metric_name}",
                                              documentation=f"Node service {service.metric_name} 1=WORKING, 0=FAILED, 2=UNKNOWN",
                                              labels=['identity', 'node_ip'])
                    metrics[service.metric_name].add_metric([service.identity, service.node_ip], service.metrics_value)
                else:
                    if service.metric_name not in metrics:
                        metrics[service.metric_name] = \
                            GaugeMetricFamily(name=f"{NodeInfo.node_service_prefix}{service.metric_name}",
                                              documentation=f"Node service {service.metric_name} 1=WORKING, 0=FAILED, 2=UNKNOWN",
                                              labels=['node_ip'])
                metrics[service.metric_name].add_metric([service.node_ip], service.metrics_value)
        except Exception as err:
            logging.error("Could not create metrics", extra={'metrics': 'node_services', 'error': err})

        try:
            for service in self.services:
                metrics[service.metric_name] = \
                    GaugeMetricFamily(name=f"{NodeInfo.service_prefix}{service.metric_name}",
                                      documentation=f"Service {service.metric_name} 1=WORKING, 0=FAILED, 2=UNKNOWN",
                                      labels=[])
                metrics[service.metric_name].add_metric([], service.metrics_value)
        except Exception as err:
            logging.error("Could not create metrics", extra={'metrics': 'services', 'error': err})

        try:
            for service in self.node_hw_info:
                if service.metric_name not in metrics:
                    metrics[service.metric_name] = \
                        GaugeMetricFamily(name=f"{NodeInfo.node_hw_info_prefix}{service.metric_name}",
                                          documentation=f"Node info {service.metric_name}",
                                          labels=list(service.labels.keys()))
                metrics[service.metric_name].add_metric(list(service.labels.values()), service.metrics_value)
        except Exception as err:
            logging.error("Could not create metrics", extra={'metrics': 'node_hw_info', 'error': err})

        for m in metrics.values():
            yield m

    def parse(self):
        for node_ip, member in self.node_info_data.items():
            info = NodeHWInfo()
            info.labels['ha_status'] = member['ha_status']
            info.labels['hwid'] = member['hwid']
            info.labels['hwtype'] = member['hwtype']
            info.labels['platform'] = member['hwplatform']
            info.labels['node_ip'] = node_ip
            self.node_hw_info.append(info)

            for service_data in member['service_status']:
                if service_data['status'] != 'INACTIVE':
                    service_name, identity = parse_service_name(service_data['service'])
                    service = NodeService(node_ip, service_name, get_status(service_data['status']))
                    if identity:
                        service.identity = identity
                    self.node_services.append(service)

        for member in self.service_data:
            if member['status'] != 'INACTIVE':
                service_name, identity = parse_service_name(member['service'])
                service = Service(service_name, get_status(member['status']))
                self.services.append(service)


def get_status(status: str) -> float:
    if status == 'WORKING':
        return 1.0
    if status == 'UNKNOWN':
        return 2.0
    return 0.0


def parse_service_name(name: str):
    new_name: str = ''
    identity = None
    for element in name:
        if element.isdigit():
            identity = element
        else:
            new_name = f"{new_name}{element}"
    return new_name.lower(), identity
