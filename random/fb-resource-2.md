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

# Medium Linux Questions

## What do the following commands do and how would you use them?
1. `tee` - reads stdin and writes it to both stdout and one or more files
    * `wc -l file1.txt | tee -a file2.txt` prints the output of `wc` to stdout and appends to `file2.txt`.
2. `awk` - scripting language used for manipulating data and generating reports.
    * `awk '{print}' file.txt` prints each line of `file.txt`.
    * `awk '/manager/ {print}' file.txt` prints each line with `manager` in `file.txt`.
    * `awk '{print $1,$4}' file.txt` prints column 1 and 4 of each line in `file.txt`.
3. `tr` - translates or deletes characters
    * `cat file.txt | tr "[a-z]" "[A-Z]"` converts all lowercase letters in `file.txt` to uppercase.
    * `echo "foobar" | tr -d "o"` deletes all `o` in `foobar`.
4. `cut` - cut out sections from each line and writing result to stdout
    * `cut -c 1-3 file.txt` prints first 3 characters of each row in `file.txt`.
    * `cut -d " " -f 1 file.txt` prints the first field separated by `" "` delimiter.
5. `tac` - concatenate and print files in reverse
    * `tac file.txt` prints `file.txt` in reverse.
6. `curl` - transfer data to or from a server using HTTP, FTP, IMAP, POP3, SCP, SFTP, SMTP, TFTP, TELNAT, LDAP or FILE
    * `curl https://www.google.com` to curl Google front page.
    * `curl -o hello.zip ftp://some.website/file.zip` to curl zip file into `hello.zip` location.
7. `wget` - non-interactive (can run in the background) network downloader supporting HTTP, HTTPS, FTP.
    * `wget https://www.google.com`
    * `wget -c https://some-website.com/large-file.zip` to resume downloading a large file.
8. `watch` - executes a program periodically (default is 2 seconds) showing output in fullscreen.
    * `watch -d free -m` to highlight differnce between successive updates of `free -m` command.
9. `head` - prints the top N number of data of given input.
    * `head file.txt` prints the top 10 (default) lines of `file.txt`.
    * `head -n 5 file.txt` prints the top 5 lines of `file.txt`.
    * `head -c 5 file.txt` prints the top 5 characters of `file.txt`.
10. `tail` - prints the last N number of data of given input.
    * `tail file.txt` prints last 10 (default) lines of `file.txt`.
    * `tail -n 3 file.txt` prints last 3 lines of `file.txt`.
11. `less` - read contents of text file one page at a time.
    * `less file.txt`
12. `cat` - reads data from file, create, view and concatenate files.
    * `cat file1.txt >> file2.txt` appends `file1.txt` to `file2.txt`.
13. `touch` - create an empty file.
    * `touch file.txt` to create an empty `file.txt`.
14. `sar` - montor Linux resources e.g., CPU, memory use, I/O device consumption, network monitoring, disk usage, process/thread allocation, battery performance.
    * `sar -u <interval> <number of reports>` shows CPU details number of reports times at specified interval
    * `sar -r <interval> <number of reports>` shows memory used, amount of memory free, available cache and buffer.
    * `sar -F <interval> <number of reports>` shows filesystems details.
    * `sar -d <interval> <number of reports>` shows block device details.
    * `sar -S <interval> <number of reports>` shows swapping details.
15. `netstat` - displays network related information such as connections, routing tables, interface statistics, etc.
    * `netstat -a` to show both listening and non-listening sockets.
    * `netstat -at` to show all TCP ports.
    * `netstat -au` to show all UDP ports.
    * `netstat -l` to show only listening ports.
    * `netstat -lt` to show listening TCP ports.
    * `netstat -s` to show statistics for all ports.
    * `netstat -pt` to show PID and program names.
    * `netstat -r` to show kernel routing information e.g., default gateway.
    * `netstat -ap | grep <program>` to show port on which program is running.
    * `netstat -an | grep ':<port>'` to show which process is using a given port.
    * `netstat -i` to show list of network interfaces
