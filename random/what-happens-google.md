# What Happens When You Enter http://google.com/

## Parse URL

- Browser receives URL with protocol (HTTP) and resource (`/`)

## Check HSTS List

- Browser checks its preloaded HTTP Strict Transport Security (HSTS) list to see if it is a website that has to be requested via HTTPS
- If on list, browser sends request via HTTPS instead of HTTP

## DNS Lookup

- Browser checks if domain is in cache (`chrome://net-internals/#dns`)
- If not found, browser calls `gethostbyname` to do lookup
- `gethostbyname` checks if hostname can be resolved in `hosts` file
- If not found, then browser makes a request to DNS server typically the lcoal router or ISP's caching DNS server
- If DNS server is on same subnet, network library follows ARP process for DNS server
- If DNS server is on different subnet, network library follows ARP process for default gateway

## ARP Request

- To send Address Resolution Protocol (ARP) broadcast the network library needs target IP address and MAC address of the interface it will use to send out the ARP broadcast
- ARP cache checked for ARP entry for target IP
- If not in ARP cache, look up route table
- Network library sends a layer 2 ARP request:
```
Sender MAC: interface:mac:address:here
Sender IP: interface.ip.goes.here
Target MAC: FF:FF:FF:FF:FF:FF (Broadcast)
Target IP: target.ip.goes.here
```
- Router responds with an ARP reply:
```
Sender MAC: target:mac:address:here
Sender IP: target.ip.goes.here
Target MAC: interface:mac:address:here
Target IP: interface.ip.goes.here
```
- Now network library has IP address of either DNS server or default gateway
- DNS client establishes socket to UDP port 53 on the DNS server
- If local/ISP DNS server does not have it, then a recursive search is requested that flows up the list of DNS servers until the SOA is reached