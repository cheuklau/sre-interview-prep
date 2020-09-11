# Lecture 37

## System call graph: tcp sockets

- We have seen this already which illustrates an iterative server
- When client is transferring data with server, server has `listen()` call running which stores subsequent connections into a queue
- Example of iterative server (seen already):
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
   listen(server_sockfd, 10);
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
- Client:
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
   if(argc!=3){printf("Must enter IP and port\n"); exit(1);}
//*** STEP-I:  Create a socket
   int sockfd = socket(PF_INET, SOCK_STREAM, 0);
//*** STEP-II: Populate Socket's DS for remote IP and Port, and
//***          let the local IP and Port be selected by the OS itself
   struct sockaddr_in dest_addr;
   dest_addr.sin_family = AF_INET;
   dest_addr.sin_port = htons(atoi(argv[2]));
   inet_aton(argv[1], &dest_addr.sin_addr);
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
- If we run client on kali and server on ubuntu and start multiple terminals on kali to make mutliple connections we see:
    * Only the first process is served
    * After we close the first process, second process is served and so on
    * Therefore we see that for iterative server, only 1 client is served at a time while remaining clients are kept in a queue
- On the contrary, if we start multiple processes contacting ubuntu server's `xinetd` echo service (concurrent server) on port 7, we see
    * Originally, ubuntu server has port 7 listening
    * After first process from kali is started, we have port 7 on ubuntu server in an `ESTABLISHED` state with the kali server at port 50620
    * After second process from kali is started, we have port 7 on ubuntu server in an `ESTABLISHED` state with the kali server at port 50621
    * and so on

## Concurrent Server

- Concurrent models mostly use Stream sockets and can be implemented using three techniques:
    1. Multi-process model
        * Multiple single-threaded process using `fork()` system call for every new client
        * Done if each slave can opearte in isolation to achieve maximal concurrency in case of multiprocessor
        * System call graph
            1. Master server performs `socket()`, `bind()`, listen()`
            2. Whenever a connection comes in the master server will run `accept()`, perform a three-way handshake and then call `fork()`
            3. Child process will then handle the `read()`, `write()` requests with the client before `close()`
    2. Multi-threaded model
        * Multiple threads within a single process
        * Use `pthread_create()` library call to cater for every new client
        * Done if each slave need to share data with the parent or with each other
    3. Non-blocking multi-plexed I/O
        * Single thread within a single proces using asynchronous I/O
        * Server create a non-blocking socket and use `select()` system call to cater for reading and writing on multiple clients using socket multiplexing

## Example

- Concurrent server using `fork()`:
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
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#define BACKLOG 10  //how many pending connections queue  will hold
void reaper(int sig){
   waitpid(-1, NULL, 0);
}
int main(){
   signal(SIGCHLD, reaper);
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
//*** STEP-IV: Accept a connection, blocks until connection from client is established
//****         will return a brand new descriptor for comm with this single connection
      int client_len = sizeof client_addr;
      client_sockfd=accept(server_sockfd,(struct sockaddr*)&client_addr,&(client_len));
      switch(fork()){
          case 0: //child
            fprintf(stderr, "\n********* CLIENT CONNECTION ESTABLISHED ********");
            close(server_sockfd); // child must close its own master descriptor
	         char buf[100];
            int rv;
            while (rv = read(client_sockfd, buf, sizeof buf))
               write(client_sockfd, buf, rv);
            close(client_sockfd);
            fprintf(stderr, "\n********* CLIENT CONNECTION TERMINATED ********");
            exit(0);
          default: //parent
            close(client_sockfd); // parent must close its slave descriptor
            break;
          case -1:
            fprintf(stderr,"Error in fork\n");
            exit(1);
      }
    }
   return 0;
 }
 ```

 ## Concurrent Connection Server using Multi-Thread

 - Example:
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
#include <pthread.h>
#define BACKLOG 10  //how many pending connections queue  will hold
void* tcpechod(void *fd);
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
//*** STEP-IV: Accept a connection, blocks until connection from client is established
//****         will return a brand new descriptor for comm with this single connection
      int client_len = sizeof client_addr;
      client_sockfd=accept(server_sockfd,(struct sockaddr*)&client_addr,&(client_len));
      pthread_t tid;
      pthread_attr_t ta;
      pthread_attr_init(&ta);
      pthread_attr_setdetachstate(&ta, PTHREAD_CREATE_DETACHED);
      pthread_create(&tid, &ta, &tcpechod, (void*)&client_sockfd);
    }
   return 0;
 }
void* tcpechod(void * fd){
   int client_sockfd = *((int*)fd);
   char buf[100];
   int rv;
   fprintf(stderr, "\n********* CLIENT CONNECTION ESTABLISHED ********");
   while (rv = read(client_sockfd, buf, sizeof buf))
      write(client_sockfd, buf, rv);
   close(client_sockfd);
   fprintf(stderr, "\n********* CLIENT CONNECTION TERMINATED ********");
   pthread_exit(NULL);
}
```
- Running above will show four established connections with `netstat` but only one process running with `ps`

## Introduction to select()

- Process sometimes expects input from two different sources but doesn't know which input will be available first
    * Example: consider process trying to read from source A but input is only available from Source B, and the process blocks
- One solution of monitoring multiple file descriptors is to use a separate process/thread for each descriptor
- The other method is perform I/O multiplexing which can be done using
    * `select()`
    * `poll()`
- Nowadays both are required by SUSv3
- `select()` allows a program to monitor multiple file descriptors until one or more of them become ready for some class of I/O operation
    * File descriptor is considered ready if it is possible to perform a corresponding I/O operation without blocking
- `select()` takes three descriptor sets of type `fd_set` as arguments
    1. `rfds` is set of file descriptors to be tested to see if input is possible
    2. `wfds` is set of file descriptors to be tested to see if ourput is possible
    3. `efds` set of file descriptors to be tested to see if exponential condition has occurred
- Last argument `timeout` is a value that forces `select()` to return after a certain time has elapsed even if no descriptors are ready