# Indexes

- Goal of creating an index on a particular table in a DB is to make it faster to search through the table and find relevant rows
- Indexes can be created using one or more columns of a database table, providing rapid random lookups and efficient access of ordered records

## Example: A Library Catalog

- Library catalog is a register that contains list of books found in a library
- Catalog organized like a DB table with four columns: `Title`, `Writer`, `Subject` and `Date`
- Two such catalogs:
    * One sorted by `Title`
    * One sorted by `Writer`
    * Provide a sorted list of data that is easily searchable by relevant information
- Index is a data structure that can be perceived as a table of contents that points us to the location where actual data lives
- To create index on a column of a table, we store column and a pointer to the whole row in the index
- For example, we can create an index on `Title` where each row contains the `Title` and a pointer to the full row in the original DB table
- Must carefully consider how users will access the data
- Particularly important when we have a large dataset
    * Can't possibly iterate over that much data in a reasonable amount of time
    * Very likely large data set is spread over multiple machines

## How do Indexes Decrease Write Performance?

- Speeds up data retrieval but may itself by large due to additional keys which slow down data insertion and update
- When adding rows or updating existing rows for a table with active index, we have to write the new data and also update the index
    * This decreases write performance
- Therefore, adding unnecessary indexes to tables should be avoided
- Adding indexes is about improving performance of search queries
- Should not add indexes to write-heavy databases