16. `tcpdump` - packet sniffing and packet analyzing tool to troubleshoot connectivity issues.
    * Used to capture, filter and analyze network traffic such as TCP/IP packets going through your system.
    * Saves captured information in a PCAP file which can b eopened through applications such as Wireshark.
    * `sudo tcpdump` to capture packets of current network interface connected to internet.
    * `sudo tcpdump -i <network interface>` to capture packets at a specific network interface.
    * `sudo tcpdump -w output.pcap -i <network interface>` to save captured packets to PCAP file.
    * `sudo tcpdump -r output.pcap` to read captured packets from file.
    * `sudo tcpdump -i <network interface> tcp` to capture only TCP packets.
    * Sample `tcpdump` output line:
    ```
    08:41:13.729687 IP 192.168.64.28.22 > 192.168.64.1.41916: Flags [P.], seq 196:568, ack 1, win 309, options [nop,nop,TS val 117964079 ecr 816509256], length 372
    ```
    * Timestamp, IPv4, source IP + port, destination IP + port, TCP flags (P=data push), sequence number (packet contains bytes 196 to 568), ack number (1 since this is the side sending the data), window size (309 bytes avaiable in the receiving buffer), TCP options, packet length (372 bytes) of the payload data.
17. `lsof` - provides a list of files that are opened and by which process.
    * `lsof` to list all opened files in the system.
    * `lsof -u <username>` to list all opened files by a user.
    * `lsof -c <process name>` to list all opened files by a process by name.
    * `lsof -p <pid>` to list all opened files by a process by PID.
    * `lsof -R` to list parent PIDs.
    * `lsof -i` to list all files opened by network connections.

## What does an `&` after a command do?

- `<command> &` runs the process in the background.
- Inherits stdout/stderr from shell so it still writes to terminal.
- Can bring to foreground with `fg`.
- Can be accessed using `%<pid>`.
- If shell receives SIGHUP, it also sends a SIGHUP to the process.

## What does `& disown` after a command do?

- `disown` removes the job from the shell's job list.
- Job will no longer received SIGHUP.
- However still connected to the terminal so if terminal is destroyed, the program will fail as soon as it tries to access stdin/stdout.
- Note: `nohup <command>` separates process from terminal.
    * Closes stdin, redirects stdout and stderr to `nohup.out`.
    * Prevents process from receiving a SIGHUP.

## What is a packet filter and how does it work?

- Packet filter is a piece of software that looks at the header of packets as they pass through and decides their fate i.e., DROP (discard as if it never received it), ACCEPT (let it pass through) or something more complicated.
- Increases control (e.g., prevent packets from going to certain outside regions), security (e.g., stop ping of death from entering), and watchfulness (e.g., look for abnormalities).
- `iptables` inserts and deletes rules from kernel's packet filtering table.
- `iptables -L --line-number` shows all rules with line number.
- `iptables -t <table name> --append INPUT -j DROP` appends a rule that drops all incoming traffic on any port.
- `iptables -t <table name> --delete INPUT 2` deletes rule 2 from INPUT chain.
- `iptables -t <table name> -A INPUT -p udp -j DROP` appends a rule to drop all UDP packets.
- `iptables -t <table name> -A INPUT -s 192.168.1.230 -j ACCEPT` to append a rule in the INPUT chain to accept all packets from 192.168.1.230.
- `iptables -t <table name> -A OUTPUT -d 192.168.1.123 -j DROP` to append a rule in the OUTPUT chain to drop all packets for 192.168.1.123.
- `iptables -t <table name> -A INPUT -i wlan0 -j DROP` to append a rule in INPUT chain to drop all packets destined for wireless interface.
- `iptables -t <table name> -A FORWARD -j DROP` to drop all packets in the FORWARD chain.
- `sudo iptables-save` to save iptables config.

