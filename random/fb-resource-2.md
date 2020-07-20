# Source

This document covers the questions here:

https://github.com/chassing/linux-sysadmin-interview-questions#fun

# General

## What function does DNS play on a network?

- DNS is a distributed database of hostnames to IP addresses.
- Different sites and organization provide part of that database (e.g., Cloudflare).
- Nameserver
    * DNS set up via name servers which load DNS settings and configs.
    * If name server doesn't know answer to a DNS query, it redirects request to other name servers.
    * Name servers can be authoritative i.e., they hold actual DNS records you look for.
    * Name servers can also be recursive i.e., they ask other servers until they find an authoritative server containing the DNS records.
    * Recursive name servers can also have the DNS record cached.
- Zone file
    * Name servers coontain zone files.
    * Zone files dictate how name servers stoore information aboout the domain or how to get domain if it doesn't know.
- Resource records
    * Zone file made up of entries of resource records.
    * Each line is a record and contains info about hosts, name servers and other resuorces.
    * Fields:
        1. Record name
        2. TTL
        3. Class: namespace of record information, most commonly `IN` for internet
        4. Data: IP if `A` record or something else depending on record type
        5. Example: `mtg-post.com IN A 192.146.0.4`
- DNS process:
    * Host asks for IP for a domain name (`rupert.com`)
    * Local ISP DNS server asks Root Servers.
    * 13 Root Servers mirrored and distributed around the world to handle DNS requests.
    * Root Servers contain information about top-level domains e.g., `.org`, `.com`, `.net`, etc
    * Root Server returns IP of the `.com` top-level DNS server.
    * Host sends anotoher request to the `.com` top-level DNS (TLD) server.
    * TLD server doesn't have `rupert.com` in their zone files, but it sees a record for the nameserver for `rupert.com` so it returns that IP.
    * Host sends final request to the authoritative DNS server with the IP for `rupert.com`.
- Note: Before going to DNS, host looks at `/etc/hosts`.
- Note: Can use `/etc/resolv.conf` to specify name server IPs.
- `nslookup <domain-name` to get resource records.
- `dig <domain-name>` also returns information about DNS servers; great for troubleshooting DNS issues.

## What is HTTP?

- Hypertext transfer protocol (HTTP) is an application protocol for distributed, collaborative, hypermedia information systems.
- A request-response protocol in the client-server computing model.
- Client initiates a request by establishing a TCP connection to a particular port on a server (80).
- Upon receiving the request, server sends back a status e.g., `HTTP/1.1 200 OK` along with its own message (requested resource).
- HTTP is stateless protocol. However some web apps implement states using cookies.

## What is an HTTP proxy and how does it work?

- HTTP proxy operates between client and server.
- Client sends `GET http://SERVER/path HTTP/1.1` to the proxy.
- Proxy forward request to the `SERVER`.
- `SERVER` only sees the proxy as connection and answers to the prooxy.
- Proxy receives response and forwards it back to client.
- HTTP proxy can do path based routing, buffers responses so it is not send back to othe client until the whole response is received, etc.

## Describe briefly how HTTPS works.

- HTTPS uses TLS/SSL encryption over the HTTP protocol.
- Client and server establishes a symmetric encrypted connection through SSL/TLS handshake as follows:
    1. Client sends "hello" message to server. Message includes TLS version, cipher type and a string of random bytes.
    2. Server sends a message containing server's SSL certicate with public key, server's chosen cipher and server random bytes.
    3. Client verifies sercer's SSL cert with CA.
    4. Client sends another random byte (premaster secret) encrypted with the public key.
    5. Server decrypts premaster secret using its private key.
    6. Both client and server generate session keys from client random, server random and premaster secret.
    7. Client sends finished message encrypted with session key.
    8. Server sends finished message encrypted with session key.
    9. Secure symmetric encryption achieved. Communicatioon continues with session keys.

## What is SMTP? Give basic scenario of how mail message is delivered via SMTP.

