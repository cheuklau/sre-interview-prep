# Source

This document covers the questions here:

https://syedali.net/engineer-interview-questions/

# Unix Processes

## What is the difference between a process and a thread?

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

## What is a Zombie process?

- A zombie process has completed but it is still in the process table waiting for its parent to read its exit status.
- Parent processes normally issue the `wait` system call to read the child's exit status upon which the zombie is removed (reaped).
- `kill` does not work on zombie processes.
- When a child dies, the parent receives a `SIGCHLD` signal.

## How to daemonize a process?

- `fork()` system call to create a separate process.
- `setsid()` system call to detach process from the parent (normally a shell).
- Standard files (stdin, stdout, stderr) need to be reopened.

## Describe ways of inter-process communication.

- Message queues
    * Linked list of messages stored within the kernel.
    * To create a new queue use `msgget()` system call.
    * To add a message to end of queue use `msgsnd()`.
    * To receive a message use `msgrcv()`.
    * Processes must share a common key to access the queue.
- Shared memory
    * Multiple processes given access to same memory block creating a shared bugger for processes to communicate.
    * `shm_open()` creates a new shared memory object.
    * `ftruncate()` allocates some number of bytes to object.
    * `mmap()` get a pointer to the shared memory
    * Writer creates a semaphore with `sem_open()` to ensure exclusive access to the shared memory.
    * Otherwise a race condition would occur if writer was writing and reader was reading at the same time.
    * `sem_post()` releases lock so reader can read.
    * `munmap()` to unmap shared memory from address space.
- Anonymous pipes
    * Has a write end and a read end for FIFO order.
    * One process writes to the pipe and another one reads.
    * Example: `sleep 5 | echo "hello"`
- Named pipes
    * Processes write to and read from a named pipe as if it were a regular file.
    * This is unlike anonymous pipes which use stdin and stdout.
- Domain sockets
    * Enable channel-based communication for process on the same host.
    * Note: This is different from a network socket which allows communication across hosts which need support from an underlying protocol (e.g., TCP or UDP).
    * ICP sockets rely on local system kernel to support communication.
    * ICP sockets use a local file as a socket address.
    * Sockets configured as streams are bidrectional and control follows a client/server pattern.
    * Server steps:
        1. `socket()` to get a file descriptor for the socket connection
        2. `bind()` to bind the socket to an address on the host
        3. `listen()` to listen for client requests
        4. `accept()` to accept a particular client request

## Describe how processes execute in a Unix shell.

- When you run a program e.g., `ls` in the shell, the shell first searches its `path` for an executable named `ls`.
- Typically this is located in `/bin/ls`.
- The shell will call `fork()` to create a copy of itself.
- If `fork()` succeeds, the child shell process will run `exec /bin/ls` which will replace the copy of the child shell with itself.
- Any parameters passed to `ls` are handled by `exec`.
- Note that `exec()` is also a system call.

## What are Unix signals?

- Signals are an IPC method.
- Default `kill` signal is `SIG-TERM` (15).
- `SIG-KILL` (9) cannot be handled by a process and causes it to be forecefully killed.
- Use `kill()` system call to send signals to a process.
- `SIG-HUP` (1) is used to reset or hang up processes when its controlling terminal is closed.
- `SIG-STOP` (17) also cannot be handled by a process. It pauses the process in its current state and waits for `SIG-CONT` to resume.
- Note: `raise()` system call can be used to send a signal to a thread.

## When you send a HUP signal to a process, you notice it has no impact, why?

- Some processes setup signal blocking during critical section execution.
- This is done by using `sigprocmask()` system call to mask certain signals.
- It is possible process was masking `SIG-HUP`.
- It will be handled once the signal is unblocked from the pending.

# Networking

## Define TCP slow start

- Congestion control algorithm.
- Increases TCP congestion window each time an `ACK` is received until an `ACK` is not received.
- This prevents the link between the sender and receiver from being overloaded.
- Note: This is different than the sliding window maintained by receiver which exists to prevent the receiver from being overloaded.

## Name a few TCP connection states

