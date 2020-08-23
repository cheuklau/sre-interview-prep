# SQL vs NoSQL

- Two main DB solutions: SQL (relational) and NoSQL (non-relational)
- Relational databases are structured with pre-defined schemas
- Non-relational databases are unstructured, distributed and have a dynamic schema

## SQL

- Relational databases store data in rows and columns
- Each row contains all info about one entity
- Each column contains all separeate data points
- Examples: MySQL, Postgres, MariaDB

## NoSQL

- Most common types of NoSQL:
    1. Key-value stores
        * Data is stored in an array of key-value pairs
        * Examples: Redis, DynamoDB
    2. Document databases
        * Data stored in documents
        * Documents grouped together into collections
        * Each document can have an entirely different structure
        * Examples: MongoDB
    3. Wide-column databases
        * Columnar databases have column families which are containers for rows
        * Don't need to know all the columns upfront
        * Each row diesn't have to have the same number of columns
        * Beste suited for analyzing large datasets
        * Examples: Cassandra, HBase
    4. Graph databases
        * Used to store data whose relations are best represented in a graph
        * Data save in graph structure with nodes (entities), properties (info about entities) and lines (connection between entities)
        * Examples: Neo4J

## High Level Differences Between SQL and NoSQL

- Storage
    * SQL stores data in tables where each row represents an entity and each column represents data point about that entity
    * NoSQL databases have different storage models e.g., key-value, document, graph and columnar
- Schema
    * In SQL, each record conforms to a fixed schema i.e., columns must be decided before data entry
        + Schema can be modified layer but requires modifying entire database and going offline
    * In NoSQL, schemas are dynamic
        + Columns added on the fly and each row doesn't have to contain data for each column
- Querying
    * SQL databases use SQL for defining and manipulating the data which is very powerful
    * In NoSQL, queries are focues on a collection of documents
        + Different databases have different syntax
- Scalability
    * SQL databases are vertically scalable i.e., by increasing memory, CPU, etc
        + Possible to scale a relational database across multiple servers, but challenging and time-consuming
    * NoSQL are horizontally scalable
- Reliability or ACID (atomicity, consistency, isolation, durability) compliancy
    * Vast majority of relational databases are ACID compliant
        + When it comes to data reliability and safe guaranteee of performing transactions, SQL is best bet
    * Most NoSQL solutions sacrifice ACID compliance for performance and scalability

## SQL vs NoSQL - Which One to Use?

- Reasons to use SQL database
    1. Need to ensure ACID compliance
        * ACID compliance reduces anomalies and protects integrity of database by prescribing exactly how transactions interact with the database
    2. Data is structured and unchanging
        * If business is not experiencing massive growth that would require more servers and data is consistent, there may be no reason to use a system designed to support a variety of data types and high traffic volume
- Reasons to use NoSQL database
    1. Storing large volumes of data that often have little to no structure
        * NoSQL database sets no limits on the types of data we can store together and allows us to add new types as the need changes
        * With document-based databases, you can store data in one place without having to define what types of data those are in advance
    2. Making the most of cloud computing and storage
        * Cloud-based storage is excellent cost-saving solution but requires data to be easily spread across multiple servers to scale up
        * NoSQL databases designed to be scaled across multiple datacenters
    3. Rapid development
        * NoSQL useful for rapid development as it doesn't need to be prepped ahead of time
        * Require frequent updates to data structure without much downtime between versions

## Aside: ACID

- Set of properties that guarantee database transactions are processed reliably
- Atomicity
    * Guarantee that either all of the transaction succeeeds or none of it does
    * All or nothing
- Consistency
    * Guarantee that all data will be consistent
- Isolation
    * Guarantee that all transactions occur in isolation i.e., no transaction will be affected by any other transaction
    * Transaction cannot read data from any other data that has not yet completed
- Durability
    * Once transaction is commmitted it will remain in the system