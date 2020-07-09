## Intelligent DNS-Based Load Balancing

- Improve point of presence (PoP) selection automation for edge network
- Dropbox edge network provides geolocation-based load balancing
- Send user to closest point of presense
- User sends DNS request, we reply with a specific Dropbox IP
    * With geolocation LB, closest PoP is closest in terms of distance to the user
- Developed 20 edge clusters
- However, some corner cases where geolocatioon does not work

### When Geolocation LB Doesn't Work

- Geolocation does not consider network topology
- User can be right next to a PoP but their ISP does not have network interconnection to it
- User request may then have to travel long distances to reach PoP
- One solution is to set up a private network interconnect (PNI) with an ISP at every user location where these corner cases occur
- However, it is unrealistic to track all the corner cases when geo routing does not work

### How to Improve DNS Load Balancing

- Teach DNS load balancing about network topology
- Route based on latency/network topology closeness
- After getting route map, teach DNS server to use it
- Dropbox collaborated with NS1, adding ability to upload and use a custom DNS map on a per-record basis

### Building Our Map

- Already have latency data between user subnets and edge PoPs
- Desktop client framework runs tests to measure latency between client and every Dropbox edge cluster
- Also need mapping between a user's subnet and DNS resolver they are using:
    * user <--> ISP's DNS resolver <--> DBX authoritative DNS server
- Authoritative DNS server does not see user's IP but the IP of DNS resolver
- Need to figure ouot which DNS resolver a user is using
- Added a test to client framework
    * DNS queries to random sub-domains of dropbox.com
    * Forces DNS resolver to perform full DNS lookups
    * On dropbox server side, we log all requests to subdomain to get map between unique DNS name and DNS resolver IP
    * At same time, client reports back which unique DNS queries it has been using
    * Above two sources of info allows us to determine:
        + client's subnet <--> DNS resolver <--> latency to PoP
- We now know all user's info behind DNS resolvers and latency towards all PoPs
- Can determine what is best PoP for most users behind this DNS resolver
- Map IP address/subnets of resolvers to PoP IP