- `LISTEN` - server is listening on a port e.g., HTTP 80
- `SYN-SENT` - sent a `SYN` request, waiting for a response
- `SYN-RECEIVED` - server waiting for an `ACK` occurs after sending an `ACK` from server
- `ESTABLISHED` - 3 way TCP handshake has completed

## Define the various protocol states of DHCP

- Dynamic host configuration protocol (DHCP) is a network management protocol used on IP networks where a DHCP server dynamically assigns IP addresses and other network configuration parameters to each device on the network so they can communicate with other IP networks.
- `DHCPDISCOVER`: client to server: broadcast to locate server
- `DHCPOFFER`: server to client: offer client configuration parameters
- `DHCPREQUEST`: client to server: request HDCP configuration from server
- `DHCPACK`: server to client: actual configuration parameters
- `DHCPNAK`: server to client: indicates client's notion of network address is wrong
- `DHCPDECLINE`: client to server: address is already in use
- `DHCPRELEASE`: client to server: giving up IP address
- `DHCPINFORM`: client to server: asking for local config parameters

## How do you figure out the network and broadcast address of a network given a netmask?

- A netmask determines the size of a subnet.
- The first address is the network address.
- The last address is the broadcast address.
- All addresses in between are the host addresses.
- Example: `192.128.64.7/24`
    * Here `/24` represents the netmask which corresponds to `255.255.255.0`
    * In this case, the whole of the last octet consists of host bits.
    * Therefore, the host address is `192.128.64.0` and the broadcast address is `192.128.64.255`
    * Hosts can be between `192.128.64.1` and `192.128.64.254`

## Describe a UDP and TCP packet fields

- UDP packets (32 bits total)
    * Source port (16 bits)
    * Destination port (16 bits)
- TCP packets
    * Source port (16 bits)
    * Destination port (16 bit)
    * Sequence number (32 bits) - number assigned to the first byte of data in the current message
    * Acknowledge number (32 bits) - value of next sequence number that sender of segment is expecting to receive if `ACK` control bit is set
    * Data offset - number of 32-bit words contained in TCP header
    * Reserved (6 bits) - for future use
    * Flags (6 bits)
        1. `URG` - urgent data placed
        2. `ACK` - acknowledgement number is valid
        3. `PSH` - data should be passed to application as soon as possible
        4. `RST` - reset connection
        5. `SYN` - synchronize sequence numbers to indicate connection
        6. `FIN` - sender has finished sending data
    * Window (16 bits) - size of sender's receive window (buffer space available for incoming data)
    * Checksum (16 bits) - if header was damaged in transit
    * Urgent pointer (16 bits) - points to first urgent data byte in packet
    * Options - various TCP options
    * Data - contains upper-layer information

## Difference between TCP and UDP

- Reliable vs. unreliable
- Ordered vs. unordered
- Heavyweight vs. lightweight
- Streaming
- Header size
- Examples: TCP used in HTTP, UDP used in DNS, FTP

## What are the different kinds of NAT available?

- Network address translation (NAT) is a method of remapping an IP address space into another by modifying network address information in the IP header of packets while they are in transit across a traffic routing device.
- One internet-routable IP of a NAT gateway can be used for an entire private network.
- Source network address translation (SNAT) is when source IP is RFC 1918 (private network) and is changed to non-RFC 1918 (public network) e.g., home laptop connecting to router which changes source address of TCP/IP packet to be it's external public IP.
- Destination network address translation (DNAT) is when the destination IP is changed e.g., router changes destination address of TCP/IP packet to be the private IP.

## Explain the SOA record in DNS

- Start of Authority (SOA) record is a DNS resource record containing administrative information for a domain
- To find the DNS SOA record: `dig rackspace.com +nssearch`
- This will return:
```
SOA ns.rackspace.com. hostmaster.rackspace.com. 1392389079 300 300 1814400 300 from server 69.20.95.4 in 12 ms.
```
- `ns.rackspace.com` is the primary name server for the domain
- `hostmaster.rackspace.com` is the email for the domain
- `1392389079` is the revision number which changes every time you update the domain
- `300` is the refresh time which is the number of seconds before the zone refreshes
- `300` is the retry time which is the number of seconds before a failed refresh is retried
- `1814400` is the time in seconds before data is considered unreliable
- `300` is the minimum TTL that applies to all resource records in the zone
- Note: DNS zone is a distinct part of a domain namespace delegated to a legal entity i.e., person, company

