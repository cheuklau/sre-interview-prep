# Lecture 34

## Client Server Paradigm

- Server machine listening on different ports e.g., `SSH` on 22 and `DNS` on 53
- Client and servers can have:
    * Short connections: e.g., `echo` limited to 1 request and 1 response
    * Long connection: e.g., `ssh` message passing continues until client sends a quit message
- Server can be:
    * Stateful: remembers client data from one request to another
    * statless: keeps no state info

## What is a socket

- Socket is a communication end point to which an app can write data (to be sent to the underlying network) and from which an app can read data
- Process/app can be related or unrelated and may be executing on the same or different machiens
- From IPC point of view, socket is a full duplex IPC channeel that may be usedf for communication between related or unrelated proccesses executing on the same or differen machines
    * Both communicating processes need to create a socket to handle their side of communciation
    * Therefore, socket is called an endpoint of communication
- Available APIs for socket scommunication in Unix is: `socket` and `XTI/TLI`

## Types of sockets

- Two types of sockets
    1. Internet domain sockets
    2. Unix domain sockets
- Every socket implementation provides at least two types of sockets:
    1. TCP/stream sockets (`SOCK_STREAM`)
    2. UDP/datagram scokets (`SOCK_DGRAM`)

## Stream Sockets / TCP Sockets

- Stream sockets (`SOCK_STREAM`) provide a reliable, full-duplex stream-orientedf communciation channel
- Stream sockets are used to communciate between only two specific processes (point-to-point) and are described as connection oriented
    * Not supporting broadcasting or multicastintg
- Characteristics:
    * Full duplex
    * Stream oriented
    * Reliable
    * Error detection using checksum
    * Flow control using sliding window
    * Congestion control
        + Sender-side congestion window
        + Receiver-side advertised window

## System Call Graph: TCP Sockets

- Server
    * Calls `socket()` system call
    * Calls `bind()` to bind socket to a port number
    * Calls `listen()` notifies kernel of willingness to accept incoming connections
    * Calls `accept()` blocks until a conenction request arrives
- Client
    * Calls `socket()` system call
    * Calls `connect()` with address of the server
        + Established using 3-way handshake
- On server side, a new socket is now created called a data socket
    * Now data can be transmitted in both directions between the client and the server via `read()` and `write()` system calls
    * Can also use `send()` and `rcv()` which are socket specific system calls for reading and writing data
- Note that while the duplex communication is happening the master socket on the server is still listening for new connections
- Client calls `close()` system call to send an EOF notification to the server
- Server also `close()` its data socket

## Pictorial Representation of TCP Socket

- Server
    * Creates master socket using `socket()`
    * Creates a data socket on which data transfer will be carried out
        + Master socket is listening for new clients and will create subsequent data sockets for those connections
- Client
    * Creates socket using `socket()`
    * Connection created between client and server sockets

## Psuedocode: TCP Sockets

- Server
    * `socket()`
    * `bind()`
    * `listen()`
    ```
    while(1) {
        accept()
        while(client writes) {
            Read a request
            Perform requested action
            Send a reply
        }
        close client socket
    }
    close passive socket
    ```
- Client
    * `socket()`
    * `connect()`
    ```
    while(x) {
        write()
        read()
    }
    close()
    ```

## TCP Three Way Handshake

1. Server master socket in `LISTEN` state
2. Client calls `connect()`, TCP protocol sends a `SYN J` (sync packet) to the server
    * Client enters `SYN_SENT` state
3. Server receieves the packet via `accept()` and is now in `SYN_RECEIVED` state
4. Server sends back a `SYN K, ACK J+1` (sync ack packet) telling the client that it has received the original sync packet
5. Client receives packet and sends back a `ACK K+1` (sync ack packet)
6. Now both server and client knows connection has been established (both client and server are in `ESTABLISHED` state)
    * Server creates a data socket and sends back a new socket descriptor to be used for data transfer
7. Now reading and writing takes place between client socket and data socket on the server side

