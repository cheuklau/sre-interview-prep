# Lecture 36

## Unix Domain Socket

- Previously talked about internet domain sockets (streams i.e., TCP and datagram i.e., UDP)
- Unix domain socket is IPC mechanism using which two or more related or unrelated processes executing on same machine can communicate with each other
- Unix domain sockets are twice as fast as TCP so theyare used in communication between a client and server when both are on the sam ehost
- Unix domain socket support both TCP and UDP sockets
    * Communication is bidrectional with stream sockets
    * Unidirectional with datagram sockets
    * Unix domain datagram sockets are always reliable and don't reorder datagrams
- Instea dof identifyinng server by IP address and port, unix domain socket known by a pathname
    * Obviously client and server have to agree on pathname to find each other
- For unix domain sockets, file and directory permissions restrict which processes on the host can open the socket thus commucate with the server
    * Therefore, Unix domain sockets provide an advantage over internet sockets to which anyone can connect unless extra authentication logic is implemented

## Unix Domain Sockets setup

- `sockfd = socket(AF_UNIX, SOCK_STREAM, 0);`
- `struct sockaddr_un addr;`
- `addr.sun_family = AF_UNIX;`
- `strncpy(addr.sun_path, "socket", sizeof(addr.sun_path)-1);`
- `bind(sockfd, (struct sockaddr*)&addr, sizeof(addr));`
- Note: Unix Domain datagram socket is unidirectional
- Note: Unix domain sream socket are bidirectional

## Domain sockets vs named pipes

- Unix domain sockets can be created as stream sockets for bidrectional communciation as well as datagram sockets for uni-diectionarl
    * Named pipes are uni-directional only
- Unix domain sockets, each client has an independent connection to the server as server has a seprate descriptor for each clinet
    * In case of named pipes, many clients may write to the pipe but the server cannot distinhuiish the clients from each other because server only has one descriptor to read from trhe named pipe
    * Therefore, unix domain sockets should be used if there are multiple clients that need to be distinguishable
- Sockets are created usign `socket()` and assigned identity via `bind()` on server side
    * Named pipes created using `mkfifo()`
    * To connect to a unix domain socket, we use `socket()` and `connect()` calls
    * Process uses `open()` to create a named pipe anf then can eithe rread or write to it

## Example

- Lab setup the same as before, but since we are using unix domain sockets, we will just work on kali machine
- Example TCP echo server over unix domain socket:
```
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main(){
   int server_sockfd;
   int client_sockfd;
   struct sockaddr_un server_addr;
   struct sockaddr_un client_addr;
//STEP-I *****Remove any old sockets and create an unnamed socket for the server
   unlink("./socketfile");
   server_sockfd = socket (AF_UNIX, SOCK_STREAM, 0);
//STEP-II ****Populate socket's DS for the sockaddr_un type by giving the filename and then bind server_sockfd with this file
   server_addr.sun_family = AF_UNIX;
   strncpy(server_addr.sun_path, "./socketfile", sizeof(server_addr.sun_path)-1);
   bind(server_sockfd, (struct sockaddr*)&server_addr, sizeof server_addr);
//STEP-III ***Create a connection queue and wait for clients
   listen(server_sockfd, 5);
   while(1){
      fprintf(stderr,"\nServer waiting for client connection...");
//STEP-IV **** Accept a connection, blocks until connection from client is established
//        **** will return a brand new descriptor to use for this single connection
      int client_len = sizeof client_addr;
      client_sockfd = accept(server_sockfd,(struct sockaddr*)&client_addr, &(client_len));
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
- Example client:
```
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
int main(int argc, char* argv[]){
//STEP-I **** Create a socket for the client
   int sockfd;
   sockfd = socket (AF_UNIX, SOCK_STREAM, 0);
//STEP-II *** Populate socket's DS for sockaddr_un type by giving the file name as agreed with the server
   struct sockaddr_un address;
   address.sun_family = AF_UNIX;
   strncpy(address.sun_path, "./socketfile", sizeof(address.sun_path)-1);
//STEP-III **** Connect this socket to the server's socket
   int rv = connect(sockfd, (struct sockaddr*)& address, sizeof address);
   if(rv == -1){ fprintf(stderr, "Error in connection."); exit(1);}
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
- Example UDP sender:
```
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
int main(int argc, char* argv[]){
//STEP-I **** Create a socket for the client
   int sockfd = socket (AF_UNIX, SOCK_DGRAM, 0);
//STEP-II *** Populate socket's DS for sockaddr_un type by giving the socket file name
   struct sockaddr_un dest_addr;
   dest_addr.sun_family = AF_UNIX;
   strcpy(dest_addr.sun_path, "./socketfile");
//*** STEP-III: Get a string from user and use sendto() to send that string
//***           to the receiver process
   char buff[128];
   fprintf(stderr, "Enter your name to be sent:");
   int n = read(0, buff, sizeof buff);
   buff[n] = '\0';
   sendto(sockfd,buff, sizeof buff, 0, (struct sockaddr*) &dest_addr, sizeof dest_addr);
//*** STEP-IV:  Close socket
   close(sockfd);
   exit(0);
}
```
- Example UDP receiver:
```
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main(){
   int sockfd;
   struct sockaddr_un server_addr;
//STEP-I *****Remove any old sockets and create  socket
   unlink("./socketfile");
   sockfd = socket (AF_UNIX, SOCK_DGRAM, 0);
//STEP-II ****Populate socket's DS for the sockaddr_un type by giving the filename and then bind server_sockfd with this file
   server_addr.sun_family = AF_UNIX;
   strcpy(server_addr.sun_path, "./socketfile");
   bind(sockfd, (struct sockaddr*)&server_addr, sizeof server_addr);
//*** STEP-III: Use recvfrom to receive msg from client
   char buff[100];
   int addr_len = sizeof server_addr;
   recvfrom(sockfd,buff,sizeof buff,0,(struct sockaddr*)&server_addr, &addr_len);
   printf("Welcome Mr. %s \n", buff);
//*** STEP-IV
      close(sockfd);
   return 0;
 }
```