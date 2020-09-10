# Lecture 35

## Datagram Sockets

- Datagram sockets `SOCK_DGRAM` provide unreliable, full-duplex, packet-oriented communication channel
- Messages are transmitted and received in terms of datagrams which is a small, fixed-length packet
- Process either reads the entire message or in case of error does not read any data
- Unreliable means there is no sequence numbering so messages may arrive out of order, be duplicated or not arrive at all
- Datagram sockets can be connected as well as unconnected

## System call graph: UDP sockets

- Only one socket on which all data transfer occurs (only 1 on server)
- On server:
    * `socket()`
    * `bind()`
    * `recvfrom()`
- On client:
    * `socket()`
    * `sendto()` to send data to server (blocks until data is received)
- On server:
    * `recvfrom()` allows us to obtain address of the client
    * `sendto()` to send reply to client
- On client:
    * `recvfrom()`
    * `close()`
- No order guarantee

## Datagram Sockets

- Connectionless datagram sockets:
    * Mostly datagram sockets are connectionless i.e., client does not call `connect()` rather address every message using `sendto()` and `recvfrom()` calls
    * Possible for a process to call `sendto()` to different server processes
- Connection-oriented datagram sockets
    * If UDP client calls `connect()` and specifies the UDP server address, socket is said to be connected
    * FCrom that point onward client may only send to and receive from the address specified by connect
    * So you don't have to use `sendto()` and `recvfrom()`
    * You can simply use `send()` and `recv()` calls
    * Normally UDP sockets do not use connect howeveer UDP sockets may use `connect()` multiple times to change their association

## Stream vs Datagram sockets

- TCP stream sockets vs UDP Datagram sockets
    + Fragment/reassemble; No
    + Ordering; No
    + Reliable; May not arrive
    + Connected; Multiple senders
- Datagram sockets
    * Place less load on kernel network code and on network traffic
    * Datagrams may get lost in transit and they may arrive out of order
    * For these two reasons, datagram sockets are best suited to apps in which simplicity, efficiency and speed are more important than data integrity and consistency
    * They are a bad choice for web, file or email servers as they can be large documents
    * Good for streams of music and video where a missing note or frame may not even be noticed

## Example

- Same lab setup as before
- On ubuntu server:
    * `ifconfig` to verify IP of server
    * `systemctl status xinetd.service` to ensure `xinetd` is running
- On Kali:
    * Run this example of a connected UDP socket
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
    if(argc != 3){printf("Must enter IP and port of echo server\n"); exit(1);}

    //*** STEP-I:  Create a socket
    int sockfd = socket (PF_INET, SOCK_DGRAM, 0);

    //*** STEP-II: Populate Socket's DS for remote IP and Port, and
    //***          let the local IP and Port be selected by the OS itself
    struct sockaddr_in dest_addr;
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(atoi(argv[2]));
    inet_aton(argv[1], &dest_addr.sin_addr);
    memset(&(dest_addr.sin_zero), '\0', sizeof dest_addr.sin_zero);

    //*** STEP-III: Connected UDP Socket
    connect(sockfd, (struct sockaddr*)& dest_addr, sizeof dest_addr);

    //*** STEP-IV: Get a string from user and use write() to send that string
    //***           to echo server and then read a message from server and display on stdout
    char buff1[128],buff2[128] ;
    while(1){
        int n = read(0, buff1, sizeof buff1);
        buff1[n] = '\0';
        write(sockfd, buff1, strlen(buff1));
        n = read(sockfd, buff2, strlen(buff1));
        buff2[n] = '\0';
        write(1, buff2, n);
    }
    //*** STEP-IV:  Close socket
    close(sockfd);
    exit(0);
    }
    ```
- On ubuntu
    * When we try to run the above, the client was unable to connect. Why?
    * `netstat -anu | grep 7` shows that the `xinetd` service is running but is disabled for UDP
    * Go to config file and enable UDP
    * `systemctl restart xinetd.service`
    * `netstat -anu | grep 7` now shows that it is running on port 7
- On Kali:
    * Run next example of an unconnected UDP socket
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
    if(argc != 3){printf("Must enter IP and port of echo server\n"); exit(1);}

    //*** STEP-I:  Create a socket
    int sockfd = socket (PF_INET, SOCK_DGRAM, 0);

    //*** STEP-II: Populate Socket's DS for remote IP and Port, and
    //***          let the local IP and Port be selected by the OS itself
    struct sockaddr_in dest_addr;
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(atoi(argv[2]));
    inet_aton(argv[1], &dest_addr.sin_addr);
    memset(&(dest_addr.sin_zero), '\0', sizeof dest_addr.sin_zero);

    //*** STEP-III: Get a string from user and use sendto() to send that string
    //***           to echo server and then read a message from server and display on stdout
    char buff1[128],buff2[128] ;
    while(1){
        int n = read(0, buff1, sizeof buff1);
        buff1[n] = '\0';
        sendto(sockfd, buff1, sizeof buff1, 0, (struct sockaddr*) &dest_addr, sizeof dest_addr);
    int addr_len = sizeof dest_addr;
        recvfrom(sockfd, buff2, sizeof buff2, 0, (struct sockaddr*) &dest_addr, &addr_len);
        buff2[n] = '\0';
        write(1, buff2, n);
    }

    //*** STEP-IV:  Close socket
    close(sockfd);
    exit(0);
    }
    ```