## TCP Four Way Connection Termination

1. Both server and client are in `ESTABLISHED` state
2. Client process calls `close()` (this is known as an active close)
    * TCP protocol sends a `FIN M` packet to the server
    * The client is now in `FIN-WAIT-1` state
3. Server receives the packet and performs a passive close
    * Server sends an `ACK M+1` packet in response to the client's `FIN M` packet
    * Server is now in `CLOSE-WAIT` state and client is in a `FIN-WAIT-2` state after receiving the `ACK M+1` packet
4. Server also sends back a `FIN N` packet
    * Server is now in `LAST-ACK` state
5. After client receives both `ACK M+1` and `FIN N` packets, it sends back an `ACK N+1` packet
    * Client is now in `TIME-WAIT` state
6. After server receives `ACK N+1` packet, it closes the data socket connection
7. After some time, the client also closes the socket connection

## Lab

- Setup is the same as previous lecture with kali, windows, ubuntu, macos and a home router acting as the internet gateway
- In ubuntu server:
    * `ifconfig` to show its own IP address
    * `systemctl status xinetd`, not running so `systemctl start xinetd.service`
    * `netstat -plant | grep xinetd` to view services running under `xinetd` which shows port 23 for telnet among other applications
- In kali server:
    * `ifconfig` to show its own IP address
    * `nc <ip of ubuntu server> 7` where `7` is the echo port
    * Type in a random string and it echoes back
    * `netstat -ant` to show active internet connections (servers and established)
- In ubuntu server:
    * `netstat -ant | grep 7` shows the connection with the kali machine on port 7 for the echo app; also shows process listening on port 7 which is the master socket
- In kali server:
    * `strace nc <ip of ubuntu server> 7` to see system calls that `nc` uses
        + `socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)=3` where `3` is the file descriptor
        + `connect(3, ..., sinport=htons(7), sin_addr=inet_addr("<IP of ubuntu>))` where `3` is the file descriptor associated with the socket we just created, note also that port and IP are listed here of the server machine
        + `read(0, "Learning is fun with Arif\n", 8192)=26` where `0` is the file descriptor for stdin
        + `write(3, "Learning is fun with Arif\n", 26)=26` where `3` is the file descriptor of the socket we made
        + `select(4, [0 3], NULL, NULL, NULL) = 1 (in [3])` where we are blocked by the descriptor `0` and `3`
        + `read(3, "Learning is fun with Arif\n", 8192)=26` where `3` is the file descriptor of the socket we made (read in what was passed back by the server `echo`)
        + `write(1, "Learning is fun with Arif\n", 26)=26` where `1` is the file descriptor for stdout
- Wireshark demo
    * Start wireshark on ubuntu server
    * On Kali, run `nc <ip of ubuntu server> 7` and enter `PUCIT` to have ubuntu server echo back
    * Go back to ubuntu server to look at what happened in wireshark
        + Filter for `tcp`
        + There are three panes:
            1. Shows time, source, destination, protocol, length and info for each packet captured
            2. After selecting a packet, second pane shows the packet headers
                * Frame
                    + Number of bytes on wire, number of bytes captured on interface 0
                * Ethernet
                    + Source and destination MAC addresses
                * Internet Protocol
                    + Source: <Kali IP address>, destination: <ubuntu IP address>
                * Transmission Control Protocol
                    + Source port: 37620, destination port: 7, seq: 1, ack: 1, len:6
                * Payload
                    + Echo data
            2. Third pane shows packet in both hex and ascii format
                * We can see `PUCIT` in plain text
        + We can see the TCP handshake happening at the beginning of Wireshark history
            * [SYN] from kali to ubuntu, [SYN, ACK] from ubuntu to kali, [ACK] from kali to ubuntu
        + We see the four way termination at the end of the Wireshark history
        + In between, we also see the request and response with the `ECHO` protocol
    * Now we repeat the above for a very large text file
        + We see that the data is broken up into multiple requests
        + The second packet is sent only after server has received acknowledgement
        + Whenever reading data from a TCP socket, you should always read in a loop until all of the data has been received

