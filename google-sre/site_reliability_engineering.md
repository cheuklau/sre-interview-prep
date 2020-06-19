## Table of Contents
- [Chapter 1 - Introduction](#Chapter-1---Introduction)
- [Chapter 2 - The Viewpoint of an SRE](#Chapter-2---The-Viewpoint-of-an-SRE)
- [Chapter 3 - Embracing Risks](#Chapter-3---Embracing-Risks)
- [Chapter 4 - Service Level Objectives](#Chapter-4---Service-Level-Objectives)
- [Chapter 5 - Eliminating Toil](#Chapter-5---Eliminating-Toil)
- [Chapter 6 - Monitoring Distributed Systems](#Chapter-6---Monitoring-Distributed-Systems)

## Chapter 1 - Introduction

### The Sysadmin Approach to Service Management

Sysadmin approach is easy to implement, but disadvantagess include:
- direct costs (e.g., change management and event handling) becomes expensive as service grows, and
- indirect costs due to conflicts between devs and ops since they have different incentives (e.g., velocity vs stability).

### Site Reliability Engineering

SRE design an implement automation with software to replace human labor. Place 50% cap on ops work for SREs, remainder on improving system automation.

### Tenets of SRE

SRE team is responsible for availability, latency, performance, efficiency, change management, monitoring, emergency response and capacity planning for their service.

On average SREs should receive a maximum of two events per 8-12 hour on-call shift. Postmortems should be written for significant incidents.

Set error budget (i.e., accepted unavailability) with product manager. Spend error budget on risks to maximize feature velocity.

Monitoring is key too track system health. Monitoring output:
- alert to signify a human action is required,
- tickets to signifigy human action is required but not immediately,
- logging for diagnostic purposes.

MTTR is how quickly response team can bring system back to health. Playbooks improve MTTR significantly (3x observed).

Use autoomation for tasks with high probability of causing outages:
- implementing progressive rollouts,
- problem detection, and
- rolling back changes.

Steps in capacity planning:
- accurate organic (natural adoption of usage) demand forecast,
- accurate inorganic (feature launches, marketing campaigns) demand forecast, and
- load testing of system.

Provisioning (e.g., spinning up new instances) should be quick and only done when necessary.

## Chapter 2 - The Viewpoint of an SRE

### Hardware

Terminology:
- machine: hardware
- server: software that runs a service
- rack: tens of machines
- row: one or more racks
- cluster: one or more rows
- datacenter: multiple clusters
- campus: multiple datacenters

### Managing Machines

Borg manages long-running (server) and ephemeral (map-reduce) jobs in a cluster. It uses its own DNS (BNS) to resolve BNS name to IP and port.

### Managing Storage

Tasks can use local disk (D) as scratchpad. Layer on top of D is a cluster-wide filesystem with replication and encryption (Colossus). Several database-like services built on top of Collosus: Bigtable (NoSQL), Spanner (SQL), and Blobstore.

### Managing Networking

Global service load balancer performs geographic load balancing for DNS requests, service-level load balancing and remote procedure call level load balancing.

### Lock Service

Chubby provides a filesystem-like API for maintaining locks using Paxos protocol for asynchronous Consensus.

### Monitoring and Alerting

Borgmon monitoring program scrapes metrics from servers.

### Software Infrastructure

Code is heavily multi-threaded so one task can use many cores. Srevices communicate using RPC infrastructure named Stubby. GSLB can load balance RPCs. Data transferred to and from RPC using protocol buffers (protobufs).

### Development Environment

SWEs work from a single shared repo. Devs can submit a changelist (CL) to any project for review, and merge it to the mainline. Build requests are sent to build servers where automated tests are run on all software that may depend on the CL. Changes are automatically pushed to production if tests pass. Otherwise, submitter is notified.

### Life of a Request

Consider a service with two parts: (1) backend that reads from BigTable, and (2) front-end handling user requests. Flow of a user request:
1. User points browser to `www.app.google.com`
2. User's DNS server resolves address to IP of Google's DNS server
3. Google's DNS server talks to GSLB which provides IP of server to handle request
4. User connects to HTTP server of returned IP
5. HTTP server is a reverse proxy that terminates TCP connection
6. HTTP server uses GSLB to find IP of front-end server to use
8. HTTP server sends RPC with HTTP request to front-end server
9. Front-end constructs a protobuf with HTTP request data and sends it to backend server (IP from GSLB)
10. Backend contacts BigTable server to retrieve required data
11. BigTable sends reply protobuf to backend server
12. Backend server sends protobuf to front-end
13. Front-end assembles HTML with data and returns to user

### Job and Data Organization

Load testing showoed backend servers can handle 100 QPS. Trials showed peak of 3470 QPS so we need 35 servers. We set up 37 (`N+2`) since during updates one server will be down. We may also want to distribute the servers across regions based on region use. We may also want to replicate the BigTable across regions to reduce latency.

## Chapter 3 - Embracing Risks

### Managing Risk

Reliability costs:
1. Redundant machine/compute resources
2. Opportunity cost

Make service reliable but not more reliable than it needs to be.

### Measuring Service Risk

We want to identify an objective to optimize. We focus on unplanned downtime measured by service availability expressed in number of nines.

### Time-Based Availability

availability=uptime/(uptime+downtime)


### Aggregate Availability

availability=successful requests/total requests

### Risk Tolerance of Services

Product managers understand users and business. They determine reliability requirements for a service.

### Target Level of Availability

Service dependent e.g., Google Apps for Work require higher availability than Youtube.

### Types of Failures

Different failures may impact services differently. More significant failures may result taking down the entire service entirely to debug. We may also have scheduled outages which should not be counted as unplanned downtime.

### Cost

Cost is a key factor in determining appropriate availability target for a service.

### Other Service Metrics

Need to understand which metrics are important and which aren't when attempting to take meaningful risks.

### Identifying Risk Tolerance of Infrastructure Services

Infrastructure components often have multiple clients with different needs.

### Target Level of Availability

Consider BigTable. Some services need low latency, high reliability whereas others require high throughput over reliability.

### Cost

It is too expensive to make the system ultra-reliable. We can partition the infrastructure and build two types of cluster: one low-latency and another high throughput.

### Motivation of Error Budgets

Tension between SRE performance (reliability) and developer performance (velocity) include:
- software fault tolerance,
- testing,
- push frequency, and
- canary duration and size.
The two teams define an error budget based on the service level objective (SLO). As long as uptime is above SLO, new releases can be pushed. Development teams will push for more testing or slower push velocity to not risk using up budget and stalling their launch i.e., development teams will become self-policing.

## Chapter 4 - Service Level Objectives

### Service Level Terminology

### Indicators

Service level indicator (SLI) is a quantitative measure of level of service (e.g., request latency, error rate, system throughput, availability, storage durability).

### Objectives

Service level objective (SLO) is a target value for an SLI.

### Agreements

Service level agreements (SLA) is a contract with end users that includes consequences of meeting or missing SLOs.

### What Do You and Your Users Care About?

SLIs fall into a few categories:
1. User-facing serving systems: availability, latency and throughput
2. Storage systems: latency, availability, durability
3. Big data systems: latency, throughput

### Collecting Indicators

We should consider both server and client side metrics.

### Aggregation

Use percentiles instead of averages to avoid false positives on skewed distributions.

### Standardize Indicators

We should standardize common definitions for SLIs e.g., averaged over 1 minute.

### Choosing Targets

Rule of thumbs:
1. Do not pick a value based on current performance.
2. Keep the target simple to define.
3. Avoid absolutes.
4. Have as few SLOs as possible.
5. Refine SLO definitions and their targets over time as you learn the system's behavior.

### SLOs Set Expectations

Use a tighter internal SLO than advertised. Avoid over-dependence by deliberately taking the system offline, throttling some requests, etc.

## Chapter 5 - Eliminating Toil

### Toil Defined

Administrative chores are overhead. Toil is work needed to run a production service that is manual, repetitive, automatable, tactical, devoid of enduring value and scales linearly with growth.

### Why Less Toil is Better

SRE goal to keep toil below 50% of each SRE's time. Other 50% shoould be engineering work to reduce toil.

### What Qualifies as Engineering

Engineering work produces permanent improvements and guided by strategy. SRE activities fall into:
1. Software engineering
2. Systems engineering
3. Toil
4. Overhead

### Is Toil Bad?

Toil can cause career stagnation, low morale, create confusion, slow progress, sets precedent, promotes attrition and causes breach of faith.

## Chapter 6 - Monitoring Distributed Systems

### Definitions

- Monitoring: collecting, processing, aggregating, displaying real-time quantitative data about a system
- White-box monitoring: metrics exposed by internals of system e.g., logs
- Black-box monitoring: externally visible behavior as a user would see
- Dashboard: app providing summary view of a system's core services
- Alert: notification read by a human
- Root cause: defect in software or human system causing a failure
- Node and machine: single instance of a running kernel
- Push: changing a server's running software

### Why Monitor?

- Analyze long-term trends
- Compare over time or experiment groups
- Alerting
- Building dashboards
- Conducting ad-hoc retrospective analysis

### Setting Reasonable Expectations for Monitoring

- Keep elements of monitoring system that direct to a pager simple and roobust.

### Symptoms Versus Causes

- Symptom: what is broken
- Cause: why is it broken
- Example:
    * Symptom: Serving HTTP 500s or 404s
    * Cause: Database servers are confusing connections

### Black-Box Versus White-Box

- Black-box is symptom-oriented and represents active problems.
- White-box allows detection of imminent problems.

### The Four Golden Signals

1. Latency: time to service a request
2. Traffic: demand on system
3. Errors: explicit (500s), implicit (200s with wrong content) or by policy (slow 200s)
4. Saturation: how full the system is

### Worrying About Your Tail

- To differentiate between slow average and slow tail, collect request couonts bucketed by latencies.

### Choosing an Appropriate Resolution for Measurements

- Different system aspects require different levels of granularity.
- For example, CPU per second to capture spikes, but hard drive space every 1-2 minutes.

### As Simple as Possible, No Simpler

- Keep monitoring simple:
1. Rules that catch real incidents should be as simple as possible
2. Remove data collection, aggregation and alerting that is rarely used
3. Remove signals in dashboards that are not used
