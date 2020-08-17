# What Happens When You Enter http://google.com/

## Parse URL

- Browser receives URL with protocol (HTTP) and resource (`/`)

## Check HSTS List

- Browser checks its preloaded HTTP Strict Transport Security (HSTS) list to see if it is a website that has to be requested via HTTPS
- If on list, browser sends request via HTTPS instead of HTTP

## DNS Lookup

- Browser checks if domain is in cache (`chrome://net-internals/#dns`)
- If not found, browser calls `gethostbyname` to do lookup
- `gethostbyname` checks if hostname can be resolved in `hosts` file
- If not found, then browser makes a request to DNS server typically the lcoal router or ISP's caching DNS server
- If DNS server is on same subnet, network library follows ARP process for DNS server
- If DNS server is on different subnet, network library follows ARP process for default gateway

## ARP Request

- To send Address Resolution Protocol (ARP) broadcast the network library needs target IP address and MAC address of the interface it will use to send out the ARP broadcast
- ARP cache checked for ARP entry for target IP
- If not in ARP cache, look up route table
- Network library sends a layer 2 ARP request:
```
Sender MAC: interface:mac:address:here
Sender IP: interface.ip.goes.here
Target MAC: FF:FF:FF:FF:FF:FF (Broadcast)
Target IP: target.ip.goes.here
```
- Router responds with an ARP reply:
```
Sender MAC: target:mac:address:here
Sender IP: target.ip.goes.here
Target MAC: interface:mac:address:here
Target IP: interface.ip.goes.here
```
- Now network library has IP address of either DNS server or default gateway
- DNS client establishes socket to UDP port 53 on the DNS server
- If local/ISP DNS server does not have it, then a recursive search is requested that flows up the list of DNS servers until the SOA is reached

## Opening of Socket

- Once browser knows IP of destination server, it calls `socket` and requests a TCP socket stream `SOCK_STREAM`
    * Request passed to Transport Layer where TCP segment is crafted
        + Destination port added too header
        + Source port chosen by kernel's dynamic port range
    * Network layer adds an additioonal IP header
        + IP address of the destination server as well as IP of current machine inserted to form a packet
    * Link layer adds frame header that includes MAC address of machine's NIC and MAC address of gateway (i.e., local router)
        + Note that MAC address of gateway was obtained early by ARP request
- Packet transmitted through physical medium
    * Modem converts 1s and 0s to analog signal for transmission over cable
    * Packet reaches router managing local subnet
    * Travel to the border routers, other Autonomous Systems, and finally to destination server
    * Each router along the way extracts destinatioon IP from IP header and routes it to the next hop
    * TTL in IP header decremented by one for each router it passes
    * Packet dropped if TTL reaches zeroo
- Send and receive happens multiple times following TCP connection flow
    * Client chooose initial sequence number (ISN) and sends packet to the server with SYN bit set
    * Server receives SYN and:
        1. Server chooses its own ISN
        2. Server copies the client ISN + 1 to its ACK field and adds ACK flag to indicate it is acknowledging receipt of first packet
    * Client acknowledges connection by sending a packet
        1. Increases its own sequence number
        2. Increases receiver ack number
        3. Sends ACK
    * Data is transferred
        1. One side sends N data bytes, it increases SEQ by that number
        2. Other side acknowledges receipt of packet by sending ACK packet with ACK value equal to olast receieved SEQ
    * To close connection
        1. Closer sends FIN packet
        2. Other side ACKs FIN packet and sends its own FIN
        3. Closer acknowledges other side's FIN with an ACK

## TLS Handshake

- Client sends `ClientHello` to server with TLS version, cipher algorithms and compression methods
- Server replies with `ServerHello` to client with TLS version, cipher and compression methods selected
    * Also includes server's public certificate signed by a CA
    * Certificate contains a public key that will be used by client to encrypt rest of handshake until a symmetric key is agreed upon
- Client verifies server certificate against list of trusted CAs. If trust established:
    * Client generates string of random bytes and encrypts it with server's public key
- Server decrypts random bytes using its private key and uses these bytes to generate its own copy of the symmetric key
- Client sends a `Finished` message to server, encrypting hash of tranmission up to this point with symmetric key
- Server generates its own hash then decrypts the client-send hash to verify it matches, if so it sendsession trs its own `Finished` message to client
- Now TLS session transmits application (HTTP) data encrypted with the agreed upon symmetric key

## HTTP Protocol

- Client sends a request to server of the form:
```
GET / HTTP/1.1
Host: google.com
Connection: close
[other headers]
```
- Server responds with a response of the form:
```
200 OK
[response headers]
```
Along with a payload of the HTML content of `www.google.com`
- After parsing the HTML, the web broowser and server repeats this process for every resuorce (image, CSS, favicon.ico, etc) referenced by HTML page except instead of `GET / HTTP/1.1` it will be `GET /$(URL relative to www.google.com) HTTP/1.1`

## HTTP Server Request Handle

- HTTPD server handles requests on the server side
- Most common HTTPD servers are apache and Nginx
- Process:
    1. HTTPD receives the request
    2. Server breaks doown the request to the following parameters:
        * HTTP request method (GET, HEAD, POST, PUT, PATCH, DELETE, CONNECT, OPTIONS, TRACE)
        * Domain (i.e., google.com)
        * Requested path/page (i.e., in this case `/`)
    3. Server verifies that there is a virtual host on the server that corresponds with google.com
    4. Server verifies that google.com can accept GET requests
    5. Server verifies client is allwoed to use this method (by IP, authentication, etc)
    6. If server has a rewrite moodule then it tries to match the request against a rule
    7. Server pull content that corresponds with the request
    8. Server parses the file; if running PHP then the server uses PHP to interpret the file and streams the output to the client

## Behind the Scenes of the Browser

- Once server supplies resources to othe browser, it will parse (HTML, CSS, JS) and render the page