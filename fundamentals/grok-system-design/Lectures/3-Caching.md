# Caching

- LBs help you scale horizontally, caching enables you to make better use of existing resources
- Caches take advantage of the locality of reference principle (recently requested data likely to be requested again)
- Used in every layer of computing e.g., hardware, OS, web browsers, web apps, etc
- Cache has limited amount of space but faster than original data source, and contains most recently accessed items
- Caches implemented near front end in order to retrun data quickly

## Application Server Cache

- Place cache on a request layer node to enable local storage of response data
- When request made to service, node returns cached data if it exists; otherwise, node will query data from disk
- Cache can be in memory (fast) or on node's storage (slow, but still faster than going to network storage)
- If there is a cluster of cache nodes, higher chance of cache miss since LB randomly distributes request
- To overcome this we can use global cache and distributed caches

## Content Distribution Network (CDN)

- CDN is a kind of cache used for serving large amounts of static data
- CDN setup:
    1. Request ask CDN for a piece of static data
    2. CDN serve content if locally available
    3. If unavailable, CDN queries back-end servers for the file, cache it locally, serve it to requesting server
- Note: if system isn't large enough yet to have a CDN, we can just use Nginx with a separate subdomain pointing to it and have it serve static media

## Cache Invalidation

- If data is modified in database, it should be invalidated in the cache; otherwise inconsisten app behavior will occur
- Three schemes for cache invalidation:
    1. Write-through cache
        * Data written into cache and corresponding database at the same time
        * Complete data consistency between cache and storage
        * Minimizes risk of data loss since every write operation must be done twice before returning success to the client
        * Scheme has higher latency for write operations
    2. Write-around cache
        * Data written directly to permanent storage, bypassing cache
        * Reduce cache from being flooded with write operations that will not subsequenctly be re-read
        * Disadvantage that a read request for recently written data will create a cache miss and must be read from slower backend
    3. Write-back cache
        * Data is written to cache and completion confirmed to client
        * Write to permanent is done after a specified interval or under certain conditions
        * Results in low latency and high throughput for write-intensive apps
        * Risk of data loss if cache crash since only copy of data is in the cache

## Cache Eviction Policies

- Common cache eviction policies:
    1. First in first out (FIFO)
        * Evict first block accessed first without regard to how often or how many times it was accessed before
    2. Last in first out (LIFO)
        * Evict block accessed most recently first without regard to how often or how many times it was accessed before
    3. Least recently used (LRU)
        * Discard least recently used items first
    4. Most recently used (MRU)
        * Discards most recently used items first
    5. Least frequently used (LFU)
        * Counts how often an item is needed and the least needed items are discarded first
    6. Random replacement (RR)
        * Randomly select an item to discard when required