## socket()

- `int socket(int domain, int type, int protocol);`
    * `socket()` creates an endpoint for communication
    * On success, a file descriptor for the new socket is returned
    * On failure `-1` is returned and `errno` is set appropriately
    * First argument `domain` specifies a communication domain under which the communication between a pair of sockets will take place
        + communication may only take place between a pair of sockets of the same type
    * Familes definied in `/usr/include/x86../bits/socket.h`
        + `AF_UNIX`: within kernel on the same host using pathname addressing
        + `AD_INET`: via IPv4 on hosts connected via IPv4 network using 32-bit IPv4 address with 16 bit port number
    * Second argument `type` specifies the communication semantics
        + Types defined in `/usr/include/x86.../bits/socket_type.h`
        + Most common types are `SOCK_STREAM` and `SOCK_DGRAM`
    * Third argument specifies the protocol to be used within the network code inside the kernel, not the protocol between the client and server
        + Just set this to `0` to have `socket()` choose the correct protocol based on the `type`
        + May use constants e.g., `IPROTO_TCP` or `IPROTO_UDP`
        + May use `getprotobyname()` to get the official protocol name
        + Look at `/etc/protocols` for details
- Once `socket()` is successful you get a file descriptor
    * `int sockfd = socket(AF_INET, SOCK_STREAM, 0);`
    * Socket data structure contains several pieces of info for the expected style of IPC including:
        1. Family/domain: `AF_INET`
        2. Service: `TCP`
        3. Local IP
        4. Local port
        5. Remote IP
        6. Remote port
    * UNIX kernel initializes the first two fields when a socket is created
    * When the local address is stored in socket data structure we say that the socket is half associated
    * When both local and remote addresses are stored in socket data structure, we say that socket is fully associated
- How addresses in socket data structure are populated
    * For client:
        + Remote end point address is populated by `connect()`
        + Local end point address is automatically populated by TCP/IP software when client calls `connect()`
    * For server:
        + Local end point addresses are populated by `bind()`
        + Remote end point addresses are populated by `accept()`

## connect

- `int connect(int sockfd, const struct sockaddr *svr_addr, int addrlen);`
- `connect()` system call connects the socket referred to by descriptor `sockfd` to the remote server (specified by `svr_addr`)
- If we haven't called `bind()` (which we normally don't in client), it automatically chooses a local end point address for you
- On success, zero is returned and the `sockfd` is now a valid file descriptor open for reading and writing
- Data written into this file descriptor is sent to the socket at the other end of the connection and data written into the other end may be read from this file descriptor
- TCP sockets may successfully connect only once
- UDP sockets normally do not use `connect()` however connected UDP sockets may use `connect()` multiple times to change their asociateion
- When used with `SOCK_DGRAM` type of socket, `connect()` call simply stores the address of the remote socket in the local socket's data structure and it may communicate with the other side using `read()` and `write()` instead of `recvfrom()` and `sendto()` calls
- `connect()` performs four tasks:
    1. ensures specified `sockfd` is valid and that it has not already been connected
    2. fills in the remote end point address in the client socket from the second argument
    3. automatically chooses a local end point address by calling TCP/IP software
    4. Initializes a TCP connection (3 way handshake) and returns a value to tell the caller whether the connection succeeded

## read() and write()

- `read()` and `write()` system calls can be used to read/write from files, devices, sockets, etc (with any type of sockets stream or datagram)
- `read()` attempts to read up to `count` bytes from file descriptior `fd` into the buffer starting at `buf`
    * If no data is available the read call blocks
    * on success returns the number of bytes read and on error returns `-1` with `errno` set appropriately
- `write()` call writes `count` number of bytes starting from memory location pointed to by `buf` to file descriptor `fd`
    * On success, returns the number of bytes actually wrtitten and on error returns `-1` with errno set appropriately
