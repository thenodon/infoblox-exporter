infoblox-exporter
----------------------
# Overview

# Test
```
curl -s 'localhost:9597/probe?target=host.foo.com&type=nodes' 
```

The `type` can have the following values:
- nodes - the target is infoblox member
- dhcp_utilization - the target has to be network like `10.121.151.128/26`