## What is Virtual Memory?

- Memory management technique.
- Kernel maps program memory addresses i.e., virtual addresses into physical addresses in computer memory.
- Main storage seen by process appears as a contiguous address space.
- Memory management unit (MMU) built into CPU automatically translates virtual addresses to physical addresses.
- Benefits:
    * Frees applications from having to manage a shared memory space.
    * Increased security due to memory isolation.
    * Conceptually use more memory than physically available using technique called paging.
- Virtual address space divided into pages i.e., contiguous virtual memory addresses.
- Page tables translate virtual addresses seen by application into physical addresses used by the hardware to process instructions.
- Page tables indicate if a page is in real memory.
- Thrashing occurs when computer spends a large amount of time transferring pages to and from a backing store, slowing down useful work.
- Occurs when there is not enough memory to store working set (min number of pages) for all active programs.
- Need to add more memory or close more programs.

## What is swap and what is it used for?

- Swap space is portion of virtual memory that is on hard disk.
- Swap space is used when RAM is full.

## What is an A record, an NS record, a PTR record, a CNAME record, an MX record?

- A: Host address
    * Translates domain name into IP address.
- NS: Name server
    * Identify DNS servers responsible (authoritative) for a zone.
- PTR: Pointer
    * Reverse records that map IP addresses to domain names.
    * Looking up dmain name for `12.23.34.45` is done with a PTR query for `45.34.23.12`.
- CNAME: Domain name aliases
    * Used to give a server multiple names (aliases)
    * Ex: `www.domain.com` and `domain.com` (A-record for `domain.com` and CNAME record for `www.domain.com` pointing to short name)
- MX: Mail exchange
    * Specify email servers responsible for a domain name
    * When sending email to `user@example.com`, email server looks up MX record for `example.com`

## Are there any other resource records and what are they used for?

- TXT: Descriptive text
    * Used too hold descriptive text e.g., who hosts it.
    * Also used for DNS verification for TLS/SSL certificates.

## What is a Split-Horizon DNS?

- Facility of a DNS implementation to provide different sets of DNS information usually selected by the source address of the DNS request.
- Use case: DNS server configured to return internal address if request from internal server; return external address if request from external server.

## What is the sticky bit?

- Sticky bit is a permission bit that is set on a file or directory that only lets the owner or root user delete or rename it.

## What does the immutable bit do to a file?

- `sudo chattr +i <filename>` sets the immutable bit of the file to prevent anyone including root user from deleting it.
- `sudo chattr -i <filename>` to remove the immutable bit.

## What is the difference between hardlinks and symlinks? What happens when you remove the source to a symlink/hardlink?

- Hardlinks share the same inode number as the source.
- Softlinks have a different inode number than the source.
```
$ touch a
$ ln a b
$ ls -i a b
24 a 24 b
$ ln -s a c
$ ls -i a c
24 a 25 c
```
- The data portion of the softlink inode is the name of the source file.
- Hardlinks are only valid in the same filesystem.
- Softlinks can be across filesystems.
- If the source is removed, hardlink would still exist and softlink would be invalid.

## What is an inode and what fields are stored in an inode?

- Data structure in Unix that contains metadata about a file.
- Data includes:
    * mode
    * owner (UID, GID)
    * size
    * atime, ctime, mtime
    * ACL's
- Note that file name is present in the parent directory's inode structure
- `ls -li <file>` to view inode number of a file
- `df -i` to check inode usage on each filesystem

## How to force/trigger a file system check on next reboot?

- Easiest way to force `fsck` filesystem check is to create an empty file called `forcefsck` in the partition's root directory.
- How a filesystem may break:
    * When a program writes to file, data is first copied into an in-core buffer in the kernel.
    * User process is allowed to proceed even if the data write may not happen long until after the write system call occurs.
    * Filesystem can become inconsistent if system is halted (unclean shutdown).
    * Blocks can become damaged on a disk drive.