- `send()` and `recv()` calls can be used for communicating over stream sockets or connected datagram sockets
    * If you want to use regular unconnected datagram sockets (UDP), you need to use the `sendto()` and `recvfrom()`

## send()

- `send()` call writes the `count` number of bytes starting from memory location pointed to by `buf` to filed descriptior `sockfd`
- `flags` argument normally set to zero if you want it to be normal data
    * Set flag as `MSG_OOB` to send data as out of band
        + Way to tell receiving system that this data has a higher priority than normal data
        + Receiver will receive signal `SIGURG` and in the handler it can then receive this data without receiving all the rest of the normal data in the queue
- `send()` call returns the number of bytes actually sent out and this might be less than the number you told it to send
    * If value returned by `send()` does not match the value in `count` then its up to you to send the rest of the string
- if socket has been closed by any side, process calling `send()` will get a `SIGPIPE` signal

## recv()

- `recv()` call attempts to read up to `count` bytes from file descriptor `sockfd` into buffer at `buf` If no data is available the call blocks
- `flag` normally set to zero if you want it to be normal `recv()`; otherwise can set to `MSG_OOB` to receive out of band data
- Call returns number of bytes read into the buffer or `-1` on error
- If `recv()` returns 0 then this means the remote side has closed the connection on you

## Reading in a Loop

- Data from a TCP socket should always be read in a loop until desired amount of data has been received
- Sample code:
```
char msg[128];
int n, nread, nremaining;
for(n=0, nread=0; nread < 128; nread += n){
    nremaining = 128 - nread;
    n = read(sockfd, &msg[nread], nremaining);
    if (n == -1) {perror("Read failed"); exit(1);}
}
printf("%s\n", msg);
```

## close()

- After a process is done using the socket, it calls `close()` to close it and it will be freed up never to be used again by that process
- On success returns zero or `-1` on error and `errno` will be set accordingly
- Remote side can tell iff this happens in one of two ways:
    1. Remote side calls `read()` and it returns 0
    2. Remote side calls `write()` and it receives a signal `SIGPIPE` and `write()` will return `-1` and `errno` is set to `EPIPE`
- In practice, Linux implements a reference count mechanism to allow multiple processes to share a socket
    * If `n` processes share a socket, the reference count will be `n`
    * `close()` decrements the reference count each time a process calls it
    * Once the rerference count reaches zero (i.e., all processes have called `close()`) then the socket will be deallocated

## shutdown()

- `int shutdown(int fd, int how);`
- When you close a socket descriptor it closes both sides of the socket for reading and writing and frees the socket fescriptor
- If you just want ot close one side you can use `shutdown()`
- Argument `fd` is descriptor of the socket you want to perform this action on and the action can be specified with `how`
    * `SHUT-RD(0)`: further receives are disallowed
    * `SHUT-WR(1)`: further writes are disallowed
    * `SHUT-RDWR(2)`: further sends and receives are disallowed
- Note: `close()` closes the socket ID and frees the descriptor for the calling process only, the connection is still opened if another process shares this socket ID
    * Connection stays open for both read and write
- Note: `shutdown()` breaks the connection for all processes sharing the socket ID
    * It doesn't close th efile descriptor or free the socket data structuire, it just changes its usability
    * To free a scoket descriptor you still have to call `close()`

## Examples:

