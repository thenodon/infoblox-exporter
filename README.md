infoblox-exporter
----------------------

> This project is DISCONTINUED, please use [go-infoblox-exporter](https://github.com/thenodon/go-infoblox-exporter) instead

The infoblox-exporter collect metrics from an infoblox master.
Currently, two types of metrics is supported:
- Member service and member node service managed by the master.
- DHCP utilization based on networks

# Metrics
## Members 
Service, member or nodes, are reported as a gauge state 1=WORKING, 0=FAILED, 2=UNKNOWN. 
Any services in the INACTIVE state are not included. 
For node services the label `node_ip` is added. If the node is part of a HA setup the value is an
ip address, if not the value is `NO_HA_IP`.

Example output for a member that have HA setup:
```commandline
# HELP infoblox_node_service_status_node_status Node service node_status 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_node_status gauge
infoblox_node_service_status_node_status{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_node_status{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_disk_usage Node service disk_usage 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_disk_usage gauge
infoblox_node_service_status_disk_usage{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_disk_usage{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_enet_lan Node service enet_lan 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_enet_lan gauge
infoblox_node_service_status_enet_lan{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_enet_lan{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_enet_ha Node service enet_ha 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_enet_ha gauge
infoblox_node_service_status_enet_ha{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_enet_ha{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_enet_mgmt Node service enet_mgmt 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_enet_mgmt gauge
infoblox_node_service_status_enet_mgmt{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_enet_mgmt{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_replication Node service replication 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_replication gauge
infoblox_node_service_status_replication{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_replication{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_db_object Node service db_object 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_db_object gauge
infoblox_node_service_status_db_object{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_db_object{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_fan Node service fan 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_fan gauge
infoblox_node_service_status_fan{identity="1",node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_fan{identity="10.99.0.141"} 1.0
infoblox_node_service_status_fan{identity="2",node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_fan{identity="10.99.0.141"} 1.0
infoblox_node_service_status_fan{identity="3",node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_fan{identity="10.99.0.141"} 1.0
infoblox_node_service_status_fan{identity="1",node_ip="10.99.0.142"} 1.0
infoblox_node_service_status_fan{identity="10.99.0.142"} 1.0
infoblox_node_service_status_fan{identity="2",node_ip="10.99.0.142"} 1.0
infoblox_node_service_status_fan{identity="10.99.0.142"} 1.0
infoblox_node_service_status_fan{identity="3",node_ip="10.99.0.142"} 1.0
infoblox_node_service_status_fan{identity="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_power_supply Node service power_supply 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_power_supply gauge
infoblox_node_service_status_power_supply{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_power_supply{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_ntp_sync Node service ntp_sync 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_ntp_sync gauge
infoblox_node_service_status_ntp_sync{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_ntp_sync{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_cpu_temp Node service cpu_temp 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_cpu_temp gauge
infoblox_node_service_status_cpu_temp{identity="1",node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_cpu_temp{identity="10.99.0.141"} 1.0
infoblox_node_service_status_cpu_temp{identity="1",node_ip="10.99.0.142"} 1.0
infoblox_node_service_status_cpu_temp{identity="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_sys_temp Node service sys_temp 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_sys_temp gauge
infoblox_node_service_status_sys_temp{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_sys_temp{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_cpu_usage Node service cpu_usage 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_cpu_usage gauge
infoblox_node_service_status_cpu_usage{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_cpu_usage{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_cpu_usage{node_ip="10.99.0.142"} 1.0
infoblox_node_service_status_cpu_usage{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_core_files Node service core_files 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_core_files gauge
infoblox_node_service_status_core_files{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_core_files{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_memory Node service memory 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_memory gauge
infoblox_node_service_status_memory{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_memory{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_swap_usage Node service swap_usage 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_swap_usage gauge
infoblox_node_service_status_swap_usage{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_swap_usage{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_discovery_capacity Node service discovery_capacity 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_discovery_capacity gauge
infoblox_node_service_status_discovery_capacity{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_discovery_capacity{node_ip="10.99.0.142"} 1.0
# HELP infoblox_node_service_status_vpn_cert Node service vpn_cert 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_node_service_status_vpn_cert gauge
infoblox_node_service_status_vpn_cert{node_ip="10.99.0.141"} 1.0
infoblox_node_service_status_vpn_cert{node_ip="10.99.0.142"} 1.0
# HELP infoblox_service_status_dhcp Service dhcp 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_service_status_dhcp gauge
infoblox_service_status_dhcp 1.0
# HELP infoblox_service_status_dns Service dns 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_service_status_dns gauge
infoblox_service_status_dns 1.0
# HELP infoblox_service_status_dot_doh Service dot_doh 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_service_status_dot_doh gauge
infoblox_service_status_dot_doh 2.0
# HELP infoblox_service_status_ntp Service ntp 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_service_status_ntp gauge
infoblox_service_status_ntp 1.0
# HELP infoblox_service_status_hsm Service hsm 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_service_status_hsm gauge
infoblox_service_status_hsm 2.0
# HELP infoblox_service_status_reporting Service reporting 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_service_status_reporting gauge
infoblox_service_status_reporting 1.0
# HELP infoblox_service_status_imc_dca_bwl Service imc_dca_bwl 1=WORKING, 0=FAILED, 2=UNKNOWN
# TYPE infoblox_service_status_imc_dca_bwl gauge
infoblox_service_status_imc_dca_bwl 2.0
# HELP infoblox_node_info Node info info
# TYPE infoblox_node_info gauge
infoblox_node_info{ha_status="PASSIVE",hwid="0805201903700276",hwtype="IB-815",node_ip="10.99.0.141",platform="PHYSICAL"} 1.0
infoblox_node_info{ha_status="ACTIVE",hwid="0805201903700277",hwtype="IB-815",node_ip="10.99.0.142",platform="PHYSICAL"} 1.0
# HELP infoblox_up Infoblox API up
# TYPE infoblox_up gauge
infoblox_up 1.0
# HELP infoblox_scrape_time_seconds Infoblox API scrape time
# TYPE infoblox_scrape_time_seconds gauge
infoblox_scrape_time_seconds 0.33961824301513843

```
In addition to all the service metrics there is also `infoblox_node_info` with additional metadata 
labels. Metrics value is always 1.0

The `infoblox_up` is set to 1.0 if the exporter could connect to the Infoblox master and that the 
member exists.

## DHCP utilization
For a specific network that the infoblox master manage the metrics show the utilization of DCHP 
addresses. This can be valuable to alert on if the metrics is close to 1.0, 100 % utilization  

```commandline
# HELP infoblox_dhcp_utilization_ratio DHCP utilization ratio
# TYPE infoblox_dhcp_utilization_ratio gauge
infoblox_dhcp_utilization_ratio{network="140.166.134.128/26"} 0.212
# HELP infoblox_up Infoblox API up
# TYPE infoblox_up gauge
infoblox_up 1.0
# HELP infoblox_scrape_time_seconds Infoblox API scrape time
# TYPE infoblox_scrape_time_seconds gauge
infoblox_scrape_time_seconds 0.28882534499280155

```
# Discovery 
Please see the [infoblox-discovery](https://github.com/thenodon/infoblox_discovery)
to get dynamic Prometheus discovery configuration for   

# Environment variables

The following variables ar mandatory to set.

- BASIC_AUTH_USERNAME - the basic auth username to the exporter
- BASIC_AUTH_PASSWORD - the basic auth password to the exporter 
- INFOBLOX_MASTER - the ip/fqdn to the infoblox server
- INFOBLOX_WAPI_VERSION - the Infoblox master api version
- INFOBLOX_USERNAME - the Infoblox master username
- INFOBLOX_PASSWORD  - the Infoblox master password

The following are optional
- EXPORTER_HOST - default to `0.0.0.0`
- EXPORTER_PORT - default to `9597`
- EXPORTER_LOG_LEVEL - default to `INFO`

# Test
```
curl -s 'localhost:9597/probe?target=host.foo.com&module=member_services' 
```

The `type` can have the following values:
- member_services - the target is infoblox member
- dhcp_utilization - the target has to be network like `10.121.151.128/26`
