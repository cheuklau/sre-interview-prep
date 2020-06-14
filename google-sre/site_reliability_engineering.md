## Table of Contents
- [Chapter 1 - Introduction](#Chapter-1---Introduction)
- [Chapter 2 - The Viewpoint of an SRE](#Chapter-2---The-Viewpoint-of-an-SRE)

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