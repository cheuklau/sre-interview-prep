# System Design Basics

- When designing a large system consider:
    1. What are different architectural pieces needed?
    2. How do these pieces work together?
    3. How can we utilize these pieces? Tradeoffs?

# Key Characteristics of Distributed Systems

## Scalability

- Scalability is the capability of a system, process or network to grow and manage increased demand
- System may have to scale for a variety of reasons e.g., increased data volume or amount of work
- Scalable system should achieve this without performance loss
- In general, performance of a system declines with system size due to management or environment cost
- Some tasks may not be distributed (either due to atomic nature or system design flaw)
    * These will limit speed-up obtained by distribution
- Scalable architecture attempts to balance load evently across all nodes

### Horizontal vs. Vertical Scaling

- Horizontal scaling adds more servers to pool of resources
- Vertical scaling adds more power (e.g., CPU, RAM, storage) to an existing server
- Horizontal scaling is easier to scale dynamically just by adding more nodes
- Vertical scaling requires downtimes and has an upper limit
- Horizontal scaling examples:
    * Cassandra
    * MongoDB
- Vertical scaling example:
    * MySQL

### Reliability

- Reliability is the probability a system will fail in a given period
- Distributed system is reliable if it delvers services even when one or more of its software or hardware components fail
- A reliable distributed system achieves reliability through redundancy in both software components and the data
- Redundancy has a cost and a reliable system has to pay that to achieve resilience for services by eliminating every SPOF

### Availability

- Availability is the time a system remains opeartional to perform its required function in a given period
- Percentage of time that a system, service or machine remains operational
- If a system is reliable, it is available
- If a system is available, it is not necessarily reliable
    * For example, it is possible to achieve high availability with an unreliable product by minimizing repair time and ensuring spares are always available when needed

### Efficiency

- Consider operation that runs in a distributed manner and delivers set of items
- Two measures of efficiency are response time (delay to obtain the first item) and throughput (number of items delivered in a unit time)
- Above two measures correspond to following unit costs:
    1. Number of messages sent by nodes regardless of message size
    2. Size of messages representing volume of data exchanges
- Complexity of operations supported by distributed data structures charactierized as a function of one of those unit costs
- Difficult to develop a precise cost model that accurately accounts for all performance factors e.g., network topology, network load, etc

### Serviceability and Manageability

- Ease of operation and maintenance
- If MTTR increases then availability decreases
- Considerations for manageability:
    * Ease of diagnosing problems
    * Ease of making updates or modifications
    * Ease of operation