- Email clients interact with simple mail transfer protocol (SMTP) server to handle the sending.
- SMTP server on host have conversatioons with other SMTP servers to deliver email.
- Example: send email from `howstuffworks.com` to `jsmith@mindspring.com`
    1. Client connects to SMTP server at `mail.howstuffworks.com` using port 25 (default).
    2. Client tells SMTP server address of sender and recipient and body of message.
    3. SMTP server parses out recipient name `jsmith` and domain `mindspring.com`.
    4. SMTP server talks with DNS to get IP address of SMTP server for `mindspring.com`. DNS replies with one or more IP addresses.
    5. SMTP server at `howstuffworks.com` connects with SMTP sercer at `mindspring.com` using port 25, and gives the message to mindspring server.
    6. Mindspring server recognizes domain name for `jsmith` is at `mindspring.com` s oit hads message to mindspring's post office protocol (POP3) server, which puts message in `jsmith` mailbox.

## What is RAID? What is RAID0, RAID1?

- Redundant Array of Independent Disks (RAID) is a data storage virtualization technology combining multiple physical disks into logical units for data redundancy, performance improvement or both.
- Data is distributed across the drives in one of several ways (referred to as RAID levels) depending on the required level of redundancy and performance.
- RAID0 (striping)
    * Data split into blocks written across all drives.
    * Superior I/O performance.
    * Not fault-tolerant i.e., if one drive fails, all data in the RAID0 array is lost.
- RAID1 (mirroring)
    * Data stored twice by writing to both the data and mirror drive.
    * If a drive fails, controller uses either data or mirror drive for data recovery and continues operation.
    * Excellent read speed.
    * Write speed comparable to single drive.
    * Half of the total drive capacity available for storage.
    * Ideal for mission-critical data.


## What is level 0 backup? What is an incremental backup?

- `dump` is a Linux tool for backing up file systems rather than individual files.
- Level 0 commands `dump` to perform a full backup of the entire file system.
- Levels 1 to 9 instruct `dump` to perform an incremental backup since the last backup at the same level.
- Incremental backups takes up less space but results in slower recovery time.

## Describe general file system hierarchy in Linux.

- Standard directories and contents:
    * `/bin` = core os commands
    * `/boot` = kernel and files to load the kernel
    * `/dev` = device entries
    * `/etc` = critical startup and config files
    * `/home` = default home directories for users
    * `/kernel` = kernel components
    * `/lib` = libraries, shared libraries
    * `/media` = mount points for filesystems of removable media
    * `/mnt` = temp mount points
    * `/opt` = optional software packages
    * `/proc` = running processes info
    * `/root` = home directory for super user
    * `/sbin` = commands for minimal system operability
    * `/tmp` = temp files
    * `/usr` = hierarchy of secondary files and commands
        + `/bin` = most commands and executables
        + `/include` = header files for compiling C programs
        + `/lib` = libraryies
        + `/local` = software you write or install
        + `/sbin` = less essential commands for admin and repair
        + `/share` = items common to multiple systems
        + `/src` = source code for nonlocal software
        + `/tmp` = more temp space
    * `/var` = system specific data and configs
        + `/adm` = setup records
        + `/log` = various system log files
        + `/spool` = spooling directories for printers, mail, etc
        + `/tmp` = more temp space

## Difference between public and private SSH keys.

- Use of public and private SSH keys is asymmetric encryption.
- User private key is on client machine.
- User public key is the counterpart to the private key.
- User public key must be registered on host server (`~/.ssh/authorized_keys`).
- Host private key is on host machine.
- Host public key is the counterpart to the private key.
- User should be provided with host public key before connecting.
- Client application prompts user with host public key on first connection to allow the user to verify and authorize the key.
- The host public key is then saved and verfied automatically on future connections.
- Client application warns the user if host key changes.
- Client encrypts using host public key, host decrypts using private key.
- Host encrypts using client public key, client decrypts using private key.

# Simple Linux Questions

## What is name and UID of admin user?

- `root` has UID of `0`

## How to list all files including hidden ones in a directory?

- `ls -al`
- Note: `a` flag specifically lists all files including hidden ones
- Note: `l` flag just shows more information

## What is Linux command to remove a directory and its contents?

- `rm -rf <directory name>`

## Which command to show free/used memory? Does free memory exist on Linux?

- `free -m`
- Note: output is in MB.
- Note: shows `total`, `used`, `free`, `buffers/cache`, `swap` and `available`.
- Note: To see how much ram apps can use without swapping look at `available` instead of `free` because `free` also deducts the memory used for `buffers/cache` as explained below.
- `cat /proc/meminfo`
- `vmstat -s`
- `top`
- `htop`
- Linux borrows memory for disk caching making free memory look lower than it actually is.
- If an application wants more memory, it just takes back memory borrowed for disk cache.

