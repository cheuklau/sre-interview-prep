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

## Continuous Integration and Deployment with Bazel

- Dropbox server-side repo lives in a single repo
- Used to run entire test corpus on every commit
- However, no longer tenable due to large number of tests
- Pointless and wasteful execution of tests that can't be affected by a particular change
- Address problem with build and test system called Bazel
    * Views repo as a set of targets and dependencies between them
    * Knows dependency graph between all source files and tests in the repo
    * Bazel computes set of tests affected by a commit
- Futher save resources by rolling up commits that affect same areas into a single test
    * This batching could break detection but automated breakage detection system called Athena can detect which tests caused the breakage
- Deployment system distributes software to hosts in the form of SquashFS images

## Monitoring Server Applications with Vortex

- Monitoring systems operate across 1000 machines with 60000 alerts
- Speed query speed by caching >200,000 queries
- Vortex is server-side monitoring system
    * Kafka for queueing ingested metrics
    * Aggregate across tags oover time (probably Kafka Stream)
    * Write results back to Kafka
    * Processes consume data from Kafka and store in memory for evaluating alerts, on-disk RocksDB (within last day) and HBase (older than one day)
- Issues:
    * Kafka and HBase issues required manual recovery
    * Some code may innudate ingestion pipeline
    * Operations and deployments of monitoring infra can cause data loss
    * Poor query performance and expensive queries not properly isolated
- Design goals
    * Completely horizontally-scalable ingestion - just add nodes to the deployment
    * Silent deployments
    * No single point of failures
    * Well defined ingestion limits - no single individual service should innudate ingestion
    * Multi-tenant query system - individual queries should not be able to disrupt monitoring system
    * Metrics scale as service scales
- Metric types
    * Counter - number of occurrences over time
    * Gauge - value at current time
    * Topology - identify the node thats logging metrics
    * Histogram - provide percentile distributions for values
- Design
    * NodeCollector
        + Vortex metrics stored in ring buffer in each local process
        + Poll-based metric collection on two tiers
        + First tier is NodeCollector - runs oon every node, polls other processes of nodes and aggregate metric into per-node total
        + NodeCollector polled by MetricCollector which writes data to storage
        + NodeCollector only poll processes when they themeselves are polled, so they are stateless
    * MetricCollector
        + MetricCollector polls NodeCollectors every 10 seconds
        + Internally buffers the metrics for four minutes before flushing to storage
            1. Reduces write load on Cassandra for storage
            2. Allows data to enter in one arrangement and leave in another (grouped by metric name rather than by node)
    * System-defined Tags
        +