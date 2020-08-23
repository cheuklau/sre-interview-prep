# Redundancy and Replication

## Redundancy

- Redundancy is the duplication of critical components or functions of a system to increase system reliability or to improve system performance
- Redundancy removes SPOF and provides backups in a crisis
- Example: If two instances of a service running in prod and one fails, the system can failover to the other one

## Replication

- Replication means sharing info to ensure consistency between redundant resources e.g., software/hardware components to improve reliability, fault-tolerance or accessibility
- Widely used in database management systems (DBMS) usually with a primary-replica relationship between original and replicas
- Primary server gets updates and then it updates the replicas
