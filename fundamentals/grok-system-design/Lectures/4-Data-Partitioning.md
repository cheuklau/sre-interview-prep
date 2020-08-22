# Data Partitioning

- Data partitioning breaks up big database into smaller parts
- Splits up database across machines to improve manageability, performance, availability, and load balancing of an applicaiton
- At certain scale point, cheaper to scale horizontally than grow vertically

## Partitioning Methods

- Three most populat schemes used by various large scale apps:
    1. Horizontal partitioning
        * Put different rows into different tables
        * Example: zip codes < 10000 stored in one table and the rest in another (range based partitioning)
        * Also known as data sharding
        * Need to carefully chose ranges or else unbalanced servers occur
    2. Vertical partitioning
        * Divide our data to store tables related to a specific feature in their own server
        * Example: place profile info on one DB server, friends list on another and photos on a third server
        * Straightforward to implement and has low impact on app
        * Main problem is that if app grows, may be necessary to further partition a feature specific DB across various servers
    3. Directory based partitioning
        * Create a lookup service that knows current partitioning scheme and abstracts it away from DB access code
        * To find out where a particular data entity resides, we query the directory server that holds the mapping between each tuple key to DB server
        * We can perform tasks e.g., adding servers to DB pool or change partitioning scheme without having impact on app

## Partitioning Criteria

- Key or hash-based partitioning
    * Apply a hash function to some key attributes that yields the partition number
    * Example: if we have 100 DB servers and our ID is an incrementing numerical value we can hash with `ID % 100` to determine which DB server to assign a record
    * Problem with approach is that it effectively fixes the number of total DB servers since adding a new one would require redistribution of data and downtime
    * Workaround is to use consistent hashing
- List partitioning
    * Each partition is assigned a list of values so whenever we want to insert a new record, we see which partition contains our key and then store it there
    * Example: users living in Iceland, Norway, Sweden, Finland and Denmark are in partition for Nordic countries
- Round-robin partitioning
    * With n paritions, the `i` tuple is assinged to partition `i mod n`
- Composite partitioning
    * Combine any of the above partitioning schemes to devise a new scheme

## Common Problems of Data Partitioning

- Extra constraints on different operations that can be performed on a partitioned database
- Operations across multiple tables or multiple rows in the same table can no longer run on the same server
- Some constraints and additional complexities caused by partitioning:
    1. Joins and denormalization
        * Once DB is partitioned and spread across multiple machines, often not feasible to perform joins
        * Data has to be compiled from multiple servers
        * Workaround is to denormalize the DB so that queries that previously required joins can be performed on a single table
    2. Referential integrity
        * Trying to enforce data integrity constraints e.g., foreign keys in a partitioned DB can be difficult
        * Most RDBMS do not support foreign keys constraints across DBs on different DB servers
        * This means apps that require referential integrity on partitioned DBs have to enforce it in the app code
    3. Rebalancing
        * Many reasons we have to change our partitioning scheme:
            1. Data partition is not uniform
            2. A lot of load on a particular partition
        * In these cases, we either have to:
            1. Create more DB paritions
            2. Rebalance existing partitions which means paritioning scheme changed and all existing data moved to new locations
        * Rebalancing without incurring downtime is difficult