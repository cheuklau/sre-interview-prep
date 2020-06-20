## Table of Contents
- [Chapter 1 - Introduction](#Chapter-1---Introduction)
- [Chapter 2 - Preparing the Host System](#Chapter-2----Preparing-the-Host-System)
- [Chapter 3 - Packages and Patches](#Chapter-3---Packages-and-Patches)
- [Chapter 4 - Final Preparations](#Chapter-4---Final-Preparations)
- [Chapter 5 - Constructing a Temporary System](#Chapter-5---Constructing-a-Temporary-System)

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

### Chapter 4 - Final Preparations

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