- What `fsck` checks for:
    * File system size, number of inodes, free-block, free-inode count.
    * Inodes checked for inconsistencies:
        + Format and type e.g., regular, directory, block, character, FIFO, symbolic, shadow, socket.
        + State e.g., allocated, unallocated, partially allocated.
        + Duplicate block checks i.e., each inode contains pointers to blocks that should not overlap.

## What is SNMP and what is it used for?

- Simple network management protocol (SNMP) is an application protocol that collects and organizes information about managed devices on IP networks.
- SNMP talks to network to find network device activity e.g., bytes, packets, and errors transmitted and received on a router, connection speed betwen devices and number of hits a web server receives.
- Useful for network monitoring.

## What is a runlevel and how to get the current runlevel?

- Run level is a state of `init` that defines what system services are ooperating.
- To check current runlevel `runlevel` or `wh o-r`.

## What is SSH port forwarding?

- Tunneling application ports from client to server and vice versa.

## What is the difference between local and remote port forwarding?

- Local port forwarding:
    * Forward a port from client to server.
    * SSH client listens for connections on configured port, when it receives a connection, it tunnels it to an SSH server.
    * Server connects to configured destination port possibly on a different machine than SSH server.
    * Typical uses include jump servers, connecting to internal network service.
    * General: `ssh -L port:host:hostport user@server`
    * Example: `ssh -L 80:internal.server.com:80 jump.server.com`
        + Opens a connection to jump server and forwards any connections to port 80 on local machine to port 80 on the internal server.
- Remote port forwarding:
    * General: `ssh -R port:host:hostport user@server`
    * Example: `ssh -R 8080:localhost:80 public.example.com`
        + Allows anyone on the remote server to connect to TCP port 8080 on remote server.
        + Connection will then be tunneled back too the client host.
        + Client host then makes a TCP connection to port 80 on local host.
    * Useful for giving someone on the outside access to internal web server.

## What are the steps to add a user to a system without using useradd/adduser?

1. Add an entry foor user in `/etc/passwd`.
2. Add an entry for the group in `/etc/group`.
3. Create home directory for user.
4. Set new user password with `passwd`.

## What is major and minor numbers of special files?

- Major number identifies genearl class of device.
    * Kernel uses it to look up appropriate driver.
- Minor number idetifies a particular device within a general class.

## Describe the mknod command and when you'd use it.

- `mknod()` system call creates a filesystem node.
- `mode` specifies permissions and type of node (file, device special file or named pipe).
- If character or block device file then `dev` specifies major and minor numbers.

## Describe a scenario when you get a "filesystem is full" error, but 'df' shows there is free space.

- Process has opened a large file which has been deleted.
    * Need to kill process to free up the space.
    * `sudo lsof +L1` to view files that have been deleted but still open.
- Max number of inodes reached.
    * `df -i` to check.

## Describe a scenario when deleting a file, but 'df' not showing the space being freed.

- Process has opened a large file which has been deleted.
    * Need to kill process to free up the space.
    * `sudo lsof +L1` to view files that have been deleted but still open.

## Describe how 'ps' works.

- `ps` reads the proc filesystem.
- `/proc/<pid>` contains varioous files that provide info about PID.
- `strace -e open ps` shows which files are opened by `ps`.

## What happens to a child process that dies and has no parent process to wait for it and what’s bad about this?

- A zombie process has completed but it is still in the process table waiting for its parent to read its exit status.
- Parent processes normally issue the `wait` system call to read the child's exit status upon which the zombie is removed (reaped).
- `kill` does not work on zombie processes.
- When a child dies, the parent receives a `SIGCHLD` signal.
- These zombie processes can fill up the process table preventing new processes from starting.

## Explain briefly each one of the process states.

- Runnable: process can be executed
    + Just waiting for CPU time to process its data
    + As soon as it makes a system call that cannot be immediately completed, kernel puts it to sleep
