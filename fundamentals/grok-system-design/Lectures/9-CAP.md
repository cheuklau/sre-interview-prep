# CAP Theorem

- CAP theorem states it is impossible for a distributed software system to provide more than two out of the three of the following:
    1. Consistency
        * All nodes see the same data at the same time
        * Achieved by updating several nodes before allowing further reads
    2. Availability
        * Every request gets a response on success/failure
        * Achieved by replicating data across different servers
    3. Partition tolerance
        * System continues to work despite message loss or partial failure
        * Sustain any amount of network failure that doesn't result in a failure of the entire network
        * Data is replicated across nodes and networks to keep the system up through outages
- We can only build a system that has two of the three properties
    * To be consistent, all nodes should see the same set of updates in the same order
    * But if network loses a partition, updates in one partition might not make it to the other partitions before a client reads from out-of-date partition
    * Only fix is to stop serving requests from out-of-date partition, but then service no longer 100% available
- Examples:
    * AP: Cassandra, CouchDB
    * AC: RDBMS
    * CP: Big table, mongoDB, HBase