# Lecture 31

## Operating System Virtualization

- How do we create a virtual OS (container)?
    * Start with a real OS
    * Create software responsible for isolating guest software inside the container
        + That software seems to lack a canonical name and today its actually a bunch of different tools
    * Container resources (processes, files, network sockets, etc) are provided by the real OS but visibility outside the container is limited
- What are the implications?
    * Container and real OS share same kernel
    * So apps inside and outside the kernel must share same ABI
    * Challenges is getting this to work are due to shared OS namespaces

## Containers vs VMs

- You can run Windows inside a container provided by Linux: False, containers shares the kernel with the host
- You can run SUSE Linux isnide an Ubuntu container: True, as long as both distributions use the same kernels, differences aree confined to different binary tools and file locations
- Running `ps` inside trhe container will show all processes: False, container process namespaces is isolated from the host

## Hypervisor vs Container Virtualization

- Hypervisor virtualization
    * Server Hardware
    * Host OS
    * Hypervisor
    * Guest OSes
    * Binaries/libraries
    * Apps
- Container virtualization
    * Server hardware
    * Host OS
    * Binaries/libraries
    * Apps

## Why Virtualize an OS?

- Shares many of the same benefits of hardware virtualization with much lower overhead
- Decoupling
    1. Cannot run multiple OS on the same machine
    2. Can transfer software setups to another machine as long as it has an identical or nearly identical hardware kernel
    3. Can adjust ahrdware container resources to system needs
- Isolation
    1. Container should not leak info inside and outside the container
    2. Can isolate all of the config and software packages a particular app needs to run

## OS vs. Hardware Overhead

- Hardware virtualization system call path
    * App inside the VM makes a system call
    * Trap to the host OS (or hypervisor)
    * Hand trap back to guest OS
- OS virtualization system call path
    * App inside the container makes a system call
    * Trap to the OS
    * Remember all of the work we had to do to deprivilege the guest OS and deal with uncooperative machine architectures like x86?
        + OS virrtualization does not require any of this: there is only one OS

## OS Virutalization is About Names

- What kind of names must the container virtualize
    * Process IDs
        + `top` inside the container shows only processes running inside container
        + `top` outside container may show processes inside the container but with different pids
    * File names
        + Processes inside the container may have a limited or different view of mounted file system
        + File names may resolve to different naems and some file names outside the container may be removed
    * User names
        + Containers may have different users with different roles
        + `root` inside the container should not be root outside the container
    * Host name and IP address
        + Processes inside the container may use a different host name and IP address when performing network operations

## OS Virtualization is About Control

- OS may want to ensure that the entire container cannot consume more than a certain amount of
    * CPU time
    * Memory
    * Disk or network I/O
- Forms of OS virutalization go back to `chroot` (run command or interactive shell with special root directory)
    * Instead of starting path resolution at inode #2 , start sometwhere else
- Modern container management systems e.g., Docker combine and build upon multiple lower-level tools and services

## Linux Namespaces

- Linux has provided namespace separation for a variety of resources that typically had unified namespaces
    * Mount points: allows different namespaces to see different views of the file system
    * Process IDs: new processes are allocated IDs in their current namespace and all parent namespaces
    * Network: namespaces can have private IP addresses and their own routing tables, and can communciate with other namespaces through virtual interfaces
    * Devices: devices can be present or hidden in different namespaces

## Cgroups

- Cgroups is a Linux kernel feature that limits, accounts for, and isolates the resource usage of a collection of processes
- Processes and their children remain in the same cgroup
- cgroups make it possible to control the resources allocated to a set of processes

## UnionFS

- A stackable unification file system
- Path name resolution:
    * Does `/foo/bar` exist in the top layer; if yes, return its contents
    * Does `/foo/bar` exist in the next layer; if yes, return its contents
    * Etc
- Can also hide parts of the lower file system
    * Does `/foo/bar` exist in the top layer; if yes, return its contents
    * Access to `/ff` in the next layer is prohibted, so stop

## COW File System

- Previous container libraries made a copy of the parent's entire file system
- What could we do instead
    * Copy on write
    * Only make modifications to underlying file system when the container modifies files
    * Speeds start up and reduces storage usage
        + The container mainly needs read-only access to host files

## What is Docker?

- Docker builds on previous technologies
    * Provides a unified set of tools for container management on a variety of systems
    * Layered file system images for easy updates
    * Now involved in development of containerization libraries on Linux