- Example of echo client:
```
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
int main(int argc, char** argv){
//*** STEP-I:  Create a socket
   int sockfd = socket(PF_INET, SOCK_STREAM, 0);
//*** STEP-II: Populate Socket's DS for remote IP and Port, and
//***          let the local IP and Port be selected by the OS itself
   struct sockaddr_in dest_addr;
   dest_addr.sin_family = AF_INET;
   dest_addr.sin_port = htons(54154);
   inet_aton("192.168.100.20", &dest_addr.sin_addr);
   memset(&(dest_addr.sin_zero), '\0', sizeof dest_addr.sin_zero);
//*** STEP-III: Connect this socket to the server's socket
   connect(sockfd, (struct sockaddr*)& dest_addr, sizeof dest_addr);
//*** STEP-IV:  Client reads string from stdin and send it to server
//***           then read string returned by server and display on stdout
   char buff1[128],buff2[128] ;
   while(1){
      int n = read(0, buff1, sizeof buff1);
      buff1[n] = '\0';
      write(sockfd, buff1, strlen(buff1));
      n = read(sockfd, buff2, strlen(buff1));
      buff2[n] = '\0';
      write(1, buff2, n);
   }
//*** STEP-V:  Close socket
   close(sockfd);
   exit(0);
}
```
- Example of datetime client:
```
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
int main(){
//*** STEP-I:  Create a socket
   int sockfd = socket (PF_INET, SOCK_STREAM, 0);
//*** STEP-II: Populate Socket's DS for remote IP and Port, and
//***          let the local IP and Port be selected by the OS itself
   struct sockaddr_in dest_addr;
   dest_addr.sin_family = AF_INET;
   dest_addr.sin_port = htons(13);
   inet_aton("192.168.100.20", &dest_addr.sin_addr);
   memset(&(dest_addr.sin_zero), '\0', sizeof dest_addr.sin_zero);
//*** STEP-III: Connect this socket to the server's socket
   connect(sockfd, (struct sockaddr*)& dest_addr, sizeof dest_addr);
//*** STEP-IV:  Client sends no data to server rather the daytime
//***           server simply sends the date on connection establishment
   char buff[50];
   int rv = read(sockfd, buff, sizeof buff);
   buff[rv] = '\0';
   printf("Time Received from Server is: %s", buff);
//*** STEP-V:  Close socket
   close(sockfd);
   exit(0);
}
```

## bind()

- `int bind(int sockfd, struct sockaddr* myaddr, int addrlen);`
- socket created bvy a server process must be bound to an address and it must be advertised
    * any client process can later contact the server using this address
- `bind()` call assigns the address in 2nd argument `myaddr` to the socket referred to by `sockfd` (obtained from a previous `socket()` system call)
- `myaddr` is a pointer to a structure specifying the address to which this socket is to be bound
    * There are different address families each having own format
    * Type of structure passed in this argument depends on the socket domain
- `addrlen` argument specifies the size in bytes of the address structure pointed to by `myaddr`
- On sucecss, call returns 0
- On failure `-1` is returned and `errno` set appropriately

## listen()

- `int listen(int sockfd, int backlog);`
- `listen()` system call requests the kernel to allow specified socket mentioned in 1st argument to receive incoming calls
    * Not all types of sockets can receive incoming calls (`SOCK_STREAM` can)
- This call put a socket in passive mode and associate a queue where incoming connection requests may be placed iff the server is busy accomodating a previous request
- `backlog` arumgnet is the number of connections allowed on the incoming queue
    * Max queue size depends on the socket implementation
- on success it returns 0 and on failure `-1` is returned and `errno` is set approtiately
- Need to call `bind()` before `listen()` otherwise the kernel will have us listening on a random port

## accept()

- `int accept(int sockfd, struct sockaddr* callerid, socklen_t *addrlen);`
- `accept()` system call used by server process and returns a new socket descriptor to use for a new client
    * After this the server process has two socket descriptors:
        1. the original one (master socket) is still listening on the port
        2. new one (slave socket) is ready to be read and written
- It is used with connection based socket types(`SOCK_STREAM`)
- `sockfd` is a socket that has been created with `socket()` bound to a local address with `bind()` and is listening for connections
- On success, the kernel puts the address of the client into the second argument pointed to by `callerid` and puts the length of that address structure into `addrlen`
- on success return a non-negative integer that is a descriptor for the accepted socket
- on failure `-1` is returned and `errno` set appropriately

## Example

