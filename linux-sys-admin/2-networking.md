## Table of Contents
[Chapter 14 - TCP/IP Networking](#Chapter-14---TCP/IP-Networking)

## Chapter 14 - TCP/IP Networking

### TCP/IP and Its Relationship too the Internet

- TCP/IP is an open and non-proprietary protocol suite.
- Requests for Coomments (RFCs) standardize internet protocols.
- Relevant RFCs:
    * RFC791: Internet Protocol (IP)
        + Routes data from one machine to another.
    * RFC792: Internet Control Message Protocol (ICMP)
        + Low level support for IP for debugging.
    * RFC826: Address Resolution Protocol (ARP)
        + Translates IP addresses to hardware addresses.
    * RFC768: User Datagram Protocol (UDP)
        + Unverified one-way data delivery.
    * RFC793: Transmission Control Protocol (TCP)
        + Reliable, full duplex, error-corrected conversations.
- TCP/IP layering model
    1. Application layer
        * ARP (goes to ARP)
        * SSH, FTP, HTTP (goes to TCP)
        * DNS, gaming (goes to UDP)
        * traceroute (goes to UDP or ICMP)
    2. Transport layer
        * TCP (goes to IP)
        * UDP (goes to IP)
    3. Network layer
        * IP (goes to ARP, device drivers)
        * ICMP (goes horizontally to IP)
    4. Link layer
        * ARP
        * Device drivers
    5. Physical layer
        * Optical fiber
        * Radio waves
- Data travels on a network in packets.
- Each packet has a header and a payload.
    * Header tells where packet came from and where it is going.
    * Payload is the data to be transferred.
- Primitive data unit is called:
    * A segment in the TCP layer.
    * A packet in the IP layer.
    * A frame in the link layer.
- Each protocol adds its own header to the packet.
    * This nesting is known as encapsulation.
    * On receiving machine, encapsulation is reversed.
- Link layer adds headers to packets and separates them so receiver can tell where one stops and another begins.
    * This process is known as framing.
- Maximum transfer unit (MTU) over ethernet is 1500 bytes.
- IP layer splits packets to conform to the MTU.
- TCP protocol does path MTU discovery automatically to find hop with the smallest MTU to determine how small packets must be sized to reach the destination.
- Use `ifconfig` to set an interface's MTU.

### Packet Addressing

- Several packet addressing schemes:
1. MAC addresses for hardware.
2. IPv4 and IPv6 network addresses for software.
3. Hostnames for use by people.
- IP addresses identify network interfaces, not machines!
- MAC addresses are 2-digit hex bytes e.g., `00:50:8D:9A:3B:DF`.
- IP addresses are universally unique and hardware independent.
- IP to hardware address done at the link layer.
- One or more hostnames can map too IP addresses using `/etc/hosts`, LDAP or DNS.
- Port is a 16-bit number that supplments an IP to specify a particular communication channel.
- Services are bound to certain ports in `/etc/services`.
- Address types includes unicast, multicast, broadcast, and anycast.