# Filesystems

## List open file handles

- File handles can be regular files, directories, block/character devices, sockets, pipes, etc.
- File handes are objects that a process uses to read or write to an open file, open network sockets, etc.
- Each process has its own file descriptor table.
- `lsof -p <pid>`
- `ls /proc/<pid>/fd`

## What is an inode?

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

## Difference between soft and hard link?

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

## When would you use a hardlink over a softlink?

- Hardlinks are useful when source file is moved around because renaming the source does not remove the hardlink connection.
- Softlinks are broken if the source is renamed.
- This is because hardlinks share the same inode whereas soflink uses the source filename in it's data portion.
- Softlinks are useful when you are working across filesystems.

## Describe LVM and how it can be helpful

- Logical volume managers (LVM) group disks into logical units.
- The basic unit of an LVM is a physical extent (PE).
- A disk may be divided into one or more PEs.
- One or more PEs are contained in a volume group (VG).
- One or more logical volumes (LV) are created out of a VG.
- Example:
    * Server with two 1TB disk drives.
    * Create two PEs of 500GB on each disk.
        + Disk one has PE1 and PE3.
        + Disk two has PE2 and PE4.
    * Create VG0 from PE1 and PE2.
    * Create VG1 from PE3 and PE4.
    * We can create a LV called `/root` and another one called swap on VG0.
- Advantage of LVM is that we can create software RAID i.e., we can join multiple disks into one bigger disk.
- We cannot specify a RAID level with LVM, but we can choose which PEs we want in a VG.
- List operations:
    * `pvs` to show PVs
    * `vgs` to show VGs
    * `lvs` to show LVs
    * `lsblk` to show partition information (includes PV. VG and LV breakdown)
- Create operations:
    * `pvcreate /dev/sdc` to create a new PV called `/dev/sdc` to be managed by LVM
    * `vgcreate vg01 /dev/sdc` to create a new VG called `vg01` using `/dev/sdc` PV
    * `vgextend vg01 /dev/sdd` to extend the VG `vg01` to another `/dev/sdd` PV
    * `lvcreate -n lv01 -l 100%VG vg01` to create a LV `lv01` that utilizes 100% of `vg01` VG

## What is `md` and how do you use it?

- MD is Linux software RAID where kernel has a RAID driver which takes one or more disks and does RAID across them.
- It makes use of RAID possible without a hardware RAID controller.

## What are some reasons to consider one filesystem over another e.g., XFS over EXT?

- Ext2:
    * Max file size = 2TB
    * Max volume size = 4TB
    * POSIX permissions and file compression
    * Key weakness: takes a very long time to recover if shutdown abruptly
    * Writes files to `LOST+FOUND`, however ext2 `fsck` utility will check the entire filesystem which takes a while
- Ext3:
    * Does everything Ext2 can
    * Includes a journal which records all operations, therefore after an abrupt shutdown, `fsck` will just check files which were left incomplete
    * Note that journal does take some overhead
- Ext4:
    * Max file size = 16TB
    * Max volume size = 1 exabyte
    * Max number of files = 4 billion
    * Also uses a journal with checksum to ensure the journal is not corrurpted

## What is RAID and define a few RAID levels

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

## If a filesystem is full and you see a large file that is taking up a lot of space, how do you make space on that filesystem?

- Delete the file if no process has the filehandle open.
    * `lsof <filename>` to list processes that have the file open.
- If a process has the filehandle open, it is better to not delete.
    * Instead, `cp /dev/null <filename>` to reduce its size to zero.
- A filesystem has a reserve, you can reduce this reserve to create more space using `tunefs`.
    * `tune2fs -l /dev/partition | grep "Reserved"` shows the reserved blocks that are unusable
    * `tune2fs -m2 /dev/partition` to lower the reserved block by 2%.

## What is the difference between a character and a block device?

- Block devices are buffered and read/written in fixed sizes e.g., hard disks, cd-roms.
- Character devices read/write one character at a time and are not buffered e.g., from keyboard or a tty (terminal).

