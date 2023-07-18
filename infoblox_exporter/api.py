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

from typing import Dict, List, Any, Tuple

import urllib3
from infoblox_client import connector

from infoblox_exporter.exceptions import InfobloxException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InfoBlox:
    def __init__(self, config):
        self.master = config.get('master')

        self.opts = {'host': config.get('master'),
                     'username': config.get('username'),
                     'password': config.get('password'),
                     'wapi_version': config.get('wapi_version'),
                     'http_request_timeout': config.get('timeout', 60)}
        self.conn = connector.Connector(self.opts)

    async def get_infoblox_member(self, node_name: str) -> Tuple[List[Any], Dict[str, Any]]:
        # Define search criteria
        node_info_data: Dict[str, Any] = {}
        service_data: List[Any] = []
        search = {'host_name': node_name}
        return_fields_member = ['host_name', 'service_status', 'platform', 'node_info', 'ntp_setting',
                                'extattrs']
        members = self.conn.get_object('member', search, return_fields=return_fields_member)
        if len(members) == 0:
            raise InfobloxException(f"No hit on {node_name}")
        for member in members[0]['node_info']:
            if 'lan_ha_port_setting' in member and 'mgmt_lan' in member['lan_ha_port_setting']:
                # HA setup
                node_info_data[member['lan_ha_port_setting']['mgmt_lan']] = member
            else:
                node_info_data['NO_HA_IP'] = member

        for service in members[0]['service_status']:
            service_data.append(service)

        return service_data, node_info_data

    async def get_infoblox_dhcp_utilization(self, network: str) -> int:
        try:
            return_fields_range = ['network', 'dhcp_utilization', 'dhcp_utilization_status']
            range = self.conn.get_object('range', {'network': network}, return_fields=return_fields_range)
            return range[0]['dhcp_utilization']
        except Exception as err:
            raise InfobloxException("Not a valid network",status=400)


