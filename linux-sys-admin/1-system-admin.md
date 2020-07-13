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

- Placeholder

## Chapter 12 - Software Installation and Management

- Placeholder

## Chapter 13 - Drivers and the Kernel

- Placeholder