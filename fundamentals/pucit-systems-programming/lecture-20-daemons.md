# Lecture 20

## Overview of Daemons

- Daemon is a system process that provides services to system admins without human interviention e.g., `cron`
- Provides services to OS kernel e.g., `paged`
- Communicate with other processes e.g., `httpd`
- Has following characteristics
    * Daemon is long-lived often created at system startup and runs until the system is shutdown
    * Runs in the background and has no controlling terminal
        + Lack of a controlling terminal ensures that kernel never automatically generates any terminal related signals (e.g., `SIGINT`, `SIGQUIT`, `SIFTSTP` and `SIGHUP`) for a daemon
- Daemons are written to carry out specific tasks e.g.,
    * `crond`: daemon that executes at a scheduled time
    * `sshd`: secure shell daemon
    * `httpd`: HTTP server daemon e.g., apache that serves web pages
    * `xinetd`: internet super server daemon which listens for incooming network connections on specified TCP/IP ports and launches appropriate server programs to handle these connections

## Writing a Daemon Process

- `ps -ajx` to show processes that do not have a controlling terminal (`x`)
- Process:
    1. Perform a `fork()`
        * After which parent exits and child continues
        * Child process inherits PGID of parent ensuring child is not a process group leader
        * Daemon process becomes the child of `/lib/systemd/systemd` process having PID of 992 which is the child of `/sbin/init` having PID of 1
        * Code:
        ```
        pid_t cpid = fork();
        if (cpid > 0)
            exit(0);
        while(1);
        ```
    2. Close all open file descriptors daemon inherited from parent
        * Code:
        ```
        struct rlimit r;
        getrlimit(RLIMIT_NOFILE, &r);
        for(i=3; i<r.rlim_max; i++)
            close(i);
        while(1);
        ```
    3. Only a single instance of a daemon process should run
        * For example, if multiple instances of `cron` start running, each would start running a scheduled operation
        * We can use logic to ensure that if one instance of a prpgram is running, no user should be able to run another instance
        * `int rv = fcntl(fd, F_SET_LCK, &lock);`
    4. Make file descriptors 0, 1, and 2 of PPFDT point to the file `/dev/null`
        * Ensures that if daemoon calls library functions that perform I/O on these descriptors, those functioons won't unexpectedly fail
        * Code
        ```
        int fd = open("/dev/null", O_RDWR);
        dup2(fd, 1);
        dup2(fd, 2);
        while(1);
        ```
    5. Since daemons run in the background, there is no need to have any terminal attached to them
        * To detach terminal from a daemon we use `setsid()` system call which makes daemon process process group leader and session leader
        ```
        setsid();
        while(1);
        ```
    6. Set file mode creation mask to 0 by calling `umask(0)` to ensure that when daemoon creates files and directories they have same access privileges as mentiooned in the mode specified in `open()` or `create()` system call
        * Change proocess's CWD typically to the root directory.
        * Necessary because a daemon usually runs until system shutdown
        * If daemon's current working directory is on a file system other than the one containing `/`, then that file system cant be mounted
        ```
        setsid();
        umask(0);
        chdir("/");
        while(1);
        ```
    7. Handle `SIGHUP` singal so that when it arrives, the daemon should ignore it
    ```
    signal(SIGHUP,SIG_IGN);
    while(1);
    ```

## Writing a Daemon Process

