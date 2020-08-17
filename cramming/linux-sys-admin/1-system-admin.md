## Table of Contents
[Chapter 2 - Scripting and the Shell](#Chapter-2---Scripting-and-the-Shell)

## Chapter 2 - Scripting and the Shell

### Shell Basics

### Bash Scripting

### Regular Expressioons

### Python Scripting

## Chapter 3 - Booting and Shutting Doown

### Bootstrapping

- Standard term for starting up
- Process:
    1. Read boot loader from master boot record
    2. Load and initialize the kernel
    3. Detect device and configuratioon
    4. Create kernel processes
    5. Admin intervention (single-user mode only)
    6. Execute startup scripts
- Path to kernel typically `/boot/vmlinuz`
- First stage, system ROM loads boot loader into memory from disk
- Boot loader then arranges for kernel to be loaded
- Kernel checks what hardware are present
- Kernel creates "spontaneous" (i.e., not via `fork`) processes in user space
    * `init` is PID 1 which is accompanied by several memory and kernel handler processes e.g., `kjournald`, `kswapd`
- Once above is done kernel's role in bootstrapping is complete
- `init` handles creating proocesses for basic operations (e.g., logins) and starting daemons
- Startup scripts are normal shell scripts run by `init`
- System daemons (e.g., DNS and SMTP servers) are accepting connections

### GRUB: The Grand Unified Bootloader

- GRUB is the default boot loader for Linux running with Intel processors
- GRUB default boot configuration in `/boot/grub/grub.conf`
- Example:
```
default=0  # Default run level
timeout=10 # Waits 10 seconds for user input before running default
splashimage=/boot/grub/spash.xpm.gz
title Red Hat Enterprise Linux Server (2.6.18-92.1.10.el5)
    root (hd0,0) # Root file system
    kernel /vmlinuz-2.6.18-92.1.10.el5 ro root=LABEL=/ # Location of kernel in /boot
```

### Booting to Single-User Mode

- Placeholder

### Working with Startup Scripts

- `init` executes system startup scripts
- Scripts kept in `/etc/init.d` and links to them are made in `/etc/rc0.d`, `/etc/rc1.d`, etc
- Common tasks performed:
    * Setting host name, timezone
    * Checking disks with `fsck`
    * Mounting system's disks
    * Removing files from `/tmp`
    * Configuring network interfaces
    * Starting daemons and network services
- `init` run levels:
    0. system is shut down
    1. single-user; no network with minimal software
    2-5. support for networking
    6. reboot level
- `/etc/inittab` tells `init` what to do at each run level
- `telinit` changes `init` run level after startup
- Startup scripts live in `/etc/init.d`
    * Start and stop individual services
- `/etc/rc<level>.c/S<sequence><name>` contains sym links to files in `/etc/init.d`
    * `<level>` tells `init` which level to run these scripts
    * `<sequence>` tells `init` in what order to run the scripts
    * `S` indicates start
    * `K` indicates kill (not shown)

### Rebooting and Shutting Down

- `shutdown` is the safest way to halt or reboot a system
    * `/sbin/shutdown`
    * `shutdown -h` halts the system
    * `shutdown -r` reboots the system

## Chapter 4 - Access Control and Rootly Powers

- Placeholder

## Chapter 5 - Controlling Processes

- Process represents a running program
    * Object through which a program's use of memory, processor time and I/O resouorces can be managed

### Components of a Process

- Process consists of address space and set of data structures in the kernel
- Address space is a set of memory pages the kernel has marked for process's use
    * Contains code, libraries, variables, stacks
- Kernel internal data structure contains info about processes:
    * Address space map
    * Process status (sleeping, stopped, etc)
    * Execution priority
    * Resources used
    * File and network ports processes opened
    * Owner of process
- Thread is a fork in execution of a process
- Multiple threads can execute concurrently via multi-threading
- Threads can run simultaneously on different cores
- Kernel assigns a unique ID to every process (PID)
- Existing process must clone itself to create a new process
    * Original process is the parent and copy is child
- Process UID is the user ID of who created it
    * Usually only the creator and the super-user can manipulate a process
- Process GID is the group identificatioon number of a process
- Process's scheduling priority determines how much CPU time it receives
    * User can set `nice` value to set priority of processes
- Non-daemon processes have an associated control terminal
    * Controls default linkages for stdin, stdout and stderr channels

### Lifecycle of a Process

- Process copies itself with `fork` system call
- New process has a distinct PID
- Child proocess use one of the `exec` family of system calls to begin execution of a new program
- All processes are descendents of `init`
- When process completes it calls `_exit` to notify kernel it is ready to die
- Supplies exit code (`0` means successful)
- Kernel requires death be acknowledged by process's parent which parent does with call to `wait`
- If parent dies first, kernel recognizes that no `wait` will be forthcoming and adjusts processes to make orphan a child of `init`
- `init` accepts these orphaned processes and performs `wait` needed to get rid of them when they die

### Signals

- Signals are process-level interrupt requests
- Used in a variety of ways:
    * Sent among processes to communicate
    * Sent by terminal to kill, interrupt or suspend a proocess
    * Sent by admin `kill` to achieve various ends
    * Sent by kernel when a process commits an infraction
    * Sent by kernel to notify an interesting event e.g., death of a child proocess or availability of data on an I/O channel
- When signal is received one of tw othings can happen:
    * Receiving proocess designated a handler route for a particular signal then handler is called
        + Known as catching the signal
        + Once handler is complete, execution restarts from when signal was received
        + Signal can also be blocked by process
    * Kernel takes some default action on behalf of process
- Important signals:
    * 1 = HUP (catch, block, no core dump)
        + Sent by terminal driver to clean up (kill) processes attached to a particular terminal
        + `bash` shells can use `nohup` to make sure process runs even after user is logged oout
    * 2 = INT (catch, block, no core dump)
        + Sent by terminal driver with control-c
        + Request to terminate the current operation
    * 3 = QUIT (catch, block, no core dump)
        + Similar to TERM except it defaults to producing a core dump it not caught
    * 9 = KILL (cannot catch, cannot block, no core dump)
        + Unblockable and terminates processes at the kernel level
        + Process can never actually receive this signal
    * 11 = SEGV (catch, block, dump)
    * 15 = TERM (catch, block, no core dump)
        + Request to terminate execution completely
        + Receiving process will clean up its state and exit

### KILL: Send Signals

- `kill` used to terminate a process
- Default is the TERM signal (`15`)
- Can be used by users to kill their own processes or root to kill any process
- `kill [-signal] pid`
- `kill -9 pid` guarantees proocess will die because signal `9` cannot be caught
- `killall` kills proocesses by name e.g., `sudo killall httpd` kills all Apache webserver processes
- Running `killall` as root kills `init` and shuts down the machine
- `pgrep` and `pkill` searches processes by name and displays or kills them respectively
- `sudo pkill -u ben` kills all processes by user `ben`

### Process States

- Process execution states:
    * Runnable - process can be executed
        + Just waiting for CPU time to process its data
        + As soon as it makes a system call that cannot be immediately completed, kernel puts it to sleep
    * Sleeping - process waiting for resource
        + Waiting for a specific event to occur
        + Will not get CPU time unless it receives a signal or response to one of its I/O requests
    * Zombie - process trying to die
        + Finished executing but have not had their status collected
        + Check their PPIDs with `ps` to see where they're coming from
    * Stopped - process suspended
        + Administratively forbidden to run
        + Restarted with CONT

### Nice and Renice: Influence Scheduling Priority

- Niceness of a process is a numeric hint to kernel about how process should be prioritized for CPU time
- High nice means low priority
- Low nice means high priority
- Range from `-20` to `19`
- Child process by default inherits niceness of parent
- Nice has no effect on kernel's management of its memory or I/O
- `nice -n 5 ~/bin/longtask` lowers priority (raises nice) by 5
- `sudo renice -5 8829` sets nice value of pid 8829 to 5
- `sudo renice 5 -u boggs` sets nice value of bogg's processes to 5

### PS: Monitor Proocesses

- `ps` is sys admin's main tool for monitoring processes
- Output of `ps aux`:
```
USER PID %CPU %MEM VSZ  RSS TTY STAT  TIME COMMAND
root 1   0.1  0.2  3356 560 ?   S     0:00 init [5]
root 2   0    0    0    0   ?   SN    0:00 [ksoftirqd/0]
root 3   0    0    0    0   ?   S<    0:00 [events/0]
root 4   0    0    0    0   ?   S<    0:00 [khelper]
root 5   0    0    0    0   ?   S<    0:00 [kacpid]
root 18  0    0    0    0   ?   S<    0:00 [kblockd/0]
root 28  0    0    0    0   ?   S     0:00 [pdflush]
…
```
- `a` to show all proocesses, `u` for users oriented and `x` to show proocesses that don't have a control terminal
- `VSZ` = virtual size of process
- `RSS` = resident set size (number of pages in memory)
- `TTY` = control terminal ID
- `STAT` = current process status (`R` is runnable, `S` is sleeping, `Z` is Zombie, `T` is stopped)
- `TIME` is CPU time process has consumed
- Output of `ps lax`:
```
F UID PID PPID PRI NI VSZ RSS WCHAN STAT TIME COMMAND
4 0 1 0 16 0 3356 560 select S 0:00 init [5]
1 0 2 1 34 19 0 0 ksofti SN 0:00 [ksoftirqd/0
1 0 3 1 5-10 0 0 worker S< 0:00 [events/0]
1 0 4 3 5-10 0 0 worker S< 0:00 [khelper]
```
- `l` shows long output
- `PPID` = parent ID
- `NI` = nice value
- `WCHAN` = type of resource for which process is waiting

### Dynamic Monitoring with TOP, PRSTAT and TOPAS

- `ps` offers a static snapshot
- `topo` regularly updates summary oof active proocesses and their use of resources
- Output of `top`:
```
top - 16:37:08 up 1:42, 2 users, load average: 0.01, 0.02, 0.06
Tasks: 76 total, 1 running, 74 sleeping, 1 stopped, 0 zombie
Cpu(s): 1.1% us, 6.3% sy, 0.6% ni, 88.6% id, 2.1% wa, 0.1% hi, 1.3% si
Mem: 256044k total, 254980k used, 1064k free, 15944k buffers
Swap: 524280k total, 0k used, 524280k free, 153192k cached
PID USER PR NI VIRT RES SHR S %CPU %MEM TIME+ COMMAND
3175 root 15 0 35436 12m 4896 S 4.0 5.2 01:41.9 X
3421 root 25 10 29916 15m 9808 S 2.0 6.2 01:10.5 rhn-applet-gui
1 root 16 0 3356 560 480 S 0.0 0.2 00:00.9 init
2 root 34 19 0 0 0 S 0.0 0 00:00.0 ksoftirqd/0
3 root 5 -10 0 0 0 S 0.0 0 00:00.7 events/0
4 root 5 -10 0 0 0 S 0.0 0 00:00.0 khelper
5 root 15 -10 0 0 0 S 0.0 0 00:00.0 kacpid
18 root 5 -10 0 0 0 S 0.0 0 00:00.0 kblockd/0
```
- Most CPU-consuming processes appear at top

### /proc Filesystem

- `ps` and `top` read process infoo from `/proc` directory
- `/proc` is a psuedo-filesystem in which kernel expooses info
- Less popular info must be read directly from `/proc`
- Process-specific info is divided into sub-directories named by PID e.g., `/proc/1` for `init`
- Most useful per-process file:
    * `cmd` = command process is running
    * `cmdline` = complete command line of process
    * `cwd` = symbolic link to process directory
    * `environ` = process env variables
    * `exe` = symbolic link to file being executed
    * `fd` = sub-directory with links for each open file descriptor
    * `maps` = memory mapping info
    * `root` = symbolic link to process root directory
    * `stat` = general process status info
    * `statm` = memory usage info

### STRACE: Trace Signals and System Calls

- `strace` allows youo to directly observe a process
- Shwos every system call process makes and every signal it receieves
- Output of `sudo strace -p 5810` where 5810 is PID of `top`:
```
gettimeofday({1116193814, 213881}, {300, 0}) = 0
open("/proc", O_RDONLY|O_NONBLOCK|O_LARGEFILE|O_DIRECTORY) = 7
fstat64(7, {st_mode=S_IFDIR|0555, st_size=0, ...}) = 0
fcntl64(7, F_SETFD, FD_CLOEXEC) = 0
getdents64(7, /* 36 entries */, 1024) = 1016
getdents64(7, /* 39 entries */, 1024) = 1016
stat64("/proc/1", {st_mode=S_IFDIR|0555, st_size=0, ...}) = 0
open("/proc/1/stat", O_RDONLY) = 8
read(8, "1 (init) S 0 0 0 0 -1 4194560 73"..., 1023) = 191
close(8)
```
- Shows every system call and code kernel returns

### Runaway Processes

- Two kinds of runaway processes:
    1. Consume excessive amounts of resources e.g., CPU or disk space
        * Identify by using `ps` or `top`
        * `uptime` to show load averages over 1, 5 and 15-minute intervals
        * Use `top` to check memory consumption
        * `df -k` shows filesystem use; look for filesystem that is 100% full
        * `du` on the identified filesystem too find which directory using the most space
        * Repeat until the large files are discoovered
        * Try using `lsof` to see which process is writing the excessively large file
    2. Suddenly go berserk and exhibit wild behavioros

## Chapter 6 - The Filesystem

### Pathnames

- Placeholder

### Filesystem Mounting and Unmounting

- Filesystems are attached to the tree with the `mount` command
- `mount` maps a directory within the existing file tree (mount point) too the root of the newly attached filesystem
- Example: `sudo mount /dev/sda4 /users`
    * Installs filesystem stored on disk partition `/dev/sda4` under path `/users`
    * `ls /users` to see filesystem's coontents
- `/etc/fstab` to view list of filesystems currently mounted
- `umount` to detach a filesystem but will not work if in use
- `fuser` to find which process hold references to that filesystem
- Example: `fuser -c /usr` output:
```
/usr: 157tm 315ctom 474tom 5049tom
```
- The above shows the pids along with some system dependent codes e.g., `t` means process is executing a file
- Alternative to `fuser` is `lsof`

### Organization of the File Tree

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

### File Types

- Types of files; symbol used by `ls`, created by; removed by
    1. Regular files; `-`; editors, `cp`, etc; `rm`
        * Series of bytes
        * Text files, data files, executable prooograms, shared libraries
    2. Directory; `d`; `mkdir`; `rmdir`
        * Contains named references to other files
        * `ln oldfile newfile` to create hard links
    3. Character device file; `c`; `mknod`; `rm`
        * Device files let programs communicate with system's hardware and peripherals
        * Kernel loads driver software for each of the system's devices
        * Presents a standard communication interface that looks like a regular file
        * Allow drivers to do their own input and output buffering
        * Files typically in `/dev`
    4. Block device file; `b`; `mknod`; `rm`
        * Files used by drivers that handle I/O in large chunks
    5. Local domain socket; `s`; `socket(2)`; `rm`
        * Coonnections between processes that allow process communication
        * Local domain sockets accessible oonly from local host and are referred to throuogh a filesystem object rather than a network port
        * Created with `socket` system call
        * Removed with `rm` or `unlink` system call
        * NOT THE SAME AS NETWORK SOCKETS
    6. Named pipe; `p`; `mknod`; `rm`
        * Allow communication between two processes on the same host
    7. Symbolic link; `l`; `ln -s`; `rm`
        * Soft link points to oa file by name
        * Hard link is a direct reference whereas a soft link is a reference by name
        * Soft links are distinct from the files they point to
- Use `rm -i` to get confirmation before deletion

### File Attributes

- Placeholder

### Access Control Lists

- Placeholder

## Chapter 7 - Adding New Users

- Placeholder

## Chapter 8 - Storage

- Placeholder

## Chapter 9 - Periodic Processes

- Placeholder

## Chapter 10 - Backups

- Placeholder

## Chapter 11 - Syslog and Log Files

- `syslog` log files contain events from multiple sources e.g., kernel and network daemon

### Finding Log Files

- Many randomly-named log files
- By default most are found in `/var/log`
- Logs generally owned by `root`
- Less privileged daemons e.g., `httpd` may require write access and set the ownership appropriately
- `/etc/syslog.conf` sets config
- Keep separate partition for `/var` or `/var/log` too avoid filling up the disk and bringing down the system

### Files Not to Manage

- `wtmp` contains a record oof user's logins/logouts as well as reboots/shut downs
- `lastlog` records only time of last login of each user
- `utmp` keep record of each user currently logged in
- `syslog` manages:
    * `auth.log` for `sudo`
    * `cron`
    * `daemon.log`
    * `debug`
    * `kern.log`
    * `mail`
    * `messages`
    * `syslog`
    * `warn`
- Logs that are set by config files:
    * `apt`
    * `boot.log`
    * `httpd`

### Vendor Specifics

- Use `logrotate` for rotating, truncating and managing logs
- New software packages can add a config file to `/etc/logrotate.d` to set up log management strategy

## Chapter 12 - Software Installation and Management

- Placeholder

## Chapter 13 - Drivers and the Kernel

- Placeholder