# Lecture 33

## Protocols in TCP/IP Suite

- Application layer (user space)
    * Consists of process that use the network
    * Provides programming interface used for building a program
    * Protocols include HTTP, telnet, ftp, smtp, ssh
    * Addresses are string based URIs (URL, URN)
- Transport layer (kernel space)
    * Provides host to host communication
    * Protocols used are TCP (`SOCK_STREAM`), UDP (`SOCK_DGRAM`), RAW (`SOCK_RAW`)
    * 16 bit port numbers are used for addressing
- Internet layer (kernel space)
    * Break data into fragments small enough for transmission via link layer
    * Routing data across internet
    * Protocols are IP, ICMP, IGMP
    * IPv4 and IPv6 are used for addressing
- Link layer / physical layer (hardware)
    * Place packets on the network medium and receiving packets off the network medium
    * Protocols used are thetnet, token ring, FDDI, ISDN, SONET, ATM
    * 48 bit mac addresses used for addressing

## Addressing on the Application Layer

- A host on the internet can be uniquely identified by a fully qualified domain name (FQDN) having two parts:
    1. hostname
    2. domain-name
    * Combined as `hostname.domain-name`
- A central authority (`iana.org`) manages the assignment of domain names to organizations which can be two or more strings separated by a period
    * Mapping of these hostnames to IP addresses is kept in a hierarchical decentralized database
    * Service that performs a lookup is called DNS/BIND
- Organization can add prefixes to its domain name to define its hosts:
    * example: `pucit.pu.edu.pk` where `pucit` is the hostname
- Organization can add suffixes to its domain name to define its resources:
    * example: `pucit.pu.edu.uk/academics/timetable-pucit.html`
- URL: Uniform resource locator is a string of characters used to identify a resource located on a spherici host on a specific domain on the internet
    * `protocol://hostname.domain-name[:port]/pathtoresource`
    * `http://pucit.pu.edu.pk:80/acamdeics/timetable-pucit.html`

## Addressing on the Transport Layer

- Transport layer addresses are called port numbers
    * 16 bit integer used to identify a specific process to whic anetwork message is to be forwarded when it arrives at a host
    * there may be a machine running both http and ssh
    * http process will be listening on port 80 whereas ssh process will be listening on port 22
- Well known / reserved ports (0 to 1023)
    * Permantenty assigned to specific applications
    * ssh runs on port 22
    * Well known ports are assigned numbers by a central authority   (IANA)
- Registered ports (1024 to 49151)
    * IANA also records registered ports which are alllocated to application developers on a less stringent basis
- Dynamic/private/ephemeeral ports (49152 to 65535)
    * IANA specifies these ports as dynamic or private with intention that these ports can be used by local applications
    * If an application doesn't select a particular port (i.e., `bind()` its socket to a particular port) then TCP and UDP will assign a unique ephemeral port (short-lived) number to the socket
- `cat /etc/services` for details on port assignments

## Class Full Addresseing on the Internet Layer (IPv4)

- Class A IP address
    * Total addresses: 2^7 - 2 (1.0.0.0 to 126.0.0.0)
    * Hosts per address: 2^24 0 2
    * Subnet mask: 255.0.0.0/8
- Class B IP address
    * Total addresses: 2^14 - 2 (128.0.0.0 to 191.255.0.0)
    * Hosts per address: 2^16 - 2
    * Subnet mask: 255.255.0.0/16
- Class C IP address
    * Total addresses: 2^21 - 2 (192.0.0.0 to 192.255.255.0)
    * Hosts per address: 2^8 - 2
    * Subnet mask: 255.255.255.0/24
- There are 4 billion IPv4 addresses and this address space has gone full
    * ICANN is using a scheme called classless internetwork domain routing (CIDR) which has significantly extended the useful life of IPv4
    * ICANN has taken away many class A and class B addresses from organizations and is using them to create IP addresses with fewer number of host computers and then issuing these classless IP addresses to organizations
    * In `/28` networks ICANN controls the leftmost 28 bits for th enetwork part with remainingn 4 bits under the control of the organization it is issued to
        + This gives organization 2^4 - 2 IP addresses to use as hosts
        + If the organization is using more than 14 hosts then they can use private IP addresses

## Private IP addresses (IPv4)

- IETF has designed three address ranges as private
    * Non-routable and can only be used either on a fully disconnected network or on a network behind a firewall
- Firewalls translate private IP addresses to public IP addresses using a process called network address translation (NAT)
- NAT allows a single device called the gateway computer (router) having a public IP address to act as an agent between the internet and private network
    * This means that a single public IP addreass can represent an entire group of compjuters
    * CIDR and NAT has significantly extended the useful life of IPv4

## Addressing on the Physical Layer

- 48 bit addresses used on the physcical layer are called MAC address
- Before manufacturer can build ethernet products, it asks IEEE to assign the manufacturer a universally unique 3 byte code called the organizationally unique identifier (OUI)
- Manufactorer agrees to give all ethernet products a MAC address that begins with its assigned 3 byte OUI
- Manufacturer also assigns a unique value for the least significant 3 bytes, a number that manufacturer has never used with that OUI thus making the address of theat device unique
- If destination IP address of a network message is not in the same local area network then the packet is sent to the configured gatwayw computer for routing
- If destination IP address of a network message is in the same local area network then the source computer uses Address Resolution Protocol to get the destination MAC address from the destination IP address

## Lab

- Setup
    * Host 1
        + Hostname: kali
        + OS: Kalo
        + IP: 192.168.100.21
    * Host 2
        + Hostname: win10
        + OS: Windows 10
        + IP: 192.168.100.22
    * Host 3
        + Hostname: ubuntuserver
        + OS: Ubuntu
        + IP: 192.168.100.20
    * All three hosts are connected via a virtual box network adaptor
        + Hostname: Arifs macbook pro
        + OS: Mac OS
        + IP: 192.168.100.6
    * Home router is IP: 192.168.100.1
- On Kali machine:
    * `ifconfig` to configure network interface
        + Shows active network interfaces
        + `eth0` with `inet 192.168.100.21`, `netmask`, `broadcast`
        + `route -n` to show the kernel IP routing table
            - `192.168.100.1` is the internet gateway (destination `0.0.0.0`)
- Similar for other servers
- On Windows machine
    * `ping 192.168.100.21`
        + Packet internet dropper - internet connectivity tool to check for connectivity
- On Kali machine
    * `ping 192.168.100.20`
    * Basically ping every other machine to check for connectivity
    * `cat /etc/hosts` shows that we have given IP to hostname mapping for other machines
    * Therefore `ping ubuntuserver` works
- Go to Ubuntu server
    * `less /etc/services` to show port numbers and transport protocol type of different application servicves e.g., `ssh 22/tcp`, `telnet 23/tcp`
    * telnet is unsecured allowing bi-directional communication on a given port
    * `netstat -ant | grep 22` to make sure port 22 is listening on the local server
- Go back to Kali
    * `ssh root@192.168.100.20` to ssh to ubuntu server
- Go back to ubuntu
    * `netstat -ant | grep 22` will now show the port is established with `192.168.100.21:51208`
    * Port is also still listening on port 22 for other servers
- Go back to Kali
    * `nc 192.168.100.20 13` to reach date time service running on ubuntu server