## How to search for string in files of a directory recursively?

- `grep -r <string> <directory>`

## How to connect to a remote server with SSH?

- `ssh <username>@<server>`

## How to get all env vars ad how can you use them?

- `printenv` to print all env vars.
- `$<ENV>` to use env vars in commands.

## Command not found when running `ifconfig -a`. What can be wrong?

- `ifconfig` binary not in `PATH`.
- `which ifconfig` to check if system recognizes `ifconfig` command.
- If not, `export PATH=$PATH:/path/to/ifconfig` to recognize `ifconfig` for this session.
- If you need `ifconfig` between sessions, add `export PATH=$PATH:/path/to/ifconfig` to bash profile (`~/.bash_profile`).

## What happens if I type `TAB-TAB`?

- Tab completion of a partial command.

## What command will show available disk space on Linux system?

- `df -h`
- Note: `h` flag just makes the output human readable.

## Which Linux commands will alter a files ownership, files permissions?

- `chown` to modify file ownership for user
    * `chown <username> <filename>`
- `chgrp` to modify file ownership for group
    * `chgrp <username> <filename>`
- `chmod` to modify file permissions
    * `chmod +x <filename>` to give execute permission
    * `chmod 777 <filename>` to give read, write, execute permission

## What does `chmod +x <filename>` do?

- Gives execute permission to file

## What does the permission 0750 on a file mean?

- Note: 1 = execute, 2 = write, 4 = read
- Note: first bit is the sticky bit, if it is set to 1 then only the owner can delete the file.
- Gives read, write, execute permission to owner.
- Gives execute and read permission to group.
- No permissions for others.

## What does the permission 0750 on a directory mean?

- Note: 1 = enter directory, 2 = write into directory, 4 = read contents of directory
- Note: first bit is the sticky bit, if it is set 1 then only the owner can delete the directory.
- Gives read, write and entrance permission to owner.
- Gives read and entrance permission to group.
- No permissions for others.

## How to add a new system user without login permissions?

- Users without login permissions are typically system users bound to a service and not actual users.
- `useradd -r <system username> -s /bin/false`
    * Note: `r` flag indicates to create a system account (no password and no home directory).
    * Note: `s` flag indicates we want to set the shell (in this case to none).

## How to add/remove a group from a user?

- `usermod -a -G <groupname> <username>` to add user to an existing group (as secondary group).
    * Note: `a` flag is for append so we don't overwrite existing groups the user is assigned to.
- `usermod -g <groupname> <username>` to change user's primary group.
- `useradd -G <groupname> <username>` to create a new user and assign it to existing group (as secondary group).
- `id -nG <username>` to view groups that user belongs to.
    * Note: `n` flag is used to print name of groups rather than IDs.
    * Note: `G` flag means to print all Group IDs.
- `usermod -G <list of groups to keep> <username>` to update the user's groups.

## What is a bash alias?

- Bash aliases are shortcuts to save you from having to remember long commands.
- `alias <alias name>=<command to run>`

## How do you set the mail address of the root/a user?

- Update `/etc/aliases`:
```
root: <new root email address>
<user>: <new user email address>
```

## What does CTRL-c do?

- CTRL-c sends the `SIGINT` signal (2) to a process, which will be intercepted.
- Usually process will clean up and exit.

## What does CTRL-d do?

- Sends EOF to the running process.
- Has no impact if the program isn't readiung from the terminal; otherwise signals end of input.

## What does CTRL-z do?

- CTRL-Z sends the `SIGSTOP` signal (19) to a process, which cannot be intercepted by the program.
- You can resume it in the foreground using `fg`.
- You can resume it in the background using `bg`.

## What is in `/etc/services`?

- Contains infromation about services that client applications might use on the computer.
- Contains service name, port number and protocol.
- Supports `getportbyname()` sockets call e.g., `getportbyname(POP3)` returns 110 port that POP3 runs on.

## How to redirect STDOUT and STDERR in bash?

- Note: 0 = stdin, 1 = stdout, 2 = stderr
- `some_command > stdout_file 2 > stderr_file` to redirect stdout and stderr to two separate files.
- `some_command > stdout_file 2>&1` to redirect stdout to a file and redirect stderr to stdout.
- `some_command &> both_file` to redirect both stdout and stderr to a file (not supported by `sh` or `ksh`).
- Note: Last two commands are functionally the same.