- Sleeping: process waiting for resource
    + Waiting for a specific event to occur
    + Will not get CPU time unless it receives a signal or response to one of its I/O requests
- Zombie: process trying to die
    + Finished executing but have not had their status collected
    + Check their PPIDs with `ps` to see where they're coming from
- Stopped: process suspended
    + Administratively forbidden to run
    + Restarted with CONT

## How to know which process listens on a specific port?

- `netstat -ltnp | grep -w ':80'`
    * `l` to show listening sockets
    * `t` for tcp
    * `n` for nuumerical addresses
    * `p` to show process ID
    * `grep` for `:80`
- `lsof -i :80`

## What is a zombie process and what could be the cause of it?

- A zombie process has completed but it is still in the process table waiting for its parent to read its exit status.
- Parent processes normally issue the `wait` system call to read the child's exit status upon which the zombie is removed (reaped).
- `kill` does not work on zombie processes.
- When a child dies, the parent receives a `SIGCHLD` signal.

## You run a bash script and you want to see its output on your terminal and save it to a file at the same time. How could you do it?

- `./script.sh | tee out.txt`
- `tee` takes in stdin and writes to terminal and file.

## Explain what echo "1" > /proc/sys/net/ipv4/ip_forward does.

- Replaces the file content in `/proc/sys/net/ipv4/ip_forward` with `1`.

## Describe briefly the steps you need to take in order to create and install a valid certificate for the site https://foo.example.com.

- Create a certificate signed by a certificate authority e.g., using Let's Encrypt.
- Verify you own the domain e.g., via a DNS challenge where you create a TXT record with a random string.
- CA will verify the TXT record.
- Upload certificate to webserver or load-balancer, whichever is handling the TLS/SSL termination.

## Can you have several HTTPS virtual hosts sharing the same IP?

- Virtual host refers to practice oof running more than one website on a single server.
- Virtual hosts can be IP-based i.e., different IP address for every web site or name-based i.e., muultiple names running on each IP address.
- For name-based virtual hosting, server relies on client to report hostname as part of HTTP header.
- This allows many different hosts to share the same IP address.

## What is a wildcard certificate?

- A wildcard certificate is a digital certificate applied to a domain and all its subdomains.
- Example: `*.example.com`

## Which Linux file types do you know?

1. Regular
    * Create with `touch` or `vi`.
    * List with `ls -l | grep ^-`.
2. Directory
    * Create with `mkdir`.
    * List with `ls -l | grep ^d`.
3. Block
    * Hardware files mostly in `/dev`.
    * Create with `fdisk`.
    * List with `ls -l | grep ^b`.
4. Character
    * Serial stream of input/output e.g., terminals.
    * List with `ls -l | grep ^c`.
5. Pipe files
    * Named pipe FIFO.
    * Create with `mkfifo`.
    * List with `ls -l | grep ^p`.
6. Symbolic link files
    * Linked (soft/hard) files to other files.
    * Create with `ln`.
    * List with `ls -l | grep ^l`.
7. Socket files
    * Pass information between applications.
    * Create with `socket()` system call.
    * List with `ls -l | grep ^s`.

## What is the difference between a process and a thread? And parent and child processes after a fork system call?

- A process:
    * Created by the operating system
    * Requires overhead
    * Contains information about program resources and execution state
        + PID, UID, GID
        + Environment
        + Working directory
        + Program instructions
        + Registers, stack, heap
        + File descriptors
        + Signal actions
        + Shared libraries
        + Interprocess communication tools
- A thread:
    * Exists within a process and uses the process resources.
    * Has its own flow of control as long as its parent process exists.
    * May share process resources with threads that act equally independently.
    * Dies if the parent process dies.
    * Is lightweight because overhead has already been accomplished by creation of its process.