- Code:
```
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/resource.h>
#include <sys/fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

void create_daemon();
int main(){
   create_daemon();
   while(1){}
}
void create_daemon(){
//STEP-I: Make the process child of systemd
   pid_t cpid = fork();
   if(cpid > 0)
      exit(0);
//STEP-II: Close all files descriptors less 0,1,2
   struct rlimit r;
   getrlimit(RLIMIT_NOFILE, &r);
   for(int i=3; i<r.rlim_max; i++)
      close(i);
//STEP-III: Only a single instance of a daemon process should run
   int fd = open("f1.txt", O_CREAT | O_TRUNC | O_RDWR, 0666);
   if(fd == -1){perror("open");}
   struct flock lock;
	lock.l_start = 0;
	lock.l_len = 0;
	lock.l_type = F_WRLCK;
	lock.l_whence = SEEK_SET;
	int rv = fcntl(fd, F_SETLK, &lock);
   if(rv == -1){
      printf("This process is already running\n");
      close(fd);
      exit(1);
	}
	fprintf(stderr,"Daemon has started running with PID: %d\n", getpid());

//STEP-IV: Make std descriptors point to /dev/null
   int fd0 = open("/dev/null", O_RDWR);
   dup2(fd0, 0);
   dup2(fd0, 1);
   dup2(fd0, 2);
   close(fd0);
//STEP-V: Make the daemon session leader
    setsid();
//STEP-VI: Set umask to 0 and its pwd to /
    umask(0);
	chdir("/");
//STEP-VII: Ignore the SIGHUP signal
signal(SIGHUP,SIG_IGN);
}
```
- Running the above:
    * `ps -ajx -q <pid>`
        + See that `TTY ?` since no controlling terminal
        + `STAT Rs` for running, session leader
    * `kill <pid>` kills the daemon

## Managing Services using systemd

- `systemd` is a system and service manager for Linux OS
    * Runs as first process on boot (PID 1)
    * Acts as `init` system that brings up and maintains user space services
- `/sbin/init` and `/bin/systemd` are booth soft link to `/lib/systemd/systemd`!
- System daemoon has replacedw the traditional SYSV `init` daemon as well as the short livced `upstart` daemoon
- Two advantages of `systemd` over `init`
    * Event driven: stuff is started at the moment they are needed
    * Fast booting: `systemd` displays login prompt within a few seconds, no matter if a service on a remote socket is not available
- `systemctl()` is a program that is used to introspect and control the state of `systemd` system and service manager
    * It uses unit files to describe services that should run along with other elements of the system configuration
    * `systemd` unit file is basically a config file that describes how to manage a specific resource which can be a:
        1. `Service` units are daemons that can be started, stopped, restarted, reloaded, enabled and disabled
        2. `Target` unit group units together and represent state of the system at any one time
        3. `Socket` units describes a network, IPC socket, or FIFO buffer
        4. `Moount` unit defines a mount point on the system
        5. `Automount` units configure a mountpoint that will be automatically mounted
        6. `Timer` defines timer managed by systemd like cronjob
- `systemctl status ssh`
    * Active, running, PID, path
- `systemctl stop ssh`
- `systemctl start ssh`
- `systemctl enable ssh`
    * Enabling a service will make it be started automatically on boot

## Managing a service using systemd

1. Write a long running program in any language that you want `systemd` to manage
2. Write a service unit file to manage above executable
3. Copy executable in `/usr/local/bin` and service unit file in `/etc/systemd/system/`
4. Start/stop service using `systemctl`

## Example

- Basic echo server in Python:
```
import socket
sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockfd.bind(('0.0.0.0', 54154))
print("My echo server is listening on port: 54154")
while True:
	payload, client_addr = sockfd.recvfrom(1024)
	sockfd.sendto(payload, client_addr)
```
- `nc -u 127.0.0.1 54154`
    * Connect to local server at socket port, type and have it echo back
- All unit files are organized with sections, and a section is denoted by a pair of square brackets with section name enclosed:
    1. `[Unit]`: defines metadata of unit file; relationship with other units
    2. `[Service]`: applicable to service unit files
    3. `[Install]`: often last optioonal section and is used to define if this unit is enabled or disabled
- Example:
```
[Unit]
Description=myecho service by Arif Butt
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
ExecStart=/usr/bin/python /usr/local/bin/myechoserver.py

[Install]
WantedBy=multi-user.target
Alias=myecho.service
```
