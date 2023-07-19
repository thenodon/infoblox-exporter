# -*- coding: utf-8 -*-
"""
    Copyright (C) 2021 Redbridge AB

    This file is part of fortigate_exporter.

    fortigate_exporter is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    fortigate_exporter is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with fortigate_exporter.  If not, see <http://www.gnu.org/licenses/>.

"""
from typing import Dict, Any

from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily

from infoblox_exporter.transform import Transform, LabelsBase


class Config:
    prefix = 'infoblox_'
    help_prefix = ''

    class Labels(LabelsBase):
        def __init__(self):
            super().__init__()

    @staticmethod
    def metrics_definition() -> Dict[str, Metric]:
        common_labels = Config.Labels().get_label_keys()

        metric_definition = {
            "up":
                GaugeMetricFamily(name=f"{Config.prefix}up",
                                  documentation=f"{Config.help_prefix}Infoblox API up",
                                  labels=common_labels),
            "scrape_time_seconds":
                GaugeMetricFamily(name=f"{Config.prefix}scrape_time_seconds",
                                  documentation=f"{Config.help_prefix}Infoblox API scrape time",
                                  labels=common_labels),
        }

        return metric_definition


class Status(Config.Labels):
    def __init__(self):
        super().__init__()
        self.up = 0
        self.version_supported = 0
        self.scrape_time_seconds = 0.0


class InfobloxStatus(Transform):

    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.data = data
        self.labels: [Config.Labels] = Config.Labels()
        self.status: Status = Status()

    def metrics(self):

        metrics = Config.metrics_definition()
        for attribute in metrics.keys():
            metrics[attribute].add_metric(self.status.get_label_values(),
                                          self.status.__dict__.get(attribute))

        for m in metrics.values():
            yield m

    def parse(self):

        if 'up' in self.data and self.data['up'] == 1:
            self.status.up = 1

        if 'scrape_time_seconds' in self.data:
            self.status.scrape_time_seconds = self.data['scrape_time_seconds']