- Since threads within the same process share resources:
    * Changes made by one thread to a shared system resource will be seen by others.
    * Two pointers with same value point to the same data.
    * Reading and writing to same memory location is possible.
- Child is a clone of the parent after a `fork()` system call.

## What is the difference between exec and fork?

- Consider example of running `ls` in a terminal:
    * If `fork()` succeeds, the child shell process will run `exec /bin/ls` which will replace the copy of the child shell with itself.
    * Any parameters passed to `ls` are handled by `exec`.
    * Note that `exec()` is also a system call.

## What is "nohup" used for?

- `nohup <command>` separates process from terminal.
    * Closes stdin, redirects stdout and stderr to `nohup.out`.
    * Prevents process from receiving a SIGHUP.

## What is the difference between these two commands: `myvar=hello` and `export myvar=hello`?

- `export` makes the variables to sub-proocesses.

## How many NTP servers would you configure in your local ntp.conf?

- Network time protocol (NTP) synchronizes the time of a client server to another server within a few milliseconds of UTC.
- NTP configured using `/etc/ntp.conf`.
- Most basic NTP config uses 2 servers.
- At least two should be configured for primary and backup.

## What does the column 'reach' mean in ntpq -p output?

- `ntpq` used to query NTP servers.
- `p` flag prints a list of peers known to the server and their states
- The value in `reach` is octal and it represents the reachability register. For example, `257` value in octal is `10101111` meaning there were valid responses were not received out of 8.

## You need to upgrade kernel at 100-1000 servers, how you would do this?

- Configuration management e.g., Chef, Ansible, etc. to upgrade all controlled machines from a single server.
- For example, with Ansible, you supply a list of hosts and a playbook for upgrading and execute the playbook on all remote machines.
- Note: Ansible communicates with remote servers over SSH.

## How can you get Host, Channel, ID, LUN of SCSI disk?

- `cat /proc/scsi/scsi`

## How can you limit process memory usage?

- `ulimit` limits resources that a process can use.
- `ulimit -v` to limit amount of memory processes in a shell can use.
- `ulimit -s` to increase the allowed stack size.

## What is bash quick substitution/caret replace(^x^y)?

- Reruns previous command with substitution.
- Example:
```
$ echo foo
foo

$ ^foo^bar
bar
```

## Do you know of any alternative shells? If so, have you used any?

- Bash, ksh, zsh

## What is a tarpipe (or, how would you go about copying everything, including hardlinks and special files, from one server to another)?

- `netcat` is used to read from and write to network coonnections using TCP and UDP.
- On receiving end: `netcat -l -p 7000 | tar x`
- On sending end: `tar -cf - * | netcat otherhost 7000`

## How can you tell if the httpd package was already installed?

- `which httpd`
- `whereis httpd`
- `locate --basename '\nano'`

## How can you list the contents of a package?

- With dkpg: `dkpg -L <package>`
- With apt: `apt-file list <package>`
- With yum: `repoquery --list <package>`

## How can you determine which package is better: openssh-server-5.3p1-118.1.el6_8.x86_64 or openssh-server-6.6p1-1.el6.x86_64 ?

- Name: `openssh-server-5.3`
- Version: `5.3p1`
- Release: `118.1`
- Linux: `el6` (Enterprise Linux 6)
- Architecture: `x86_64`
- Therefore we want too use the latter since it is a newer version of the package.

## Can you explain to me the difference between block based, and object based storage?

- Block storage stores data in fixed-sized chunks.
    * No additional details associated with a block outside of address.
    * Controlling OS determines storage management.
    * OS determines where data goes in the block.
    * Use cases: databases, RAID.
- Object storage stores data in isolated containers called objects.
    * Give a single unique ID and stoore in a flat memory model.
    * Retrieve object by simply presenting ID.
    * Data could be stored local or remoote.
    * Flexible metadata.
    * Easy to scale out.

# Hard Linux Questions

## What is a tunnel and how you can bypass a http proxy?

