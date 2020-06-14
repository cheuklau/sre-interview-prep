## Table of Contents
- [Chapter 1 - Introduction](#Chapter 1 - Introduction)

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

