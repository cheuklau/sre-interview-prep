# Consistent Hashing

- Distributed Hash Table (DHT) is a fundamental component used in distributed scalable syustems
- Hash tables need a key, value and a hash function to map the key to a location where the value is stored i.e., `index=hash_function(key)`
- Example:
    * Given `n` cache servers, an intuitive hash function would be `key % n`
    * Two drawbacks:
        1. Not horizontally scable because whenever a new cache host is added, all existing mappings are broken
        2. May not be load balanced especially for non-uniformly distributed data

## Consistent Hashing

- Useful strategy for distributed caching systems and DHTs
- Distribute data across a cluster in such a way that will minimize reorganization when nodes are added or removed
- When hash table is resized e.g., new cache host added, only `k/n` keys need to be remapped
- Objects are mapped to the same host if possible
- When host is removed, objects on that host are shared by the other hosts

## How Does it Work?

- Consistent hashing maps a key to an integer
- Suppose output of the hash function is `[0, 256]` range
- Imagine integers in the range placed on a ring such taht the values are wrapped around
- Procedure:
    1. Given a list of cache servers, hash them to integers in the range
    2. To map a key to a server
        * Hash it to a single integer
        * Move clockwise on the ring until finding the first cache it encounters
        * That cache is the one that contains the key
- To add a new server `D`, keys originally in `C` will be split with some of them shifted to `D`
- To remove cache `A` all keys that were originally mapped to `A` will fall into `B`
- For load balancing, real data is essentially randomly distributed and thus may not be uniform
- To handle above issue, we add virtual replicas for caches i.e., instead of mapping each cache to a single point on the ring, we map it to multiple points on the ring