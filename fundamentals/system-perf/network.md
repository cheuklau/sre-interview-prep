# Network

## Methodology

### Tools Method

- `netstat -s`: find high rate of retransmits
- `netstat -i`: interface error counters
- `ifconfig`: check errors, dropped and overruns
- `vp`: check rate of bytes transmitted and received
- `tcpdump`: see who is using network and identify unnecessary work
- `dtrace`: packet inspection between app and wire

### USE Method

- Utilization: time interface busy sending or receiving frames
- Saturation: degree of extra queueing, buffering or blocking due to fully utilized interface
- Error:
    * For receive, check bad checksum, frame too oshort/long, collisions
    * For transmit: check late collisions

### Workload Characterization

- Network interface throughput: RX and TX, bytes per second
- Network interface IOPS: RX and TX, frames per second
- TCP connection rate: active and passive connections per second
- Questions to ask:
    1. Ave packet size received and transmitted
    2. Protocol? UDP or TCP?
    3. Which ports active? Bytes per second, connections per second?
    4. Which processes actively using the network

### Latency Analysis

- Network latencies caused by:
    1. System call send/receive latency
    2. System call connect latency
    3. TCP connection initialization time
    4. TCP first-byte latency
    5. TCP connection duration
    6. TCP retransmits
    7. Network round-trip time
    8. Interrupt latency: time from network controller interrupt for a received packet to when it is serviced by the kernel
    9. Inter-stack latency

### Performance monitoring

- Look for
    * Throughput
    * Connections
    * Errors e.g., drop packets counters
    * TCP retransmits
    * TCP out-of-order packets

### Packet Sniffing

- Capture packets from network so their protoocol headers and data can be inspected on a packet level
    * Timestamp
    * Entire packet including protocool headers, partial or full payload data
    * Metadata e.g., number of packets, number of drops

### TCP Analysis

- Usage of TCP send/receive buffers
- Usage of TCP backlog queues
- Kernel drops due to backlog queue being full
- Congestion window size
- SYNs received during a TCP TIME_WAIT interval


### Static Performance Tuning

- Number of network intefaces available for use?
- Max speed of network interfaces?
- MTU configured for network interfaces?
- Routing? Default gateway?
- How is DNS configured?
- Known issues with network device driver? Kernel TCP/IP stack?