## What is the difference between UNIX and Linux.

- UNIX is a full-fledged paid OS whereas Linux is just a kernel of many free OS e.g., Fedora, Ubuntu, etc.

## What is the difference between Telnet and SSH?

- SSH is more secure, encrypting data whereas telnet sends data in plain text.
- SSH uses public key authentication wheres telnet does not authenticate.
- SSH has more overhead than telnet.
- Telnet has been all but replaced by SSH in almost all use cases.
- Telnet and SSH servers the same purpose.
- `telnet <server ip>` to connect (default port is 23 using TCP)

## Explain the three load averages and what do they indicate. What command can be used to view the load averages?

- Load averages are the three numbers shown with `uptime` and `top` e.g., `load average: 0.09, 0.05, 0.01`.
- The three numbers represent load averages over 1, 5 and 15 minute averages.
- Note: The 100% CPU utilization mark is 1.00 on a single core system, 2.00 on a dual-core, etc.
- For the purposes of sizing CPU load, the total number of cores is what matters regardless of how many physical processors those cores are spread across.
- `cat /proc/cpuinfo` to see how many cores system has.

## Can you name a lower-case letter that is not a valid option for GNU `ls`?

- e, j, y (obtained by looking at `man ls`).

## What is a Linux kernel module?

- Linux kernel module are pieces of code that can be loaded and unloaded into the kernel on demand.
- Code extends functionality of the kernel without needing to reboot the system.
- Module can be configured as built-in or loadable.
- `lsmod` to show what kernel modules are loaded.
- `modinfo <module name>` to show more information about a module.
- `/etc/modules-load.d/<program name>.conf` list kernels to load during boot.
- `modprobe <module name>` to load a module.
- `modprobe -r <module name>` to unload a module.
- Stored in `/lib/modules` and have extension `.ko`.
- Common uses of kernel modules:
    * Device drivers for specific pieces of hardware.
    * Filesystem drivers that interpret contents of a filesystem e.g., files and directories.
    * Invent your own system call or override an existing system call with a Linux kernel module of your own.
        + Note: System calls are always built into the base kernel (no kernel module option).

## Walk me through the steps in booting into single user mode to troubleshoot a problem.

- You can change to single user mode dynamically by `telinit 1`.
- For a system using Grand Unified Boot Loader (GRUB), you can reboot with `shutdown -r` then select the run level via the GRUB menu.
- Single user mode is useful when you need to recover a filesystem or database, or to install and test some new hardware.
- In these cases, we do not want other users on the system interfering.
- Note:
    * `shutdown` (unlike `telinit`) will send a message to all logged-in user and block any futher logins.
    * It then tells `init` to switch runlevel.
    * The `init` process sends all running processes a `SIGTERM` signal giving them a chance to save data.
    * After 5 seconds a `SIGKILL` signal is sent to foricbly end processes.

## Walk me through the steps you'd take to troubleshoot a 404 error on a web application you administer.

- The HTTP 404 response indicates that the browser was able to communicate with a given server but the server could not find what was requested.
- Debugging procedure:
    1. Verify the issue. If server is running Nginx, look at `/var/log/nginx/access.log` and find the requested URI with the 404 return code.
    2. Verify the URI is valid. If server is running Nginx, look at `/etc/nginx/nginx.conf` and see how the requested URI is being handled.
    3. Verify that the requested resource is available. For example, if the URI is for a static file on the local server, verify it exists.
    4. For more complex resource requests, increase log level from `warn` (default) to `info`.
        * This allows missing resources causing 404 return codes to be in `/var/log/nginx/error.log`.

## What is ICMP protocol? Why do you need to use?

- Internet control message protocol (ICMP) is an internet layer protocol that network devices use to diagnose network communication issues.
- Any IP network device has the capability to send, receive and process ICMP messages.
- Primary use is for error reporting i.e., ICMP generates errors to share with sending device is any of its data did not get to the destination.
- Second use is network diagnostics e.g., `traceroute` to find hops (and time between hops) to destination.
- Note: `ping` is simplified `traceroute` to test speed of connection between two devices (useful for calculating latency).
- Note: ICMP is not a transport protocol that sends data between systems (not TCP or UDP).