- Tunneling traffic is sending data e.g., HTTP over a different protocol e.g., SSH.
- Use destination server as a proxy server.
- Setting up a tunnel:
    * `ssh -D 8080 user@server-to-route-to.com`
        + `D` sets up a SOCKS proxy on your local machine at port 8080.
        + Tunnel all traffic across SSH pipe.
        + As long as `ssh -D` is running, youo can set `localhost:8080` as a proxy in any application that supports it e.g., web browser, and have all traffic routed through `server-to-route-to.com`.
        + Note: In Chrome you can add `127.0.0.1:8080` into SOCKS row for proxy.

## What is the difference between IDS and IPS?

- IDS (intrusion detection system) monitors network and flag suspicious activity.
- IPS (intrusion prevention system) live in same area of network as firefall between outside woorld and internal network and proactively deny netwoork traffic based on a security profile if the packet presents a known security threat.

## What shortcuts do you use on a regular basis?

- Tab for autocomplete.
- Ctrl+c to stop program.
- Ctrl+z to send current process to background.

## What is the Linux Standard Base?

- Joint project by several Linux distributions under Linux Foundation to standardize software system structure including the filesystem hierarchy used in the kernel.
- LSB is based on POSIX (portable operating system interface) specificatioon.

## What is an atomic operation?

- Operation during which processor can simultaneously read a location and write it in the same bus operation.
- Prevents ay other processor or I/O from writing or reading memory until operation is complete.
- Linux uses a variety of atomic operatioons to provide safe and efficient behavioor in a multi-threaded environment.

## Your freshly configured http server is not running after a restart, what can you do?

- Troubleshoot:
    1. SSH onto server.
    2. `ps aux | grep http` to see if proocess is running.
    3. `journalctl -u http` to see if it had problems starting up.
    4. `vi /var/log/nginx/error.log` for more error logs.
    5. `vi /var/log/nginx/access.log` to see if any successful requests before going down.
    6. Address errors found e.g., full disk, incorrect config, missing resources, etc.
    7. `systemctl restart http`
- Note: Above only considered server side errors, and also did not consider monitoring tools.

## What kind of keys are in ~/.ssh/authorized_keys and what it is this file used for?

- Specifies the SSH keys that can be used for logging into the user account foor which the file is configured.
- Configures permanent access using SSH keys.

## I've added my public ssh key into authorized_keys but I'm still getting a password prompt, what can be wrong?

- `~/.ssh/authorized_keys` must be writable only by you i.e., `700`, `755` or `775`
- `~/.ssh/authorized_keys` must be readable i.e., at least `400`
- Private key on local machine must be readable and writable only by you i.e., `600`

## What does :(){ :|:& };: do on your system?

- This is a fork bomb.
- It defines a function called `:` which calls itself and pipes to itself in the background.
- Need to reboot the system.

## How do you catch a Linux signal on a script?

- `trap` allows you to execute a command when a signal is received by your script.
- `trap arg signals`
    * `signals` is a list of signals to intercept.
    * `arg` is a command to execute.
- Example: `trap "echo 'hello'; exit" SIGHUP SIGINT SIGTERM`
- Note: `SIGKILL` cannot be trapped.

## Can you catch a SIGKILL?

- No, kernel immediately terminates any process sent this signal without signal handling.

## What's happening when the Linux kernel is starting the OOM killer and how does it choose which process to kill first?

## Describe the linux boot process with as much detail as possible, starting from when the system is powered on and ending when you get a prompt.

## What's a chroot jail?

## When trying to umount a directory it says it's busy, how to find out which PID holds the directory?

## What's LD_PRELOAD and when it's used?

## You ran a binary and nothing happened. How would you debug this?

## What are cgroups? Can you specify a scenario where you could use them?

## How can you remove/delete a file with file-name consisting of only non-printable/non-type-able characters?

## How can you increase or decrease the priority of a process in Linux?