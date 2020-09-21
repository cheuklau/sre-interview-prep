# Introduction to Neworking

## TCP/IP Model

- Physical
    * Represents physical devices that connect computers
- Data Link
    * Defines common way of interpreting signals so devices can communicate
    * Example: ethernet
- Network
    * Allows different networks to communicate with each other
    * Responsible for making sure data gets to correct host
    * Example: Internet protocol
- Transport
    * Example: TCP, UDP
    * Responsible for making sure data gets to correct applications
- Application
    * Example: HTTP, SSH, DNS

## Basics of Networking Devices

- Cables
    * Connect devices to each other allowing data to be sent over them
    * Types:
        + Copper - changes voltage between two values to represent binary (Cat5, Cat5e, Cat6e)
            - Newer cable versions reduce cross talk
        + Fiber - contain individual optical fibers that transport beams of flight to represent binary
            - Better for operating in e-m fields
            - Less data loss over distances than copper
- Hubs and Switches
    * Hub - physical layer device that allows communication of many systems at once
        + Causes a lot of noise since each server has to determine whether the communciation is meant for them
        + Collision domain - network segment where only one device can communicate at a time
        + If multiple systems try sending data at same time, electrical signals can conflict
        + In general, hubs are not used anymore due to above problems
    * Switches - Connect many devices to it
        + Difference is that switch is a layer 2 (data link) device
        + Switch inspects contents of the packet and decide which system it is intended for and only sends the packet to that system
        + Higher overall throughput and less retransmits
- Routers
    * Device that knows how to forward data between independent device
    * Router is a layer 3 (network layer) device
    * Router inspects IP data to see where to send things
    * Take traffic from inside LAN and forward it to ISP then a more sophisticated router takes over which forms the backbone of the internet (core ISP router)
    * Routers share data with each other using Border Gateway Protocol (BGP) which lets them learn about th emost optimal paths to forward traffic
- Servers and Clients
    * Server - provides data to something requesting data
    * Client - receives data from servers

## The Physical Layer

- Moves 1's and 0's from one host to another
- Bit: smallest representation of data computer can understand (1s and 0s)
- Standard copper cable will use modulation (way of varying voltage of charge across cable)
    + Line coding where digital data is encoded into a digital singal and decoded on the other end
- Twisted pair cable
    + Pairs of copper wires twisted together
    + Twisted prevents e-m interferance and cross talk
    + Duplex communicatin: info can flow in both directions
    + Full duplex: info can flow in both directions at the same time
    + Half duplex: only one device can communicate at a time
- Network ports and patch ports
    + RJ45 is the most common plug
    + Network ports: directly attached to devices that make up a network
        * Link light: lit when properly connected
        * Activity light: when data is transmitted

## The Data Link Layer

- Most common protocol is ethernet
    * Abstract away physical layer from above layers
- CSMA/CD
    * Used to determine when communciation channels are clear and when a device is free to transmit data
- MAC address
    * Globally unique ID attached to a network interface
    * 48-bit number represented by six groupings of two hexadecimal numbers
    * Hexadecimal represents numbers with 16 digits
    * Octet: any number that can be represented by 8 bits
    * First 3 octets are organizationally unique identifier
    * Last 3 octets assigned any way manufacturer likes, but must be only assigned once
    * Ethernet uses MAC addresses to ensure data it sends has both an address for the machine that sent transmission as well as the one the transmission was intended for
- Unicast, multicast, broadcast
    * One device to another deivce is a unicast transmission
        + If least significant bit in first octet is set to zero, then it means the ethernet frame is only intended for one destination
        + If set to one, then you have a multicast frame (sent to group of hosts on a local network)
        + Broadcast sent to all hosts on local network
            * Used so devices can learn more about each other e.g., address resolution protocol
            * Use broadcast address FF:FF:FF:FF:FF:FF
