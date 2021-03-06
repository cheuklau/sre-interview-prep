## Table of Contents
- [Chapter 1 - Introduction](#Chapter-1---Introduction)
- [Chapter 2 - Preparing the Host System](#Chapter-2----Preparing-the-Host-System)
- [Chapter 3 - Packages and Patches](#Chapter-3---Packages-and-Patches)
- [Chapter 4 - Final Preparations](#Chapter-4---Final-Preparations)
- [Chapter 5 - Constructing a Temporary System](#Chapter-5---Constructing-a-Temporary-System)
- [Chapter 6 - Installing Basic System Software](#Chapter-6---Installing-Basic-System-Software)
- [Chapter 7 - System Configuration](#Chapter-7---System-Configuration)

## Chapter 1 - Introduction

The LFS system will be built using an already installed Linux distribution (e.g., Debian). The existing host provides the compiler, linker and shell to build the new system.

Breakdown of this book:
- Chapter 2 will create a new partition and file system where the LFS system will be compiled and installed.
- Chapter 3 explains which packages need to be downloaded to build the LFS system.
- Chapter 4 sets up the working environment.
- Chapter 5 explains installation of packages that form the basic development suite. Some packages are needed to resolve circular dependencies e.g., to compile a compiler. After Chapter 5, LFS no longer depends on the host except for the running kernel.
- Chapter 6 builds the full LFS system. We use `chroot` to start a new shell whose root directory is in the LFS partition. This is similar to rebooting and telling the kernel to mount the LFS partition as the root partition.
- Chapter 7 sets up basic system configurations.
- Chapter 8 creates the kernel and boot loader. After this step, the computer can be rebooted into the new LFS system.

## Chapter 2 - Preparing the Host System

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

## Chapter 3 - Packages and Patches

First, create a directory to unpack the sources and build them:

```
mkdir -v $LFS/sources
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
pushd $LFS/sources
md5sum -c md5sums
popd
```

## Chapter 4 - Final Preparations

#### Creating the $LFS/tools Directory

The `$LFS/tools` directory will keep programs compiled in Chapter 5. These programs are temporary tools that are not part of the final LFS system, and will be discarded.

```
mkdir -v $LFS/tools
```

Create a simlink on the host system.

```
ln -sv $LFS/tools /
```

#### Add the LFS User

We will build packages as non-root user. We create a user `lfs` and member of grooup `lfs`.

```
groupadd lfs
useradd -s /bin/bash -g lfs -m -k /dev/null lfs
```

Note that `-s` is the shell, `-g` is the group, `-m` creates a home directory, and `-k` prevents copying files from a skeleton directory i.e., `/etc/skel`. Assign `lfs` a password.

```
passwd lfs
```

Grant `lfs` access to `$LFS/tools` and `$LFS/sources` by making it owner.

```
chown -v lfs $LFS/tools
chown -v lfs $LFS/sources
```

Login as user `lfs`

```
su - lfs
```

#### Setting up the Environment

Create a new bash profile:

```
cat > ~/.bash_profile << "EOF"
exec env -i HOME=$HOME TERM=$TERM PS1='\u:\w\$ ' /bin/bash
EOF
```

When logged on as `lfs`, initial shell is a login shell which reads `/etc/profile` of the host then `.bash_profile`. The `exec env...` command replaces the running shell with a new one with an empty environment except for `HOME`, `TERM` and `PS1` variables. The new shell is non-login which does not read `/etc/profile` or `.bash_profile` but instead reads `.bashrc`. Create the `.bashrc` file:

```
cat > ~/.bashrc << "EOF"
set +h
umask 022
LFS=/mnt/lfs
LC_ALL=POSIX
LFS_TGT=$(uname -m)-lfs-linux-gnu
PATH=/tools/bin:/bin:/usr/bin
export LFS LC_ALL LFS_TGT PATH
EOF
```

Consierations:
- `+h` turns off hashing so that bash searches `PATH` (`$LFS/tools`) instead of a hash function when looking for executables
- Setting `umask` to `022` ensures newly created files and directories are only writable to owner but readable and executable by anyone
- `LFS` set to mount point
- `LC_ALL` controls localization of certain programs
- `LFS_TGT` sets the machine description
- We add `/tools/bin` in front of standard `PATH` so that the programs we install in Chapter 5 are picked up first

Source the newly created user profile:

```
source ~/.bash_profile
```

#### About SBUs

Standard Build Unit (SBU) is a standardized metric of time it takes for a build to complete.

#### About the Test Suites

Test suite for the core toolchain packages (GCC, Binutils and Glibc) are the most importance due to their central role in a properly functioning system.

## Chapter 5 - Constructing a Temporary System

To build the minimal system:
1. Build a new and host-independent toolchain (compiler, assembler, linker, libraries, and utilities).
2. Use this toolchain to build the other essential tools.

We will store the tools in this chapter in `$LFS/tools`.

### Toolchain Technical Notes

- Binutils installs its assembler and linker in `/tools/bin` and `/tools/$LFS_TGT/bin`.
- Next package installed is GCC.
- Next installed are Linux API headers which allow Glibc to interface with Linux kernel features.
- Next package installed is Glibc for the compiler, binary tools and kernel headers.
- Next we do a second pass oof Binutils.
- Finally we do a second pass of GCC.
- At this point the core toolchain is self-contained and self-hosted. The rest of the packages are built against the new Glibc in `/tools`.

### General Compilation Instructions

For each package that was downloaded into `/mnt/lfs/sources`:
1. Extract the package with `tar`.
2. Change into the expanded directory.
3. Build the package as specified below.
4. Delete the extracted source directory.

Install the following packages:
- Binutils (Pass 1)
    * Contains a linker, assembler and other tools for handling object files.
    * Run:
    ```
    mkdir -v build
    cd build
    ../configure --prefix=/tools \
                 --with-sysroot=$LFS \
                 --with-lib-path=/tools/lib \
                 --target=$LFS_TGT \
                 --disable-nls \
                 --disable-werror
    make
    case $(uname -m) in x86_64)
        mkdir -v /tools/lib && ln -sv lib /tools/lib64 ;;
    esac
    make install
    ```
- GCC (Pass 1)
    * Contains the GNU compiler collection, which includes the C and C++ compilers
    * Run:
    ```
    tar -xf ../mpfr-4.0.2.tar.xz
    mv -v mpfr-4.0.2 mpfr
    tar -xf ../gmp-6.2.0.tar.xz
    mv -v gmp-6.2.0 gmp
    tar -xf ../mpc-1.1.0.tar.gz
    mv -v mpc-1.1.0 mpc
    for file in gcc/config/{linux,i386/linux{,64}}.h
    do
        cp -uv $file{,.orig}
        sed -e 's@/lib\(64\)\?\(32\)\?/ld@/tools&@g' \
            -e 's@/usr@/tools@g' $file.orig > $file
        echo '
    #undef STANDARD_STARTFILE_PREFIX_1
    #undef STANDARD_STARTFILE_PREFIX_2
    #define STANDARD_STARTFILE_PREFIX_1 "/tools/lib/"
    #define STANDARD_STARTFILE_PREFIX_2 ""' >> $file
        touch $file.orig
    done
    case $(uname -m) in
        x86_64)
            sed -e '/m64=/s/lib64/lib/' \
                -i.orig gcc/config/i386/t-linux64
        ;;
    esac
    mkdir -v build
    cd build
    ../configure \
        --target=$LFS_TGT \
        --prefix=/tools \
        --with-glibc-version=2.11 \
        --with-sysroot=$LFS \
        --with-newlib \
        --without-headers \
        --with-local-prefix=/tools \
        --with-native-system-header-dir=/tools/include \
        --disable-nls \
        --disable-shared \
        --disable-multilib \
        --disable-decimal-float \
        --disable-threads \
        --disable-libatomic \
        --disable-libgomp \
        --disable-libquadmath \
        --disable-libssp \
        --disable-libvtv \
        --disable-libstdcxx \
        --enable-languages=c,c++
    make
    make install
    ```
- Linux API Header
    * Linux API Headers expose the kernel's API for use by Glibc.
    * Run:
    ```
    make mrproper
    make headers
    cp -rv usr/include/* /tools/include
    ```
- Glibc
    * Contains the main C library. Provides basic routines for allocating memory, searching directories, opening na dlcosing files, reading and writing files, string handling, pattern matching, math, etc.
    * Run:
    ```
    mkdir -v build
    cd build
    ../configure \
        --prefix=/tools \
        --host=$LFS_TGT \
        --build=$(../scripts/config.guess) \
        --enable-kernel=3.2 \
        --with-headers=/tools/include
    make
    make install
    ```
- Libstdc++
    * Standard C++ library needed to compile C++ code (part of GCC written in C++).
    * Run:
    ```
    cd $LFS/sources/gcc-9.2.0
    mkdir -v build
    cd build
    ../libstdc++-v3/configure \
        --host=$LFS_TGT \
        --prefix=/tools \
        --disable-multilib \
        --disable-nls \
        --disable-libstdcxx-threads \
        --disable-libstdcxx-pch \
        --with-gxx-include-dir=/tools/$LFS_TGT/include/c++/9.2.0
    make
    make install
    ```
- Binutils (pass 2)
    * Contains linker, assembler and other tools for handling object files
    * Run:
    ```
    CC=$LFS_TGT-gcc \
        AR=$LFS_TGT-ar \
        RANLIB=$LFS_TGT-ranlib \
        ../configure \
        --prefix=/tools \
        --disable-nls \
        --disable-werror \
        --with-lib-path=/tools/lib \
        --with-sysroot
    make
    make install
    make -C ld clean
    make -C ld LIB_PATH=/usr/lib:/lib
    cp -v ld/ld-new /tools/bin
    ```
    * Note that above now uses the new cross-compiler instead of the ones on the host
- GCC (pass 2)
    * Contains GNU compiler with C and C++ compilers.
    * Run:
    ```
    cat gcc/limitx.h gcc/glimits.h gcc/limity.h > \
    `dirname $($LFS_TGT-gcc -print-libgcc-file-name)`/include-fixed/limits.h
    # Change location of GCC linker to the one in /tools
    for file in gcc/config/{linux,i386/linux{,64}}.h
    do
    cp -uv $file{,.orig}
    sed -e 's@/lib\(64\)\?\(32\)\?/ld@/tools&@g' \
    -e 's@/usr@/tools@g' $file.orig > $file
    echo '
    #undef STANDARD_STARTFILE_PREFIX_1
    #undef STANDARD_STARTFILE_PREFIX_2
    #define STANDARD_STARTFILE_PREFIX_1 "/tools/lib/"
    #define STANDARD_STARTFILE_PREFIX_2 ""' >> $file
    touch $file.orig
    done
    # Change default directory name for 64-bit libraries
    case $(uname -m) in
    x86_64)
    sed -e '/m64=/s/lib64/lib/' \
    -i.orig gcc/config/i386/t-linux64
    ;;
    esac
    # Unpack GMP, MPFR and MPC packages
    tar -xf ../mpfr-4.0.2.tar.xz
    mv -v mpfr-4.0.2 mpfr
    tar -xf ../gmp-6.2.0.tar.xz
    mv -v gmp-6.2.0 gmp
    tar -xf ../mpc-1.1.0.tar.gz
    mv -v mpc-1.1.0 mpc
    # Build again
    sed -e '1161 s|^|//|' \
    -i libsanitizer/sanitizer_common/sanitizer_platform_limits_posix.cc
    mkdir -v build
    cd build
    CC=$LFS_TGT-gcc \
    CXX=$LFS_TGT-g++ \
    AR=$LFS_TGT-ar \
    RANLIB=$LFS_TGT-ranlib \
    ../configure \
    --prefix=/tools \
    --with-local-prefix=/tools \
    --with-native-system-header-dir=/tools/include \
    --enable-languages=c,c++ \
    --disable-libstdcxx-pch \
    --disable-multilib \
    --disable-bootstrap \
    --disable-libgomp
    make
    make install
    ln -sv gcc /tools/bin/cc
    ```
- TCL
    * Contains Tool Command Language.
    * Support running test suites for GCC and Binutils.
    * Run:
    ```
    cd unix
    ./configure --prefix=/tools
    make
    TZ=UTC make test
    make install
    chmod -v u+w /tools/lib/libtcl8.6.so
    make install-private-headers
    ln -sv tclsh8.6
    ```
- Expect
    * Contains a program for running scripted dialogues with other interactive programs.
    * Run:
    ```
    cp -v configure{,.orig}
    sed 's:/usr/local/bin:/bin:' configure.orig > configure
    ./configure --prefix=/tools \
        --with-tcl=/tools/lib \
        --with-tclinclude=/tools/include
    make
    make test
    make SCRIPTS="" install
    ```
- DejaGNU
    * Contains framework for testing other programs
    * Run:
    ```
    ./configure --prefix=/tools
    make install
    make check
    ```
- M4
    * Coontains a macroprocessor
    * Run:
    ```
    sed -i 's/IO_ftrylockfile/IO_EOF_SEEN/' lib/*.c
    echo "#define _IO_IN_BACKUP 0x100" >> lib/stdio-impl.h
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Ncurses
    * Run:
    ```
    sed -i s/mawk// configure
    ./configure --prefix=/tools \
        --with-shared \
        --without-debug \
        --without-ada \
        --enable-widec \
        --enable-overwrite
    make
    make install
    ln -s libncursesw.so /tools/lib/libncurses.so
    ```
- Bash
    * Contains the Bourne-Again Shell
    * Run:
    ```
    ./configure --prefix=/tools --without-bash-malloc
    make
    make tests
    make install
    ln -sv bash /tools/bin/sh
    ```
- Bison
    * Contains a parser generator
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Bzip2
    * Contains programs for compressing and decompressing files
    * `bzip2` has better compressioon percentage than traditional `gzip`
    * Run:
    ```
    make -f Makefile-libbz2_so
    make clean
    make
    make PREFIX=/tools install
    cp -v bzip2-shared /tools/bin/bzip2
    cp -av libbz2.so* /tools/lib
    ln -sv libbz2.so.1.0 /tools/lib/libbz2.so
    ```
- Coreutils
    * Contains utilities for showing and setting basic system characteristics
    * Run:
    ```
    ./configure --prefix=/tools --enable-install-program=hostname
    make
    make RUN_EXPENSIVE_TESTS=yes check
    make install
    ```
- Diffutils
    * Contains programs that show differences between files or directories
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- File
    * Contains utility foor deftermining the type of a given file or files
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Findutils
    * Contains programs to find files
    * Recursively search throough directory tree and to create, maintain and search a database
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Gawk
    * Contains programs to manipulate text files
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Gettext
    * Contains utilities for internalization and localization
    * Allow programs to be coompiles with native language support
    * Run:
    ```
    ./configure --disable-shared
    make
    make check
    make install
    ```
- Grep
    * Contain programs for searching through files
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Gzip
    * Contains programs for compressing and decompressing files
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Make
    * Contains a program for compiling packages
    * Run:
    ```
    ./configure --prefix=/tools --without-guile
    make
    make check
    make install
    ```
- Patch
    * Contains a program for modifying or creating files by applying a patch file created by the diff program.
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Perl
    * Contains Practical Extraction and Report Language
    * Run:
    ```
    sh Configure -des -Dprefix=/tools -Dlibs=-lm -Uloclibpth -Ulocincpth
    make
    cp -v perl cpan/podlators/scripts/pod2man /tools/bin
    mkdir -pv /tools/lib/perl5/5.30.1
    cp -Rv lib/* /tools/lib/perl5/5.30.1
    ```
- Python
    * Run:
    ```
    sed -i '/def add_multiarch_paths/a \ return' setup.py
    ./configure --prefix=/tools --without-ensurepip
    make
    make install
    ```
- Sed
    * Contains a stream editor
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Tar
    * Contains an archiving program
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Texinfo
    * Coontains programs for reading, writing and converting info pages
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```
- Xz
    * Contains program for compressing and decompressing files
    * Run:
    ```
    ./configure --prefix=/tools
    make
    make check
    make install
    ```

### Stripping

We can remove unnecessary items. We can remove uneeded debugging tools:
```
strip --strip-debug /tools/lib/*
/usr/bin/strip --strip-unneeded /tools/{,s}bin/*
```
Remove documentation:
```
rm -rf /tools/{,share}/{info,man,doc}
```
Remove unneeded files:
```
find /tools/{lib,libexec} -name \*.la -delete
```

### Change Ownership

Current `$LFS/tools` is owned by `lfs` user who only exists on the host system. We change ownership to `root`:
```
chown -R root:root $LFS/tools
```

## Chapter 6 - Installing Basic System Software

### Introduction

- Start constructing the LFS system by chrooting into the temporary mini Linux system, make a few final preparations and begin installing the packages

### Preparing Virtual Kernel File Systems

- Various file systems exported by the kernel are used to communicate with the kernel itself
- These file systems reside in memory
- Create directories onto which file systems will be mounted
```
mkdir -pv $LFS/{dev,proc,sys,run}
```
- When kernel boots the system, it needs a few device nodes i.e., `console` and `null` devices
    * Must be created on hard disk before `udevd` is started
    * Create the devices:
    ```
    mknod -m 600 $LFS/dev/console c 5 1
    mknod -m 666 $LFS/dev/null c 1 3
    ```
- Bind mount host system's `/dev` :
```
mount -v --bind /dev $LFS/dev
```
- Mount remaining virtual kernel filesystems:
```
mount -vt devpts devpts $LFS/dev/pts -o gid=5,mode=620
mount -vt proc proc $LFS/proc
mount -vt sysfs sysfs $LFS/sys
mount -vt tmpfs tmpfs $LFS/run
```

### Package Management Techniques

### Install in Separate Directories

- Package manager tracks installation of files making it easy to remove and upgrade packages
- Each package is installed in a separate directory e.g., `/usr/pkg/foo-1.1` and a symlink is made from `/usr/pkg/foo` to `/usr/pkg/foo-1.1`
- Env vars e.g., `PATH`, `LD_LIBRARY_PATH`, `MANPATH`, `INFOPATH` need to be expanded to include `/usr/pkg/foo`
- For more than a few packages, this scheme becomes unmanageable

### Symlink Style Package Management

- Similar to previous scheme but instead of making the symlink, each file is symlinked into `/usr`
- This removes need to alter env vars
- Example:
```
./configure --prefix=/usr
make
make DESTDIR=/usr/pkg/libfoo/1.1 install
```

### Timestamp Based

- File is timestamped before installation of the package
- After installation, `find` can generate a log of all files instawlled after the timestamp file was created

### Tracing Installation Scripts

- Record commands that installation scripts perform

### Creating Package Archives

- Package installation faked into a separate tree similar to Symlink style package management
- After installation a package is archived using the installed files
- Archive used to install the package on local machine
- Used by RPM, APT

### User Based Management

- Each package is installed as a separte user
- Files belonging to a package are found by checking user ID
- This scheme is unique to LFS

### Entering the Chroot Environment

- Now we enter chroot environment to build and install final LFS system
- Enter realm populated with temporary tools
```
chroot "$LFS" /tools/bin/env -i \
 HOME=/root \
 TERM="$TERM" \
 PS1='(lfs chroot) \u:\w\$ ' \
 PATH=/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin \
 /tools/bin/bash --login +h
```
- No need to use `LFS` env var anymore because all work will be restricted to the LFS filesystem

### Creating Directories

- Create a standard directory tree
```
mkdir -pv /{bin,boot,etc/{opt,sysconfig},home,lib/firmware,mnt,opt}
mkdir -pv /{media/{floppy,cdrom},sbin,srv,var}
install -dv -m 0750 /root
install -dv -m 1777 /tmp /var/tmp
mkdir -pv /usr/{,local/}{bin,include,lib,sbin,src}
mkdir -pv /usr/{,local/}share/{color,dict,doc,info,locale,man}
mkdir -v /usr/{,local/}share/{misc,terminfo,zoneinfo}
mkdir -v /usr/libexec
mkdir -pv /usr/{,local/}share/man/man{1..8}
mkdir -v /usr/lib/pkgconfig
case $(uname -m) in
 x86_64) mkdir -v /lib64 ;;
esac
mkdir -v /var/{log,mail,spool}
ln -sv /run /var/run
ln -sv /run/lock /var/lock
mkdir -pv /var/{opt,cache,lib/{color,misc,locate},local}
```

### Creating Essential Files and Symlinks

- Create symbolic links that will be replaced by real files after software installation:
```
ln -sv /tools/bin/{bash,cat,chmod,dd,echo,ln,mkdir,pwd,rm,stty,touch} /bin
ln -sv /tools/bin/{env,install,perl,printf} /usr/bin
ln -sv /tools/lib/libgcc_s.so{,.1} /usr/lib
ln -sv /tools/lib/libstdc++.{a,so{,.6}} /usr/lib
ln -sv bash /bin/sh
```
- Create `/etc/passwd`:
```
cat > /etc/passwd << "EOF"
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/dev/null:/bin/false
daemon:x:6:6:Daemon User:/dev/null:/bin/false
messagebus:x:18:18:D-Bus Message Daemon User:/var/run/dbus:/bin/false
nobody:x:99:99:Unprivileged User:/dev/null:/bin/false
EOF
```
- Create `/etc/group`:
```
cat > /etc/group << "EOF"
root:x:0:
bin:x:1:daemon
sys:x:2:
kmem:x:3:
tape:x:4:
tty:x:5:
daemon:x:6:
floppy:x:7:
disk:x:8:
lp:x:9:
dialout:x:10:
audio:x:11:
video:x:12:
utmp:x:13:
usb:x:14:
cdrom:x:15:
adm:x:16:
messagebus:x:18:
input:x:24:
mail:x:34:
kvm:x:61:
wheel:x:97:
nogroup:x:99:
users:x:999:
EOF
```
- Initialize log files:
```
touch /var/log/{btmp,lastlog,faillog,wtmp}
chgrp -v utmp /var/log/lastlog
chmod -v 664 /var/log/lastlog
chmod -v 600 /var/log/btmp
```
- `wtmp` records all logins/logouts
- `lastlog` records when each user last logged in
- `faillog` records failed login attempts
- `btmp` records bad login attempts
- Install following programs:
    * Linux API Headers
    * Man pages
    * Glibc
    * Zlib
    * Bzip2
    * Xz
    * File
    * Readline
    * M4
    * Bc
    * Binutils
    * GMP: math library
    * MPFR: functions for multiple precision math
    * MPC
    * Attr
    * Acl: utilities to admininster access control lists
    * Shadow: handles passwords in a secure way
    * GCC: GNU compiler collection
    * Pkg-config
    * Ncurses
    * Libcap: user-space interfaces to Linux kernel
    * Sed
    * Psmisc: displays information about running processes
    * Iana-etc: provides data for network services and protocols
    * Bison: parser generator
    * flex: programs that recognize patterns in text
    * grep
    * bash
    * libtool
    * GDBM
    * Gperf: generates perfect hash function from a key set
    * Expat: parses XML
    * Inetutils: program for basic networking (e.g., ifconfig, ping)
    * perl
    * xml
    * Intltool
    * Autoconf
    * Automake
    * Kmod: libraries and utilities for loading kernel modules
    * Gettext
    * Elfutils
    * Libffi
    * Openssl
    * python
    * ninja
    * meson
    * coreutils: shows basic system characteristics (e.g., cat, chown, date, cut, echo, head, ls, rm, rmdir, etc)
    * check: unit testing framework for C
    * difutils: differences between files or directories
    * gawk
    * findutil: programs to find files
    * groff: programs for processing and formatting text
    * grub: grand unified bootloaded
    * less
    * gzip
    * zstd
    * IPRoute2: program for basic and advanced IPV4-based networking
    * kbd
    * libpipeline
    * make
    * patch
    * man-db
    * tar
    * texinfo
    * vim
    * procps-ng: programs for monitoring processes (e.g., ps)
    * util-linux: misc utility programs (e.g., fsck)
    * e2fsprogs: handles ext2 file system
    * sysklogd: programs for logging system messages (e.g., syslogd)
    * sysvinit: controls startup, running and shutdown of system

### Cleaning Up

- Clean up extra files:
```
rm -rf /tmp/*
```

## Chapter 7 - System Configuration

### Introduction

- Booting involves several tasks:
    * Mount virtual and real file systems
    * Initialize devices
    * Activate swap
    * Check file systems
    * Mount any swap partitions or files
    * Set system clock
    * Bring up network
    * Start daemons
    * Perform user tasks

### System V

- System V is a classic boot process
- Consists of a small program `init` that sets up basic programs e.g., `login` and runs a script
- Script called `rc` controols executioons of a set of other scripts that performs tasks to initialize the system
- `init` controlled by `/etc/inittab` file organized into run files:
    0. halt
    1. single user
    2. multi-user, no networking
    3. full multi-user
    4. user definable
    5. full multi-user with display
    6. reboot
- Advantages:
    * Established, easy to customize
- Disadvantages:
    * Slower to boooot
    * Serial processing of boot tasks
    * Does not directly support advanced features e.g., control groups (cgroups) and per-user fair share scheduling
    * Adding scripts requires manual, static sequencing decisions

### LFS-Bootscripts

- Contains set of scripts to start/stop LFS system at bootup/shutdown
- Install LFS-bootscripts which include:
    * checkfs: chechks integrity of filesystem
    * cleanfs: removes files that should not be preserved between reboots
    * console: loads keymap table for keyboard layout
    * functions: common functions e.g., error and status checking
    * halt: halts the system
    * ifdown: stops network device
    * ifup: starts network device
    * localnet: sets up system hostname and loopback device
    * modules: loads kernels in `/etc/sysconfig/moodules`
    * mountfs: mounts filesystems
    * network: sets up network interfaces
    * rc: master run-level control script; runs all bootscripts one-by-one
    * reboot: reboots the system
    * sendsignals: makes sure every process is terminated before system reboots or halts
    * setclock
    * swap: enables and disables swap files and partitions
    * sysctl: loads system config values from `/etc/sysctl.conf`
    * sysklogd: starts and stops system and kernel log daemons
    * template
    * udev: prepares `/dev` directory and starts `Udev`
- Install in `/etc/rc.d`, `/etc/init.d`, `/etc/sysconfig`, `/lib/services`, `/lib/lsb`

### Overview of Device and Moodule Handling

- Linux traditionally used a static device creation method
- Device nodes created under `/dev` with a `MAKEDEV` script which contains a number of calls to the `mknood` program with the device numbers for every possible device that might exist
- With `UDev` only devices detected by kernel gets device noodes created for them
    * Stored on a `devtmpfs` file system

### Udev Implementation

#### Sysfs

- `sysfs` knows about which devices are present on the system because drivers compiled into the kernel directly registers their objects with `sysfs`
- Once `sysfs` is mounted on `/sys` data which the drivers reguster are available to othe userspace processes and to `udevd`

#### Device Node Creation

- Device files are created by kernel throuogh `devtmpfs`
- Any driver that wants to register a device noode goes through `devtmpfs`
- When a `devtmpfs` instance is mounted on `/dev` the device node will be created with name, permission, and owner
- Later kernel will send a uevent to `udevd` which will create additional symlinks to device node or change its permissions, owner or group
    * Based on rules in `/etc/udev/rules.d`

#### Handling Dynamic Devices

- When you plug in a USB MP3 player, kernel recognizes device is connected and generates a uevent
- Uevent is then handled by `udevd` as described above