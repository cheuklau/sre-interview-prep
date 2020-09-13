# Pucit-Booting Process

## Overview of Booting Process

1. BIOS/UEFI
    * Basic Input Output System (BIOS) is now replaced by Unified Extensible Firmware Interface (UEFI)
    * Performs Power On Self Test (POST)
    * Hand over control to the Master Boot Record
2. MBR
    * Master Boot Record
    * First sector of bootable disk
    * Stage 1 boot loader
    * Hands over control to Grand Unified Boot Record
3. GRUB
    * Default bootloader of Linux
    * Main task is to load kernel into memory
4. Kernel
    * Initializes itself
    * Loads initial RAM disk image which contains temporary file system with different loadable kernel modules which loads the actual filesystem
    * After actual filesystem loaded into memory
    * Forks and executes systemd
5. Systemd
    * Also called init in previous verions
    * Executes different user space processes and scripts to bring the system into normal state typically graphical.target or multi-user.target
    * Gives interface for user to interact with it

## Brief Overview of Motherboard

- Processor (CPU) connected to Northbridge chip (also known as the memory controller) via a Front Side bus
    * 33 pins for address (2^33)
    * 64 pins for data (2^33*8bytes=64GB)
- Northbridge chip connected to:
    * RAM via DDR channels
    * Graphics card
- Northbridge chip connected to Southbridge chip via DMI interface
- Southbridge chip connected to:
    * BIOS (flash memory)
    * Serial ATA ports
    * USB ports
    * Power management
    * Clock generation
    * PCI Bus

## BIOS/UEFI initialization

- Press power buttion
- Once motherboard is powered up it initializes its own firmware and tries to get the CPU running
- Chooses one of the processor as the bootstrap processor (BSP), remaining processors called application processors (AP) which are halted until they are activated by the kernel
- BSP is in real mode with memory paging disabled
- Instruction pointer EIP contains address known as the reset vector (0xFFFFFFF0 - 16 bytes below 4GB)
    * This is a jump instruction that goes to 0xF0000
    * This is the BIOS entry point and spans 1MB
- BSP executes the BIOS code
    * Power on self test: tests various hardware componets
        + Ex. BIOS emits long beeps for problems e.g., video card problems and displays problem on screen
    * Locates booting device (e.g., hard disk, USB flask, optical disk, machine on network, etc)
    * CMOS contains priority of booting devices (normally hard disk)
    * BIOS reads the first sector (1st 512B) of hard disk and loads it to memory addddress 0x7C00
    * BIOS is now done
- Note: UEFI is replacing BIOS

## Master Boot Record

- Contents of MBR:
    1. Code (440 bytes) - this is the actual MBR
    2. Disk signature (4 bytes)
    3. Nulls (2 byutes)
    4. Partition table (4 16-byte entries)
    5. MBR signature (2 bytes)
- Above contents make up the Stage 1 boot loader
- `dd if=/dev/sda bs=440 count=1 | hexdump -C` to view MBR code
- Cannot load kernel using MBR as it has no concept of filesystem
- All MBR does is:
    * Load the actual boot loader

## The Boot Loader

- A boot loader is the first software program that runs when a computer starts
- For Linux: LILO, GRUB, GRUB2 (used by most latest Linux distros)
- Three stages of GRUB2:
    1. Stage 1 boot loader `boot.img` (446 bytes) stored in MBR loads stage 1.5 boot loader
    2. Stage 1.5 boot loader (30kb) in `core.img` resides right after MBR before the first partition
        * Contains file system drivers and loadable kernbel modules that enable stage 1.5 to load stage 2 bootloader
    3. Stage 2 bootloader (GRUB2)
        * `ls /boot` to see files belong to GRUB2
            + `vmlinuz-*` is the compressed bootable linux kernel image
            + `initrd.img` contains device drivers to allow bootloader to get the final file system
            + `system.map` contains symbolt table used by kernel
            + `config-*` contains configuration parameters for linux kernel
        * `/etc/default/grub` contains GRUB configurations
        * `update-grub` for changes to take place

## Kernel initialization

- Kernel is uncompressed and loaded into memory
- Kernel initializes itself after being loaded
    * Needs to mount the root `/` file system
    * LVM, RAID, NFS are not compiled into Linux kernel, but are rather in `/lib/modules` which is on the root file system itself
    * How does the Linux Kernel access the loadable kernel modules required for mounting the root file system located in `/lib/modules`?
    * Solution: `/boot/initrd.img` is uncompressed and then loaded
        + Temporary file system which contains directories and files e.g., `/bin`, `/dev`, `/lib` which contains the loadable kernel modules required for mounting the actual root filesystem
    * Kernel executes `pivot_root` which removes temporary file system to permanent file system
    * Kernel initializes scheduler PID=0
    * Forks and executes `/sbin/init` or `/bin/systemd` both of which these days are softlinks to `lib/systemd/systemd`
    * `systemd` responsible for establishing all other user space processes
        + Then it moves to the background

## Systemd

* Older Linux distributions (e.g., Ubuntu 14, Debian 6, Centos 6) all used `init`
* Newer Linux distributions (e.g., Ubuntu 15, Debian 7, Centos 7) all use `systemd`
* Systemd has faster booting, prompt is shown within a couple of seconds
* For System V init, login is not available until all startup processes are complete
* System V has 7 run levels:
    0. Power off
    1. Rescue
    2. Multi-user without networking
    3. Multi-user with network
    4. Unused
    5. Graphical
    6. Reboot
* Systemd targets
    - `poweroff.target`
    - `rescue.target`
    - `multi-user.target`
    - `graphical.target`
    - `reboot.target`
* `ls /etc/rc5.d`
    * Shows scripts that are executed based on numbering in file name
    * The files are softlinks to `/etc/init.d`
    * This is systemv way of initialization
* `systemctl`
* `ls /lib/systemd/system/runlevel*.target` to show all systemd target files
    - We can see how `runlevel5.target` map to run level init script by running `systemctl list-dependencies graphical.target` to see which targets `graphical.target` depends on
    - We can see that these targets correlate to the scripts that run level 5 runs