- Ethernet frame
    * Data packet: all-encompassing term that represents any single set of binary data sent across a network link
    * Ethernet frame: highly structued collection of info presented in a specific order
    * Ethernet frame:
        1. Preamble: 8 bytes, split into two sections
            * Buffer between frames
            * Start frame delimiter (SFD) - signals that preamble is over
        2. Destination address
            * Hardware address of intended recipeient
        3. Source address
            * Hardware address of originator
        4. VLAN Tag
        5. Ether-type
            * 16 bits, describes the protocol of the contents of frame
        6. Payload
            * Actual data being transported (everything that isn't a header)
            * up to 1500 bytes long
            * Contains all data from higher layers
        7. FCS
            * 4 byte number that represents a checksum value for frame
            * Calculated by performing a cyclical redundancy check against the frame
                + Important concept for data integrity
                + Mathematical transformation to create a number that represents a larger set of data
                + Receiving host can confirm that it received uncorrupted data

## Network Layer

- IPv4 addresses
    * 32 bit number
    * Dotted decimal notation
    * Distributed in large sections to companies
    * IBM owns every since IP that starts with `9.x.x.x`
- Dynamic Host Control Protocol
    * Assigns dynamic address assigned to a server automatically
- Network layer
    * IP datagram - highly structured series of fields that are strictly deifined
    * Header
        + Version e.g., IPv4
        + Header length - 20bytes for IPv4
        + Service type - Details about quality of service (QoS)
            * Some IP datagrams may be more important than others
        + Total Length - total length of IP datagram
        + Identification - Used to group messages together
        + Flag - indicate if datagram is allowed to be fragmented
            * Fragmentation is process of taking a single IP datagram and splitting it up into several smaller datagrams
        + Fragmentation offset
        + TTL - how many router hops a datagram can traverse before it is thrown away
        + Protocol - which transport protocol is being used e.g., TCP or UDP
        + Header checksum - checksum of entire IP datagram header (similar to ethernet checksum)
        + Source IP address
        + Destination IP address
        + Options - set special characteristics for datagram mostly for testing purposes
        + Padding
    * Payload: contains all data from previous layers
- IP Address classes
    * Two sections: network ID, host ID
    * Address class ysstem defines how global IP address space is split up
    * Class A: first octet for network ID
        + 0-126, 16 million hosts
    * Class B: first two octets for network ID
        + 128-191, 64000 hosts
    * Class C: first three octets for network ID
        + 192-224, 254 hosts
- Address resolution protocol
    * Protocol used to discover hardware address of a node with a certain IP address
    * Device needs a destination MAC address
    * ARP table: list of IP addresses and MAC addresses associated with them
    * Example:
        1. Host A wants to send data to 10.20.30.40 but doesn't know the mac address
        2. Host A sends an ARP message to 10.20.30.40 which goes to all hosts on local network
        3. Host B with 10.20.30.40 IP address sends back an ARP response with its MAC address
        4. Now Host A can put that MAC address to its ARP table entry and subsequent ethernet frames will have the proper MAC address for that given IP address
    * ARP table entries expire after a short amount of time to ensure changes in network are accounted for
- Subnetting
    * Split up large network and split it up into subnets
    * Subnets have their own gateway routers serving as ingress and egress points
    * Subnet masks
        + Example: 10.0.1.10 can have:
            - 10.0 as network ID
            - 1 as subnet ID
            - 10 as host ID
    * Core routers only care about network ID
    * Subnet masks
        + Example: 9.100.100.100
        + In binary: 0000 1001.0110 0100.0110 0100.0110 0110
        + Subnet mask: 1111 1111.111 111.111 111.000 000 (255.255.255.0)
        + 1's represent the subnet ID
        + Only last octet represents host ID
        + Only 1 to 254 are for hosts since 255 is broadcast and 0 is never used
        + We can also rewrite above as /24 since the first 24 bits are part of subnet mask
    * Skipped rest of info on subnetting because I already know it
        + Basic binary math
        + CIDR notation

## Routing

- Basic Routing Concepts
    * Router: network device that forwards traffic based on destination address
    * General steps:
        1. Router receives data packet
        2. Router examines destination IP
        3. Router looks at routing table to determine which path is the quickest and forwards the packet along the path
- Routing tables
    * Four columns:
        1. Destination network
            * When router receives an incoming packet, it examines the destination IP and determines which network it belogns to
        2. Next hop
            * IP address of next router that should receive data intended for the destination network in question
        3. Total hops
            * Routers try to pick shortest possible paths to ensure fast delivery of data
            * Shortest possible path changes over time
            * For each next hop and each destination entwork, router has to keep track of how far away that destination is
        4. Interface
            * Know which interface it should forward based on destination IP
- Interior Gateway protocols
    * Routing protocols: routers speak to each to share info they may have
    * Routing protocols fall into two main categories:
        1. Interior gateway protocols:
            + Link-state
            + Distance-vector
        2. Exterior gateway protcols
    * Interior gateway protocols used by routers to share info within a single autonoous system
        + Autonomous system is collection of networks that fall under control of a single network operator
- Exterior gateway protocols
    * Used to communicate data between routers at edge of autonomous systems
    * Used to share information across different organizations
    * Core internet routers need to know about autonomous systems in orderf to properly forward traffic
    * Since autonomous systems are defined collections of networks, getting data to the edge router of an AS is the number one goal of core internet routers
    * IANA responsble for autonomous system number allocation
        + ASNs are numbers assigned to individual AS
        + Normally referred as just a singel decimal numbers
- Non-routable address space
    * IPv4 has 4 billion addresses which quickly getting used up
    * RFC 1918 (request for comments) outlined number of networks that would be non-routable
    * 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
    * Network address translation allows for computers on non-routable address space to communciatite with other devices on the internet

## Transport Layer

- Multiplexing means that nodes on the network have the ability to direct traffic toward many different receiving services
- Demultiplexing for receiving end: takes traffic aimed at the same node and delivering it to the proper receiving service
- Port: 16-bit number used to direct traffic to specific services runnin on a networked computer
- Different network services run while listening on specific ports for incomng requests
    * HTTP = 80
    * Ex: 10.1.1.100:80 (socket address or socket number)
    * FTP = 21
- TCP Segment dissection
    * Remember that IP datagram encapsulates a TCP segment
    * TCP segment made up of a TCP header and data section
    * Data section is just another payload area for where app layer places its data
    * TCP header has lots of fields:
        1. Source port: high-numbered port chosen from set of ephemeral port
            + Keeps a lot of outgoing ports separate
        2. Destination port: port of traffic service is intended for
        3. Sequence number
            + 32 bit number used to keep track of where a sequence of TCP segments this one is supposed to be
            + TCP splits data into many segments
            + Sequence number is used to keep track which segment out ogf many this particular segment might be
        4. Acknowledgement number
            + Nuimber of next expected segment
            + Sequence number of one and an ack number of two could be read as this is segment one expect segment two next
        5. Data offset
            + Communicates how long TCP header for segment is
            + Receivijng netwrok device understands where the actual data payload begins
        6. TCP control flags
        7. TCP window
            + Specifies range of sequence numbers that might be sent before an ack is required
        8. Checksum
            + Similar to checksum fields at IP adn thetnet level
            + Once all of this segment has been ingested by recipeint, checksum is calculate across entire sefment and compared to checksum in the header to make sure data has not been lost/corrupted
        9. Urgent pointer
            + Rarely used but is used for more complicated flow control protocols
        10. Options
            + Somtimes used for more complicated flow control protocols
        10. Padding
            + Ensures payload begins at expected location
- TCP control flags and three-way handshake
    * TCP establishes connections used to send long chains of segments of data
    * IP and ethernet just sends individual packets of data
    * TCP establishes connection through use of TCP control flags in a very specific order
    * Six TCP control flags
        1. URG: value of 1 indivcates this segment is considered urgent and that the urgent pointer field has more info about this (rarely used)
        2. ACK: acknowledge
            * Value of 1 means that ack number field should be examined
        3. PSH: push
            * Transmitting device wants the receiving device to push currently-buffered data to app on receiving end as soon as possible
        4. RST: reset
            * One of the sides in a TCP connection hasn't properly recovered from a series of missing/malformed segments
            * One of the partners is a TCP connection is saying let's start over from scratch
        5. SYN: synchronize
            * Used when first establishing a TCP connection
            * Make sure receiving end knows to examine the sequence number field
        6. FIN: finish
            * When set to one it means transmitting computer doesn't have any more data to tsend and connection can be closed
    * How TCP connection is established:
        1. Computer A sends TCP segment to computer B with SYN flag set
        2. Computer B responds with a TCP segment where both SYN and ACK are set
            + Computer B acknowledge's Computer A's sequence number
        3. Computer A responds again with just ACK which is saying I ack your ack, let's start sending data
        + Handshake ensures two devices are speaking the same protocol and will be able to understand each other
        + Once threeway handshakle complete, TCP connection is established
        + TCP connection in this established state is operating in full duplex
        + Each segment sent should be reponded to by TCP segment with ACK field set
    * Four-way terminate handshake happens to close the connection
        1. Computer ready to close conenction sends a FIN flag
        2. Other computer sends ACK flag
        3. Other computer also sends a FIN flag
        4. Original sender responds with ACK flag
- TCP socket states
    * Instantiation of an endpoint in a potential TCP connection
    * Require actual programs to instantiate them
    * You can send traffic to any port you want but you will only get a response if a program has opened a socvket on that port
    * TCP states:
        1. LISTEN (server)
            * TCP socket is ready and listening for incoming connections
        2. SYN_SENT (client)
            * Synch request has been sent but connection hasn't been established yet (client)
        3. SYN_RECEIVED (server)
            * Socket previously in a listen state has received a sync request and sent a SYN_ACK back
            * Has not received final ACK from client yet
        4. ESTABLISHED (client and server)
            * TCP connection is in working order and both sides free to send data to each other
        5. FIN_WAIT
            * FIN has been send but ACK from other end has not been received yet
        6. CLOSE_WAIT
            * Connection has been closed at TCP layer but app that opened the socket has not released its hold on the socket yet
        7. CLOSED
            * Connection has been fully terminated, no further communication possible
- Connection-oriented and connectionless protocols
    * TCP is a connection-oriented protocol
    * At the IP or ethernet level, if a checksum doesn't compute all data is just discartded
    * Up to TCP to determine when to resend this data
    * Since TCP expects an ack for every bit fo data it sends, it is in the best position to know what data successfully got delivered and can make the decision to resend a segment if needed
    * While TCP generally sends all segments in sequenetial order, they may not always arrive in that order
    * Sequence numbers allow for all of the data to be put back together in the right order
    * Connection-oriented protocols have a lot of overhead e.g., srtream of constant streams of acks, need to establish connection, tear down connection, etc
    * Connectionless protocols e.g., UDP doesn't rely on connections and does not support concept of acks
    * Just set a destination port and send the packet
    * Useful for messages that are unimportant e.g., streaming video (doesn't matter if a frame goes missing)
- Port assignments by IANA:
    * 1-1023: system ports for well-known netowrk services
    * 1024-49151: registered ports for network services that might not be as common as the system ports e.g., 3306 for many database apps
    * 49152-65535: ephemeral ports used for establishing outbound connections
- Firewalls
    * Firewall is a device that blocks traffic that meets a certain criteria
    * Can operate at many layers of the network:
        + Perform inspection of application layer traffic
        + Can block ranges of IP addresses
    * Most commonly used at the transport layer
        + Enables them to block traffic to certain ports while allowing traffic to other ports
        + Example: Only allow external traffic to enter port 80 of a webserver
    * Firewall is a network device
        + Smaller systems e.g., laptop just has it built into the same machine

## Application Layer

- Application layer
    * TCP segments have a generic data section which is contains the contents of data applciations
    * A lot of protocols used at the application layer
    * For web traffic, application layer protocol is HTTP
- Application layer and the OSI model
    * OSI model has two additional layers between transport and application layers
    * Fifth layer is the session layedr
        + Responsible for facilitating communication between actual applications and the transport layer
        + Part of the OS that takes the app layer data thats been encapulated from all of the layers below it and hands it off to the nextlayer in the OSI model, the presentation layer
    * Sixth layer is the presentation layer
        + Responsible for making sure that the unencapsulated application layer data is actually able to be understood by the application in question
        + This is the part of an OS that might handle encryption or compression of data

# Introduction to Network Services

## Name Resolution

- Domain name system (DNS)
    * Global and highly distributed network service that resolves strings of letters into IP addresses
    * IP address for a domain can changes all the time for a variety of reasons
    * Want to distribute servers around the world to decrease geograhic latency
    * DNS helps provides the above functionarlity i.e., if you are in region A, resolve to IP A, etc
- DNS is a system that converts domain names into IPs
- Name resolution is process of turning a doman name into an IP address
- Five primary types of DNS servers:
    1. Caching name servers (Provided by ISP or local network)
        + Store domain name lookups for a certain amount of time
        + Max time is TTL (time to live) set by owner of domain name
    2. Recursive name servers (provided by ISP or local network)
        + Usually same as caching name server
        + If it does not have the mapping cached, then it recursively asks root, TLD and authoritative name servers for the IP address mapping before returning answer to the client
    3. Root name servers
    4. TLD name servers
    5. Authoriative name servers
- Steps to perform a full lookup (no cache):
    1. Contact a root named server
        * 13 total
        * Responsible for directing queries towards the appropriate TLD name server
    2. TLD (top level domain)
        * represents the top of the hierarchical DNS name resolution system
        * Last part of any domain name e.g., www.facebook.com the `.com` portion is the TLD
    3. TLD server responds with authoritative name server to contact
    4. Authoritative name servers
        * Responsible for the last two parts of any domain name which is the resolution at which a single org may be responsible for DNS lookups
        * Provides the actual IP of the server in question
- Important to follow above to prevent malicious redirects
- Local system e.g., phone or laptop will also have its own temp DNS cache so it doesn't have to bother the local name server for every TCP connection either
- DNS uses UDP
    * A single DNS request/response can fit into a single UDP datagram
    * Requires only 8 packets:
        1. Client to local name server
        2. Local name server (acting as recursive name server) sends request to Root name server
        3. Root name server replies back with TLD
        4. Local name server sends request to TLD
        5. TLD replies back with authoritative
        6. Root name server sends request to authoritative
        7. Authoritative replies back with IP
        8. Local name server replies back to client with IP

## Name Resolution in Practice

- Common types of resource record types
    * A record
        + Point a certain domain name at a certain IPv4 IP address
        + A single domain name can have multiple A records allowing DNS round robin to balance traffic across multiple IPs
    * CNAME
        * Redirects traffic from one domain to anoer
        * Example microsoft.com to www.microsoft.com
    * MX
        * Redirects email traffic to correct servers
    * SRV
        * Define location of specific services
    * TXT
        * Text data
    * NS
    * SOA
- Anatomy of a domain name
    * www.google.com
        + `www`: sub-domain (i.e., host name)
        + `google`: domain name
            + Demarcates where control moves from a TLD name server to an authoritative name server
        + `com`: Top level domain
    * Combining above results in a fully-qualified domain name (FQDN)
    * Costs money to register a domain name with a registrar
    * Subdominas can be freely chosen and assigned by anyone who controls a registered domain
    * DNS can support up to 127 levels of domain in total for a single fully-qualified domain name
    * Each individual section can only be 63 characteers long
    * Complete FQDN limited to 255 characters
- Authoritative name server responsible for responding to a name resolution request for specific domains
    * Responsible for a specific DNS zone
    * DNS zones are a hierarchical concept
    * Root name servers responsible for root zone
    * Each TLD name server responsible for zone covering its specific TLD
    * Example:
        + Comany owns `largecompany.com` domain
        + 200 servers in three locations: LA, Paris, Shanghai
        + 600 A record to keep track of if configured as a single zone
        + Can split each location into its own zone:
            - `la.largecompnay.com`, `pa.largecompany.com`, `sh.largecompany.com`
        + Now have three subdomains each with their own DNS zones
        + Four authoritative name servers are now required
            - One for `largecompany.com` and three for the subdomains
    * Zones configured using zone files
        + Simple config files that declare resource records for a particular zone
        + Zone file contains a start of authority (SOA) resource record declatartion
        + SOA record declares the zone and name server that is authoritative for it
        + Also has NS records to indicate other name servers that may be responsible for this zone


## Dynamic Host Configuration Protocol

- Every modern TCP/IP based network needs four things configured:
    1. IP
    2. Subnet for local network
    3. Primary gateway
    4. Name server
- Tedious to configure on hundreds of servers
- The last three are typically same across all servers in local network
- The IP address needs to be different on every node in the network
- Dynamic Host Configuration Protocol handles that configuration
    * Application layer protocol that automates config of hosts on network
    * Machine queries DHCP server when it connects to network and receives all netwwork config in one go
    * DHCP sets aside a range of IPs for client devices
- DHCP dynamic allocation sets aside range of IP addresses for client devices
    * Issues one of those when a request comes in
    * IP of a computer could be different every time it connects to the network
- DHCP Automatic allocation assigns the same IP to the same machine each time if possible
- Fixed allocation
    * Requires a manually specified list of MAC addresses and their corresponding IPs
    * Used as a security measure to ensure only defices that have had their MAC address specifically configured at the DHCP server will be able to obtain an IP and communicate on the network
- DHCP discovery steps
    1. Server discovery step
        * DHCP client sends DHCP message (DHCPDISCOVER) out onto network
        * Since machine doesn't have an IP and doesn't know the IP of the HDCP server, this is a braoadcast message
        * DHCP listens on UDP port 67 and DHCP messages are always sent from port 68
        * TCP source = 67, TCP dest = 68
        * IP source = 0.0.0.0, IP dest = 255.255.255.255
        * DHCP server receives message and examines its own cofig to make a decision on IP address to offer
        * Response TCP source = 67, dest = 68
        * Response IP source = (DHCP IP), dest = 255.255.255.255
        * DHCPOFFER message reaches every machine
        * Original client would recognize this message was intended for itself beacuse the DHCPOFFER field that specifies the MAC address of the client that sent the DHCPDISCOVER message
        * Client processes DHCPOFFER to see what IP is being offered and respond with HDCPREQUEST
        * DHCP server responds with DHCPACK
        * Client netowrkign stack can now use the config information from DHCP server to set up its own network layer configuration
- Above process is a DHCP lease and will expire eventually at which point client needs to start process all over again

## Network Address Translation

- NAT takes one IP and translates it into another
- NAT allows a gateway (router or firewall) to rewrite source IP of an outgoing IP datagram while retaining the original IP in order to rewrite it into the response
- Example:
    * Network A has 10.1.1.0/24
    * Network B has 192.168.1.0/24
    * Between these two networks is a router with IP of 10.1.1.1 for network interface with Router A and 192.168.1.1 for network interface with Router B
    * Computer 1 on network A has IP of 10.1.1.100 and computer 2 on network B has IP of 192.168.1.100
    * Computer 1 wants to communicate with computer 2
    * Crafts packet at all layers and sends this to primary gateway (router between two networks)
    * Router configured to perform NAT for any outbound packets
    * Router rewrites the source IP address which in this instance becomes the router's IP on network B (192.168.1.1)
    * When datagram gets to computer 2, it will look like it originated from the router not from computer 1
    * Computer 2 crafts response and sends it back to the router
    * Router knows that this traffic is actually intended for computer 1 so it rewrites the defstination IP field before forwarding it along
    * NAT is hiding the IP of computer 1 from computer 2
        + This is IP masquerading (important security concept)
        + No one can establish a connection to your computer if they don't know what IP it has
    * We can actually have hundreds of computers on network A all of their IPs being translated by the router to its own
    * One-to-many NAT which is used by many LANs today
- Router uses port preservation
    * Technique where source port chosen by client is the same port used by the router
    * Outbound connections chooses a source port at random (ephemeral)
    * In simplest setuip, router setup to NAT outbound will just keep track of what this source port is and use that to direct traffic back to the right computer
    * However, it is possible for two computers on a network to both choose the same source port at the same time
        + When this happens, router normally selects an unused port at random to use instead
- Port forwarding is a technique where a sspecific destination ports can be configured to always be delievered to specific nodes
    * Allows for complete IP masquerading while still having services that can respond to incominng traffic
    * Example:
        + Clients just talk to router with 192.168.1.1 and traffic directed at port 80 on 192.168.1.1 will be forwarded to servers specifcally serving web requests e.g., 10.1.1.5
        + Response traffic would have source IP rewritten to look like the external IP of the router
    * With port fotwarind, traffic for multiple services could be aimed at the same external IP and therefore the same DNS name, but would get delivered to entirely different internal servers due to their different destination ports
- With NAT, we can have thousands of machines using non-routable address spaace
    * Use a single public IP so that all of those servers can still send traffic to and receive traffic from the internet

## VPNs and Proxies

- VPN
    * Allwos for extension of a private or local nework to hostthat might not work on the same local network
    * Tunnelling protocol provisioning access to something not localy available
    * VPN client establishes a VPN tunnel to their company network
    * Provisions computer with a virtual interface with an IP that matceshs the address space of the netwwork they've established a VPN connection to
    * By sending data out of this virtual interface, the computer can access internal resources as if it was physically connected to the private network
    * Most VPNs work by using payload section of transport layer to carry an encrypted payload that actually contains an entire second set of packets
    * The network, transport and app layers of a packet intend to traverse the remove network
    * Payload is carried to the VPN end point where all other layers are removed
    * Payload is unecncrypted, leaving VPN server with the top three layers of a new packet
    * This ggets encapsuatled with proper data link layer info and sent across the network
- VPNs require strict authentication procedures to ensure they can only be connected to by computers and users authorized to do so
    * Ex: MFA
- Proxy service
    * Acts on behalf of a client in order to access another service
    * Sit between clients and other services providing some additional benefits e.g., anonymity, security, contetnt filtering, increased performance, etc
    * Web proxies
        + Proxies built for web traffic
        + Org can direct all web traffic through it, allowing proxy server to retrieve the webpage data from the internet, and cache it
        + Above purpose not in use much more today due to dynamic nature of web content
        + More common use is to prevent someone from accessing sitesentirely
            * Inspect what data is requested and then allow or deny this request depending on the site accessed
        + Another use is reverse proxy
            * Appears as a single server to external clients but actually represents many servers living behind it
            * Act as a single front-end for many webservers living behind it
            * Reverse proxy distributed incoming requests to lots of different physical servers
        + Deal with decryption

## Troubleshooting

### Verifying Connectivity

- Need to diagnose connectivity issues as part of network troubleshooting
- Common problems:
    * Router doesn't know how to route to a destination
    * Certain port isn't reachable
    * TTL of an IP datagram expired
- ICMP (Internet Control Message Protocol) is used to troubleshoot these issues
- ICMP mainly used by router or remote host to communicate why a transmission has failed back to the origin of the transmission
- Makeup of an ICMP packet is simple:
    * Header with a few fields
        1. Type: specifies what type of message is being delivered e.g., destination unreachable, time exceeded, etc
        2. Code: indicates more specific reason for the message e.g., destination network unreachable, destination port unreachable
        3. Checksum
        4. Rest of header
        5. Payload for ICMP packet
            * Receipient of message uses this to know which of their transmissions cause the error being reported
            * Contains entire IP header and the first 8 bytes of the data payload section of offending packet
    * Data section use by host to figure out which transmissions generated the error
- Use `ping`
    * Let's you send a special type of ICMP message called an echo request
    * Asks destination "Hey, are you there?"
    * If destination is up and running and able to communcate on the network, it will send back an ICMP echo reply message type
- `ping <destination IP or FQDN>`
- Every line of output will display the address sending the ICMP echo reply, how long it took for the round trip communication, and the TTL remaining an dhow large the ICMP message is in byutes
- Once command ends, it will display % of packets transmitted and received, average round trip types
- Options include the number of requiests to send, how large the message should be and how quickly they should be sent
- Ping allows you to determine if you can reach a certain computer
- Need a way to determine where in the long chain of oruter hops the problems actually are
- Use `traceroute`
    * Discover paths between two nodes
    * Gives you info about each hop along the way
    * Manipulates TTL field at the IP level
    * Setting it to one for the first packet, then two, then three, and so on
    * Ensures that the first packet sent will be discarded by the first router hop
    * This results in an ICMP time exceeded message, the second packet will make to the second router, third to third and so on
    * This continues until packet reaaches destination
    * For each hop, traceroute sends three identical packets
    * Traceroute output:
        + Number of the hop
        + Round trip time for all three packet
        + IP of the device at each hop and a hostname if traceroute can resolve one
    * Linux `mtr` allows you collect aggregate data from traceroute
- We have used ping and traceroute to test connectivity at the network layer
- For transport layer we can use `netcat`
    * Run through the command `nc <host> <port>`
    * If fail, command will exit
    * If succeeds, you will see blinking cursor, waitign for more input
    * You can send application layered data to the listening service from keyboard
    * If only curious about status, just use `-Z` for zero input/output mode

### Digging into DNS

- `nslookup <hostname>`
    * Output displays what server was used to perform the request and the resolution result
    * `type=<resource record type>` to get specific record type
- ISP almost always gives you access to a recursive name server as part of the service it provides
    * These named servers are all you really need for computer to communciate with other devices on internet
    * However, most busineses run their own DNS servers
    * E.g., to resolve names of internal hosts
    * Some orgs run public DNS servers which are name servers set up so that anyone can use them for free
    * Handy technique for troubleshooting any kind of name resolution problems you might experience
    * IP address for Level 3's public DNS servers are 4.2.2.1 through 4.2.2.5
    * Google public DNS servers are 8.8.8.8 and 8.8.4.4
### The Cloud

### IPv6