- Example of a TCP echo server:
```
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#define BACKLOG 10  //how many pending connections queue  will hold

int main(){
   int server_sockfd;//socket on which server process will listen for incoming con
   int client_sockfd; //socket on which the server will be comm with the client
   struct sockaddr_in server_addr;
   struct sockaddr_in client_addr;

//*** STEP-I:  Create passive socket for the server
   server_sockfd = socket (AF_INET, SOCK_STREAM, 0);

//*** STEP-II: Create a address structure containing server IP addr
//***          and port, then bind the server_sockfd with this address
   server_addr.sin_family = AF_INET;
   server_addr.sin_port = htons(54154);
   inet_aton("192.168.100.20", &server_addr.sin_addr);
   memset(&(server_addr.sin_zero), '\0', sizeof server_addr.sin_zero);
   bind(server_sockfd, (struct sockaddr*)&server_addr, sizeof server_addr);

//*** STEP-III: Create a connection queue and wait for clients
   listen(server_sockfd, BACKLOG);
   while(1){
      fprintf(stderr,"\nServer waiting for client connection...");

//*** STEP-IV: Accept a connection, blocks until connection from client is established
//****         will return a brand new descriptor for comm with this single connection
      int client_len = sizeof client_addr;
      client_sockfd=accept(server_sockfd,(struct sockaddr*)&client_addr,&(client_len));
      fprintf(stderr, "\n********* CLIENT CONNECTION ESTABLISHED ********");

//STEP-V ***** Read from sockfd and write back
      char buf[100];
      int rv;
      while (rv = read(client_sockfd, buf, sizeof buf))
        write(client_sockfd, buf, rv);
      close(client_sockfd);
      fprintf(stderr, "\n********* CLIENT CONNECTION TERMINATED ********");
      }
   return 0;
 }
```
- Example of `gethostbyname`:
```
#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
int main (int argc, char **argv){
    if (argc != 2){
        printf("You must enter the name of host whose IP U wanna find\n");
        exit (1);
    }
    struct hostent *phe; //pointer to host information entry
    phe=gethostbyname(argv[1]);
    printf("Host Name: %s\n", phe->h_name);
    printf("IP Address: %s\n", inet_ntoa(*((struct in_addr *)phe->h_addr)));
    return 0;
}
```
- Example of `getservbyname` to get port a server is using
```
#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
int main (int argc, char **argv){
   if (argc != 2){
      printf("Must enter a service name (e.g, echo, ftp)...\n");
        exit (1);
    }
    struct servent *pse; //pointer to service information entry
    pse = getservbyname(argv[1], '\0');
    printf("Service Name: %s\n", pse->s_name);
    printf("Port number: %d\n", ntohs(pse->s_port));
    return 0;
}
```

## Architecture of web app

- Client machine
    * Runs a web browser
    * Address: `protocol://hostname[:port]/pathtoresource`
- Web server
    * Receives HTTP request, sends back HTTP response
    * Web server sends static data request to storage for static web pages (e.g., html, xml, css, json, etc)
    * Web server can also send dynamic data request to app servers (e.g., PHP, Python, Ruby, etc)
        + Those may need to access databases e.g., MySQL, MariaDB, etc

## HTTP Request / Response Message

- HTTP request message consists of:
```
<method> <url> <version>
<header name> <value>
...
<header name> <value>
<optional body>
```
- Example:
```
GET / HTTP/1.1
Host: www.arifbutt.me
User-Agent: curl/7.56.1
```
- Methods: GET, HEAD, PUT, POST, TRACE, DELETE, OPTIONS
- HTTP response message consists of:
```
<version> <status code> <description>
<header name> <value>
...
<header name> <value>
<optional body>
```
- Example:
```
HTTP/1.1 200 OK
Date: Sun, 20 May 2018 18:18:23 GMT
Server: Apache
Content-Type: text/html; charset=UTF-8
Body
```
- Status codes: 1xx, 2xx, 3xx, 4xx, 5xx

## Example

- `curl http://arifbutt.me` to see request and response