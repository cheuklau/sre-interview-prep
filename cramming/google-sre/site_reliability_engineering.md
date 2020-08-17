## Table of Contents
- [Chapter 1 - Introduction](#Chapter-1---Introduction)
- [Chapter 2 - The Viewpoint of an SRE](#Chapter-2---The-Viewpoint-of-an-SRE)
- [Chapter 3 - Embracing Risks](#Chapter-3---Embracing-Risks)
- [Chapter 4 - Service Level Objectives](#Chapter-4---Service-Level-Objectives)
- [Chapter 5 - Eliminating Toil](#Chapter-5---Eliminating-Toil)
- [Chapter 6 - Monitoring Distributed Systems](#Chapter-6---Monitoring-Distributed-Systems)
- [Chapter 7 - The Evolution of Automation at Google](#Chapter-7---The-Evolution-of-Automation-at-Gooogle)
- [Chapter 8 - Release Engineering](#Chapter-8---Release-Engineering)
- [Chapter 9 - Simplicity](#Chapter-9---Simplicity)
- [Chapter 10 - Practical Alerting](#Chapter-10---Practical-Alerting)
- [Chapter 11 - Being On-Call](#Chapter-11---Being-On---Call)
- [Chapter 12 - Effective Troubleshooting](#Chapter-12---Effective-Troubleshooting)
- [Chapter 13 - Emergency Response](#Chapter-13---Emergency-Response)
- [Chapter 14 - Managing Incidents](#Chapter-14---Managing-Incidents)
- [Chapter 15 - Postmortem Culture](#Chapter-15---Postmortem-Culture)
- [Chapter 16 - Tracking Outages](#Chapter-16---Tracking-Outages)
- [Chapter 17 - Testing for Reliability](#Chapter-17---Testing-for-Reliability)
- [Chapter 18 - Software Engineering in SRE](#Chapter-18---Software-Engineering-in-SRE)
- [Chapter 19 - Load Balancing at the Frontend](#Chapter-19---Load-Balancing-at-the-Frontend)
- [Chapter 20 - Load Balancing in the Datacenter](#Chapter-20---Load-Balancing-in-the-Datacenter)

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

## Chapter 7 - The Evolution of Automatioon at Google

### The Value of Automation

- Consistency
- A platform that can be extended, applied to more systems, or spun out for profit. A platform also centralizes mistakes.
- Faster repairs i.e., reduced MTTR
- Faster action
- Time saving

### The Value for Google SRE

- For large services, Google does not have the time to hand-hold services.
- Platform-based approach is required for manageability and scalability.

### The Use Cases for Automation

- Example use cases:
    * User account creation
    * Cluster turnup/turndown for services
    * Software/hardware installation
    * Rollouts of new software
    * Runtime config changes

### Hierarchy of Automation Classes

- No automation
- Externally maintained system-specific automation
    * SRE has a failover script locally
- Externally maintained generic automation
    * SRE adds database support to a generic failover script everyone uses
- Internally maintained system-specific automation
    * Database ships with its own failover script
- Systems that don't need any automation
    * Database notices prooblems and fails over withoout human intervention

### Automate All the Things

- First example:
    * Migrating MySQL into Borg
        + Eliminated machine/replica maintenance
        + Enable bin-packing of multiple MySQL instances on the same machine

### Detecting Inconsistencies with Prodtest

- ProdTest exteended Python unit test to allow for unit testing of real-world services.
- Set up a chain of tests and a failure in one test would quickly abort.

## Chapter 8 - Release Engineering

- Solid understanding of source code management, compilers, build configs, automated build tools, package managers and installers.
- How software is stored in repo, build rules for compilation, testing, packaging and deployment.

### Role of a Release Engineer

- Ensure projects released using consistent and repeatable methodologies.

### Philosophy

- Self-service model: dev teams should control and run their own release process
    * Projects automatically built and released using automated tools.
- High velocity: Push on green to deploy every build that passes all tests.
- Hermetic builds: ensure consistency and reliability

### Enforcement of Policies and Procedures

- Gated operations include:
    * Approoving source code changes
    * Specifying actions for release
    * Deploying a new release

### Continuous Build and Deployment

- Google automated release system is called Rapid.
- Blaze is Google's build tool of choice.
    * Devs use build to define build targets and dependencies.
    * Binaries include build date, revision number, build identifier.
- All code checked into mainline
    * Most projects do not release from mainline.
    * Branch from mainline at specific revision and merge changes back into mainline.
    * Bug fixes submitted to mainline and cherry-picked into the branch.
    * This prevents picking up unrelated changes to the mainline since the original build occurred.
- Continuous test system runs unit tests against code in the mainline each time a change is submitted.
- Software is distributed to production machines using Midas Package Manager.

### Deployment

- Rapid used for deployments.
    * Update Borg jobs to use newly built MPM packages.
- Sisyphus used for more complicated deployments.
    * General purpose rollout framework.

### Configuration Management

- Use the mainline for configuration.
    * Binary releases and config changes are decoupled.
    * This technique often leads to skew between checked-in version of coonfig files and running version.
- Include config files and binaries in same MPM package.
    * Limits flexibility by binding binary and config.
    * Simplifies the deployment.
- Package config files into MPM configuration packages.
- Read config files from an external store.
- Project owners should decide which works best on a case-by-case basis.

## Chapter 9 - Simplicity

### System Stability Versus Agility

- SREs create procedures, practices, tools to make software more reliable
- SREs ensure this work has as little impact on dev agility as possible

### The Virtue of Boring

- SRE teams should push back when accidental complexity is added to systems which they are responsible
- SRE teams should constantly strive to eliminate complexity in systems they onboard

### I Won't Give up my Code

- SRE promotes practices that makes all code have an essential purpose

### Negative Lines of Code Metric

- Avoid software bloat where software become slower over time as a result of constant additional features

### Minimal APIs

- Write clear, minimal APIs

### Modularity

- Want ability to make changes to parts of the system in isolatioon is essential to creating a supportable system

### Release Simplicity

- Release in smaller batches to move faster with more confidence

### A Simple Conclusion

- Software simplicity is a prerequisite to reliability

## Chapter 10 - Practical Alerting

### Time-Series Monitoring Outside of Google

- Borgmon relies on a common data exposition format enabling mass data collection with low overheads
- Data used for rendering charts and creating alerts
- Scraper Borgmon feed into cluster-level Borgmon

### Instrumentation of Applications

- `/varz` HTTP handler lists all exported variables in plain text

### Exporting Variables

- Each major language used at Google has an implemnetation of the exported variable interface

### Collection of Exported Data

- Service discovery allows monitoring to scale
- Borgmon fetches `/varz` URI on each target, decodes and stores the values in memory

### Storage in the Time-Series Arena

- Data have form (timestamp, value), stored in chronological lists called time-series, named by a set of labels
- For example http_requests time-series has dimensions (time step, host id)
- Garbage collector expires the oldest entries once the time-series arena is full
- Typically about 12 hours of data is kept (can fit 1 million unique time-series for 12 hours at 1-minute intervals using 17GB RAM)

### Labels and Vectors

- `{var=http_requests,job=webserver,instance=host0:80,service=web,zone=us-west}` is an example vatriable expression to get a time-series

### Rule Evaluation

- Example:
    * Create alert when web server cluster serves more errors as a percent of requests than normal
    * Non-200 responses divided by sum of requests over all tasks in cluster
    * Procedure:
        1. Aggregate rates of response codes across all tasks, outputting a vector of rates at that point in time
        2. Compute total error rate, outputting a single value for the cluster at that point in time
        3. Compute cluster-wide ratio of errors to requests, dividing the total error rate by the rate oof requests that arrived, outputting single value for the cluster at that point in time
- Borgmon has nearly identical syntax to Prometheus

### Alerting

- When alerting rule is evaluated, result is either true (alert is triggered) or false
- Borgmon connected to Alertmanager which receives Alert RPCs when rule first triggers then again when the alert is considered to be firing

### Sharding the Monitoring Topology

- Multiple DC scraping Borgmon in each cluster
- One datacenter Borgmon per cluster sending data to permanent storage and alert manager
- Global Borgmon in selected clusters sending data to alert manager

### Black-Box Monitoring

- Borgmon is white-box monitoring
- White-box monitoring does not provide a full picture e.g., queries that never make it due to a DNS error are invisible
- Use Prober which runs a protocol check against a target and reports success or failure
    * Can send alerts directly to Alertmanager

## Chapter 11 Being On-Call

### Life of an On-Call Engineer

- Take care of operations by managing outages and performing production changes.
- Typically response times are 5 minutes for user-facing and 30 minutes for less sensitive systems.
- On-call engineer receives and acknowledges page and then triages the problem, possibly involving other engineers.
- Non-paging events can be handle by on-call engineers during business hours.
    * Take priority over project work.

### Balanced On-Call

- Quantity is the percent of time spent by engineers on on-call duties.
- Quality is the number of incidents that ooccur during on-call.

### Balance in Quantity

- 50% of time engineering, remainder no more than 25% on call, 25% on operational, non-project work.

### Balance in Quality

- On average, dealing with tasks involved with an on-call incident (RCA, remediation, postmortem) takes 6 hours.

### Compensation

- Google offers cash compensation, capped at some proportion of overall salary.

### Feeling Safe

- Important on-call resources:
    * Clear escalation paths.
    * Well defined incident management procedures.
    * Blameless postmortem culture.

### Operational Overload

- Paging alerts should be aligned with symptoms that threaten a service's SLO.
- All paging alerts should be actionable.
- SRE have option to give the pager back to dev team until standards of SRE team is met.

### Operational Underload

- To ensure continual practice, exercises can be performed to hone troubleshooting and knowledge of the system.

## Chapter 12 - Effective Troubleshooting

- SREs need to knoow how the system is designed and built.

### Theory

- We iteratively hypothesize potential causes for failure and try to test those hypotheses.
- Steps:
    1. Problem report
    2. Triage
    3. Examine
    4. Diagnose
    5. Test/treat
    6. Cure
- Pitfalls:
    * Looking at irrelevant symptoms
    * Misunderstanding system metrics
    * Misunderstanding how to change the system to test hypotheses
    * Coming up with improbable theories or latching onto past events

### In Practice

- Problem report e.g., automated alert or ticket
    * Should give the expected and actual behavior
    * Should give how to reproduce the behavior

### Triage

- Assess severity to determine level of response required
- Make the system work as well as it can under the circumstances
    * Diverting traffic from a broken cluster
    * Dropping traffic to precent a cascading failure
    * Disabling sub-systems to lighten the load

### Examine

- Examine each component's behavior
- Use monitoring system metrics
- Use logging, tracing requests throuogh the stack
- Exposing current state e.g., endpoints that show a sample of RPCs recently sent or received to understand how any one server is communicating with others without an architecture diagram

### Diagnose

- Develop plausible hypotheses
- Look at connections between components
- A malfunctiong system is still trying to do something so figure out what it is doing, why it is doing it and where its resources are being used
- Find what touoched it last e.g., a new version deployment or configuration change

### Test and Treat

- Find which factor is at the root of the problem
- Rule out hypotheses
    * Consider obvious first
    * Experiment may have misleading results due to confounding factors
    * Active tests may change future test results

### Negative Results are Magic

- Do not discount negative results
- They tell us something certain about production or the design space or the performance limit of a system
- Publish results

### Cure

- Often we can only find probable causal factors since systems are complex and reproducing the problem in a live environment may not be an option

### Making Troubleshooting Easier

- Build observability
- Design well-understood and observable interfaces between components

## Chapter 13 - Emergency Response

### What to Do when Systems Break

- Don't panic, pull in more people if necessary

### Test-Induced Emergency

- Proactive approach by breaking system on purpose, watch response and make changes to improve reliability

### Change-Induced Emergency

- Numerous tests on configuration changes to make sure they don't result in unexpected and undesired behavior

### Process-Induced Emergency

- Sometimes automation tools may not behave accordingly

### All Problems have Solutions

- Systems will break in unknown ways

### Learn from the Past. Don't Repeat it.

- Keep a history of outages
- Ask the big, even improbable questions
- Encourage proactive testing

## Chapter 14 - Managing Incidents

- Effective incident management key to limiting the disruption caused by an incident and restoring normal business operations.

### Unmanaged Incidents

- Common hazards that cause incidents to spiral out of control:
    * Sharp focus on the technical problem
    * Poor communication
    * Freelancing

### Elements of Incident Management Process

- A well designed incident management process has the following features:
    * Recursive separation of responsibilities
    * Incident command
    * Operational work
    * Communication
    * Planning
    * A recognized command post
    * Live incident state document
    * Clear, live handoff

## Chapter 15 - Postmortem Culture: Learning from Failure

- Primary goals of a postmoretm is to ensure incident is documentd
    * All rooot causes are understood
    * Effective preventive actions are put in place to reduce likelihood of recurrence
- Triggers for postmortem:
    * User affected
    * Data loss
    * On-call engineer intervention
    * Resolution time above threshold
    * Monitoring failure
- Blameless postmortem is key
- Encourage regular review sessions for postmortems
- Visibly reward people for doing the right thing
- Ask for feedback on postmortem effectiveness

## Chapter 16 - Tracking Outages

- Google tool Outalator receives all alerts sent by monitoring systems and allows us to annotate, group, and analyze data
- Get insight such as number of alerts per on-call shift, ratio of actionable/non-actionable alerts, what service creates the most toil

### Escalator

- If alert is not acknowledged, alert is escalated to next destination e.g., primary to secondary

### Outalator

- Stores original alert and allows incident annotation
- Slack for internal communication and updating status dashboard
    * Great places to hook into a system like Outalator

### Aggregation

- Group multiple alerts into a single incident

### Tagging

- General purpose tagging to add metadata to notifications

### Analysis

- Use historical information to find systemic, periodic problems

## Chapter 17 - Testing for Reliability

- SREs should quantify confidence in the systems they maintain
- Measured by both past (monitoring data) and future (testing) reliability

### Relationships Between Testing and MTTR

- MTTR measures how long it takes ops to fix a problem via rollback or another action
- If testing system identifies a bug before reaching production it is a zero MTTR bug
- The more bugs you find with zero MTTR, the higher Mean Time Between Failure (MTBF) experienced by users

### Types of Software Testing

- Traditional tests are more common to evaluate correctness of software offline during development
- Production tests are performed on live web service to determine if a deployed system is working

### Traditional Tests

- Unit tests
    * Assess a separable unit of software for correctness independent of the larger software system
- Integration tests
    * Tests on an assembled component to verify that it functions correctly
    * Dependency injection creates mocks of complex dependencies to test a component
- System tests
    * Largest scale test for an undeployed system
    * Tests end-to-end functionality of the system
    * Smoke tests: test simple, critical behavioro
    * Performance tests: ensures a system doesn't degrade over time
    * Regression tests: prevents bugs from sneaking back into codebase

### Production Tests

- Interact with live environment
- Rollouts entangle tests
    * During rollout, the entire production environment is intentionally not representative of any given version of a binary that's checked into source control
    * This can complicate test results
- Configuration tests
    * Config files should be version controlled
    * For each config while, a separate config test examines production to see how a particular binary is actually configured and reports discrepancies against that file
- Stress tests
    * SREs should understand limits of system and its components
    * Stress tests answer questions such as:
        + How full can a database get before failure
        + How many queries per second can be sent before overloaded
- Canary tests
    * Subset of servers is upgraded to a new version and left in incubation period
    * If passes quality assurance, release continues until all servers are upgraded
    * If things go awry modified servers are rolled back to known good state

### Creating a Test and Build Environment

- As an SRE for a built codebase, ask yourself:
    * Can you prioritize the codebase?
    * Are there particular classes or functions that are mission-critical?
    * Which APIs are teams integrating against?
- Document all reported bugs as test cases
- Set up testing infrastructure
- Set up a continuous build system that runs test every time code is submitted
- Use tools to visualize the level of test coverage needed

### Testing at Scale

- Unit tests have a short list of dependencies whereas a release test may depend on many moving parts
- Practical testing envs select branch points among versions and merges
- SRE tools also need to be tested
- Software that bypass usual heavily tested API could destroy a live service
- Automation tool testing is more subtle
    * Test whether internal state (seen through API) is constant across operation
- Disaster recovery tools can be designed to operate offline
    * Compute checkpoint state and push it to be loadable by existing non-disaster validation tools
- Statistical tests e.g., Chaos Monkey are not repeatable but may be useful for:
    * Providing log of all randomly selected actions
    * Refactor log as a release test
    * Variatioons in errors help pinpoint suspicious areas of the code
    * Later runs may demonstrate more severe failures leading to escalation of the bug severity
- Most tests are simple and give engineers interactive feedback before context switch
- Batch tests require orchestration between many binaries and do not offer interactive feedback; instead of context switch, tell engineer that the coode is not ready for review

## Chapter 18 - Software Engineering in SRE

- Examples include binary rollout mechanisms, monitoring
- SRE develop internal tools
- Staff SRE teams with a mix of traditional swe and system engineers
- Example: Auxom, SRE tool to automate capacity planning
    * Traditional capacity planning involved:
        1. Collect demand forcasts
        2. Devise build and allocation plans
        3. Review and sign off
        4. Deploy and configure resources
    * Traditional capacity planning easily disrupted by minor changes
        + Increase customer demand
        + Change in delicery date
    * Traditional capacity planning is laborious and imprecise
    * Solution is intent-based capacity planning
        + Specify the requirements not the implementation
        + Programmatically encode dependencies and parameters of a service's need
        + Use that encoding to auto-generate an allcoation plan that details which resources go to with service in which cluster
        + If demand changes, we auto-generate a new plan
    * Intent is rationale for how a service owner wants to run their service
    * Different degrees of flexibility:
        1. I want 50 cores in clusters X, Y and Z
        2. I want 50 cores in any 3 clusters
        3. I want to meet service demand in each geographic regioon and have `N+2` redundancy
        4. I want to run service at 5 nines of reliability
    * In order to capture a service's intent, we need:
        + Dependencies e.g., oother services, infrastructure
        + Performance metrics
        + Prioritization between services
    * Auxom configuration language engine takes in:
        1. Intent config (dependencies, constraints, priorities)
        2. Performance data
        3. Per-service demand forecast data
    * Auxom solver takes in:
        1. Auxom configuration language engine output
        2. Resource supply
        3. Resource pricing
    * Auxom solver outputs allocation plan
- Requirements and implementation
    * Don't focus on perfection of solution, instead iterate
    * Raise awareness and drive adoption
    * Identify appropriate customers
    * Design software to handle a myriad of input data sources

## Chapter 19 - Load Balancing at the Frontend

- Use traffic load balancing to decide which of the many machines in our datacenters will serve a particular request
- Two common scenarios:
    1. search request: want low latency; sent to nearest datacenter
    2. video upload: want high throughput; sent to under-utilized link to maximize throughput at expense of latency
- Within datacenter we want to distribute load to maximize utilizatioon

### Load Balancing Using DNS

- Return multiple A or AAAA records in DNS reply and let client pick an IP arbitrarily
- Usually a recursive DNS server between users and authoritative nameservers
    * Proxies user queries and acts as a caching layer
    * IP authoritative nameserver sees does not belong to the user, so the IP it provides is shortest distance for recursive resolver
    * EDNS0 extension sends information about client subnet too authoritative namserver so it can optimize for user
    * Cached responses are used within TTL
- Proximity may not always be the best route; must consider oother factors e.g., datacenter capacity, state of network connectivity, etc

### Load Balancing at the Virutal IP Address

- Most important part of VIP is the netowork load balancer
    * Receives packets and forwards them to one of the machines behind the VIP
- VIP strategies:
    1. Send to the least loaded backend; breaks down for stateful protocols; use consistent hashing to keep track of which machine belongs to connections
- Current VIP load baalncing solution uses packet encapsulation
    * NLB puts forwarded packet into another IP packet with Generic Routing Encapsulation with backend address as destination; NLB and backend no longer need to be in the same broadcast domain

## Chapter 20 - Load Balancing in the Datacenter

### Ideal Case

- Ideally, load for a given service is spread evenly over all backend tasks
- Send traffic to datacenter until the moost loaded task reaches its capacity limit

### Identifying Bad Tasks

- If a given backend tasks becomes overloaded and requests start piling up, clients will avoid that backend, and workload spreads
- In reality, this only protects against extreme forms of overload; easy for backends to become overloaded before limit is reached
- From client perspective, a backend task can be in the following states:
    1. Healthy
    2. Refusing connections
    3. Lame duck: backend is listening oon port and can serve but is explicitly asking clients to stop sending requests
- Main advantage of lame duck state is that it simplifies clean shutdown which avoids serving errors to unlucky requests that are assigned to backend tasks that are shutting down
- Shutting down a backend tasks with active requests without serving errors:
    1. Job scheduler sends SIGTERM to backend task
    2. Backend task enters lame duck state so clients stop sending new requests to it
    3. Any ongoing request before going into lame duck state is executed normally
    4. As responses go back to clients, number of active requests against backend gradually decreases to zeroo
    5. Backend task exits cleanly or is killed by scheduler