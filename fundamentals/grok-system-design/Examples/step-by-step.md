# System Design Interviews: Step by Step Guide

# Step 1: Requirements Clarification

- Define end goals
- Clarify parts of the system to focus oon
- Example designing a Twitter-like service:
    1. Will users be able to post tweets/follow people
    2. Should we design to create user timeline
    3. Will tweets coontain photos and videos
    4. Are we focusing oon backend only or front end too
    5. Will users be able to search tweets

# Step 2: Back of Envelope Calculation

- Estimate scale of the system we are going to design
- Help with scaling, partitining, load balancing and caching
- What scale expected from system?
- How much storage?
- What network bandwidth?

# Step 3: System Interface Definition

- What APIs are expected from the system
- `postTweet(user_id, tweet_data, tweet_location, ...)`

# Step 4: Defining Data Model

- Help with clarifying how data will flow between different parts of system
- Guide for data partitioning and management
- Candidate should identify different parts of system, how they will interact and other aspects of data management e.g., storage, transport, encryption, etc
- Example:
    * `User: UserID, Name, Email`
    * `Tweet: TweetID, Content`
- Decide which database too use e.g., NoSQL or MySQL
- What kind of block storage to store photoos and videos

# Step 5: High-Level Design

- Draw block diagram representing core components of system
- Enough to solve actual problem end-to-end
- Example:
    * Client
    * Load balancer
    * App servers
    * Databases/File storage

# Step 6: Detailed Design

- Dig deeper intoo a few major coomponents
- Present different approaches including pros and cons
- Example:
    * How should we partitioon data
    * How will we handle hot paths for databases
    * How to store data to optimize searches
    * Where can we implement caching
    * What components need better load balancing

# Step 7: Identifying and Resolving Bottlenecks

- Identify bottlenecks and approaches to mitigate them
    * SPOFs
    * Do we have enough replicas of the data
    * Do we have enough copies of services to be highly available
    * How are we monitoring performance, alerting

# Step 8: Summary

- Be organized