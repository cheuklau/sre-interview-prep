# Lecture 5

## Binary Software Packages

- A binary package is a collection of files bundled into a single file containing
    * Executable files
    * man/info pages
    * copyright info
    * configuration and installation scripts
- It is easy to install softwares from binary packages built for your machine and OS as the dependencies are already resolved
- For Debian distributions (Ubuntu, Kali, Mint), they come in `.deb` format and package managers are available e.g., `apt`, `dpkg`
- For Redhat-based distributions (Fedora, CentOS, OpenSuse), they come in `.rpm` format and availbable package managers are `rpm` and `yum`

## Open-Source Software Packages

- Open-source software is a software with source code made available with license in which copyright holder provides rights to study, change and distribute software to anyone and for any purpose (GNU GPL)
- Normally distributed as a tarball with:
    * Source code files
    * README and INSTALL
    * AUTHORS
    * Configure script
    * `Makefile.am` and `Makefile.in`
- Source package is eventually converted into a binary package for a platform on which it is configured, built and installed
- Normally use source packages to install softwares because:
    1. We cannot find a corresponding binary package
    2. We want to enchance functionalities of a software
    3. We want to fix a bug in a software
- Download options:
    * Download via ftp or `wget`
    * Use advanced packaging tool `sudo apt-get source hello`
    * Use github
- Source package is eventually converted into a binary for a platform on which it is configured, built and installed
    * Many times we all have recited the following magic spell to install a unix open-source tarball:
        + `./configure`
        + `make`
        + `sudo make install`
- Example:
```
mkdir hellopackage
cd hellopackage
wget ftp://ftp.gnu.org/gnu/hello/hello-2.10.tar.gz
tar xzf hello-2.10.tar.gz
cd hello-2.10
```
- `src` contains source code with `hello.c` and `system.h`
- `man` contains the man page
- Note: there are no `makefile` in this package, we need to create it
- `./configure`
    * Checks for dependencies required for build and install process
    * This script will create a `makefile` for you
- `make`
- `ls src` will show `.o` files created by `make`
- `sudo make install`
    * Binary and man pages are copied
- `which hello`
    * Now exists in `/usr/local/bin`
- `hello`
    * Just prints hello world
- `sudo make uninstall`

## Packaging Your Software using GNU Autotools autoconf & automake

- Packaging software using GNU autotools
    * `configure.ac` is used by `aclocal` to generate `aclocal.m4`
    * `configure.ac` is used by `autoconf` to generate `configure`
    * `Makefile.am` is used by `automake` to generate `Makefile.in`
    * `Makefile.in` is used by `configure` to generate `makefile`
    * `make dist` generates `myexe-1.0.tar.gz` (tarball)
- Example:
    * Same `src` as in previous examples
    * `configure.ac`
    ```
    AC_INIT([myexe],[1.0],[arif@pucit.edu.pk]) # Required
    AM_INIT_AUTOMAKE # Use automake for this project
    AC_PROG_CC([gcc cl cc]) # Compiler dependencies
    AC_CONFIG_FILES([Makefile]) # Convert makefile.in to makefile
    AC_OUTPUT
    ```
    * `aclocal` will generate `aclocal.m4`
    * `autoconf` will generate `configure`
    * `makefile.am`
    ```
    AUTOMAKE_OPTIONS=foreign
    bin_PROGRAMS = myexe
    myexe_SOURCES = src/myadd.c src/mysub.c src/mymul.c src/mydiv.c src/prog1.c src/mymath.h
    ```
    * `automake`
    * `./configure`
    * `makefile` that results is huge
    * `make dist` to create tarball
        + Tarball will contain all of the files in `src` as well as the executable

## Packaging Software with Cmake

- `cmake` is a cross platform `makefile` generator
- Effort to deploy a better way to configure, build and deploy complex softwares written in various languages across many different platforms

## How Does CMake work

- CMake utility reads project description from a file named `CMakeLists.txt` and generates a build system for a Makefile project, VS project, Eclipse project, etc
- Example:
    * Consider following project:
        + `CMakeLists.txt`
        + `include`
            - `mymath.h` (contains the prototypes)
        + `lib`
            - `libarifmath.a` (contains `.o` files created in previous sections - view with `ar` utility)
            - `libarifmath.so`
        + `man`
            - `myadd.3` (contains man page info)
        + `src`
            - `prog1.c` (contains C code)
- We should build out of source so that:
    * Generated files remain separate from source files
    * We can generate multiple source trees from the same source
    * We can delete build directory later and perform a clean build again
- `CMakeLists.txt`
```
cmake_minimum_required (VERSION 3.7)
project(ex1_cmakeproject)
include_directories(${CMAKE_SOURCE_DIR}/include})
link_directories(${CMAKE_SOURCE_DIR}/lib)
set(SOURCES src/prog1.c)
add_executable(myexe ${PROJECT_SOURCE_DIR}/${SOURCES})
target_link_libraries(myexe libc.so libarifmath.a)
install(TARGETS myexe DESTINATION /usr/bin)
install(FILE man/myadd.3 DESTINATION /usr/share/man/man3)
include(InstallREquiredSystemLibraries)
set(CPACK_GNERATOR "DEB")
set(CPACK_DEBIAN_PACKAGE_MAINTAINER "Arif Butt)
include (CPACK)
```
- `cmake`
    * Produces `makefile` along with other cmake-related files
    * `make` to generate `myexe`
    * `make install` to install `myexe`
- `cpack --config CPackSourceConfig.cmake` to generate the Redhat package
- `cpack --config CPackConfig.cmake` to generate the Debian package