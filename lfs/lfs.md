## Table of Contents
- [Chapter 1 - Introduction](#Chapter-1---Introduction)
- [Chapter 2 - Preparing the Host System](#Chapter-2----Preparing-the-Host-System)

### Chapter 1 - Introduction

The LFS system will be built using an already installed Linux distribution (e.g., Debian). The existing host provides the compiler, linker and shell to build the new system.

Breakdown of this book:
- Chapter 2 will create a new partition and file system where the LFS system will be compiled and installed.
- Chapter 3 explains which packages need to be downloaded to build the LFS system.
- Chapter 4 sets up the working environment.
- Chapter 5 explains installation of packages that form the basic development suite. Some packages are needed to resolve circular dependencies e.g., to compile a compiler. After Chapter 5, LFS no longer depends on the host except for the running kernel.
- Chapter 6 builds the full LFS system. We use `chroot` to start a new shell whose root directory is in the LFS partition. This is similar to rebooting and telling the kernel to mount the LFS partition as the root partition.
- Chapter 7 sets up basic system configurations.
- Chapter 8 creates the kernel and boot loader. After this step, the computer can be rebooted into the new LFS system.

### Chapter 2 - Preparing the Host System

My starting point:
- AWS EC2, t2.micro
- Ubuntu 18.04 AMI

Ran `code/host_check.sh` to verify that the host OS has the pre-reqs for LFS. The following checks failed:

```
ERROR: /bin/sh does not point to bash
Binutils: version-check.sh: line 9: ld: command not found
version-check.sh: line 10: bison: command not found
yacc not found
version-check.sh: line 30: gcc: command not found
version-check.sh: line 31: g++: command not found
version-check.sh: line 36: m4: command not found
version-check.sh: line 37: make: command not found
version-check.sh: line 43: makeinfo: command not found
version-check.sh: line 45: g++: command not found
g++ compilation failed
```

To fix the errors:

```
ln -sf bash /bin/sh
apt-get update
apt-get install -y binutils
apt-get install -y bison
apt install -y build-essential # includes gcc, g++, make
apt install -y texinfo
```

#### Creating a New Partition

LFS is installed on a dedicated partition (min 10 GB). Use disk partitioning program e.g., `cfdisk` or `fdisk` to create a new partition.

0. Create a new EBS volume `/dev/xvdf` and mounted it to the EC2 instance.
1. Run `fdisk -l` to show the available partitions.
2. Run `fdisk /dev/xvdf`
3. Press `n` to create a new partition.
4. Use the default values for start and end blocks.

Next we set up the file system on the blank partition. We create an `ext4` file system on the LFS partition: `mkfs -v -t ext4 /dev/xvdf`. For convience we set `$LFS` to the name of the directory where we will build the LFS system: `export LFS=/mnt/lfs`. Next we mount the partitioon at the chosen mount point:

```
mkdir -pv $LFS
mount -v -t ext4 /dev/xvdf $LFS
```

If you want the LFS partition remounted at boot, we need to add the following line to `/etc/fstab`:

```
/dev/xvdf /mnt/lfs ext4 defaults 1 1
```

### Chapter 3 - Packages and Patches

First, create a directory to unpack the sources and build them:

```
mkdir -v $LFS/suorces
```

Make the directory writable and sticky (oonly owner of a file can delete it).

```
chmod -v a+wt $LFS/sources
```

Download all packages and patches:

```
wget --input-file=wget-list --continue --directory-prefix=$LFS/sources
```

Verify all packages are available before proceeding:

```
pushd $LFS/soources
md5sum -c md5sums
popd
```