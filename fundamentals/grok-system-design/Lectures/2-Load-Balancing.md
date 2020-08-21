# Load Balancing

- Load balancers (LB) help spread traffic across a cluster of servers to improve responsiveness and availability of applications
- LB keep track of the status of all resources while distributing requests
- LB will stop sending requests to unhealthy servers
- LB sits between client and server accepting incoming network and application traffic
- LB distributes traffic across multiple backend servers using different algorithms
- This reduces individual server load and prevents any one app server from being a SPOF
- To achieve full scalability and redundancy, we load balance at each layer of the system:
    * Between user and web server
    * Between web servers and internal platform layer e.g., application servers or cache servers
    * Between internal platform layer and database

## Benefits of Load Balancing

- Users experience faster, uninterrupted service
- Less downtime and higher throughput
- Makes it easier for system administrators to handle incoming requests while decreasing wait time for users
- Provide benefits like predictive analytics that determine traffic bottlenecks
- System administrators experience fewer failed or stressed components

## Load Balancing Algorithms

- Two factors:
    1. Is the server actually responding appropriately to requests
    2. Use a preconfigured algorithm to select one of the healthy servers
- Health checks
    * Only forward traffic to healthy backend servers
    * Health checks regularly attempt to connect to backend servers to ensure they are listening
    * If a server fails a health check, it is automatically removed from the pool
- Variety of algorithms
    1. Least connection method - directs traffic to server with fewest active connections
    2. Least response time method - directs traffic to server with fewest active connections and lowest average response time
    3. Least bandwidth method - directs traffic to server currently serving least amount of traffic measure in Mbps
    4. Round robin
    5. Weighted round robin
    6. IP hash - hash of IP address of client is calculated to redirect request to a server

## Redundant Load Balancers

- Load balancer can be a SPOF
- To overcome this a second LB can be connected to the first to form a cluster
- Each LB monitors the health of the other and in the event of a failure, the secondary LB takes over