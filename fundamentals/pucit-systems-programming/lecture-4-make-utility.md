# Lecture 4

## Make Utility Introduction

- Imagine you write a program and divide it into a hundred `.c` files and some header files
- To make executable, you need to compile those source files and create hundred relocatable object files that you need to link to the final executable
- What happens if we make a change to one of these files:
    1. Recompile all files and link them
    2. Recompile only file that has changed and link
        * What if it was `.h` file (contains prototype of functions and variables in `.c` files)
        * Then we would need to recompile only those `.c` files that include this header file and link
- `make` is a powerful tool that allows you to manage compilation of multiple modules into an executable
- Reads specification file called `makefile` that describes how modules of a software system depend on each other
- `make` uses this dependency specification and the time when various cocmponents were modified in order to minimize the amount of compilation

## Structure of Makefile

- Format
    * `target : dependency1 dependency 2 ... dependency n`
    * `<tab> command`
        + Where `target` is the name to be built
        + `dependency` are name of files on which the target needs (`.c` and `.h` files)
        + `command` is the shell command to create the target from dependencies
- Above is one dependency rule in a `makefile`
- `makefile` can have several such rules
    * Every rule describes the dependency relationship
- Advantages of `make`
    1. Makes management of large software project with multiple source files easy
    2. No need to recompile a source file that has not been modified, only those files that have been changed are recopmiled; others are just relinked

## Example

- Consider the following `makefile` with `hello.c`
```
# First target
myexe:hello.o
# Command that uses above dependency to create target executable
    gcc hello.o -o myexe
# Second target
hello.o:hello.c
# Command to create relocatable object file
    gcc -c hello.c
```
- Note that when you run above `make` recognizes dependencies and runs second command first to create `hello.o` then runs first command to create the executable
- `hello.c`
```
#include <stdio.h>
int main(){
    printf("Welcome to Learning make utility!\n");
    return 0;
}
```
- Next, we run `make` again and `make` says that `myexe` is up to date. Why?
    * If we look at access, modify, change time, we see that `hello.o` has been modified after `hello.c` was modified
- If we modify `hello.c` now, its modified time is newer than `hello.o` and if we run `make` again then it will recompile `hello.c` and relink via `makefile`

## Options to make

- Several options to make. Most common options:
    * `-f` by default `make` looks for `makefile` in current directory; this option lets you use a different filename
    * `-n` to tell `make` to print out what it would have done without actually doing it
    * `-k` tells `make` to keep going when an error is found; used for debugging multiple source files
- `makefile` can have multiple targets
    * We can call a make file with name of particular target
- To tell `make` to build a particular target, pass the target name as a parameter
- Most programmers specify `all` as first target then list the other targets as being dependencies for all
- Phony target is a target without dependency list e.g., `all`, `clean`, `install`
```
clean:
    -@rm -f *.o
```
- If there is no `.o` file in cwd, `make` will return an error in the above `clean` target
    * If we want to ignore error while executing a command we proceed the command with a hyphen as done above
    * If we want `make` to not print the command to stdout before executing, use `@` character

## Example

- Consider following `makefile`:
```
myexe : mysub.o prog1.o myadd.o mydiv.o mymul.o
    gcc prog1.o myadd.o mysub.o mydiv.o mymul.o -o myexe
myadd.o: myadd.c
    gcc -c myadd.c
mysub.o: mysub.c
    gcc -c mysub.c
mydiv.o: mydiv.c
    gcc -c mydiv.c
mymul.o: mymul.c
    gcc -c mymul.c
prog1.o: prog1.c mymath.h
    gcc -c -I. prog1.c
clean:
    rm -f *.0
install: myexe
    @cp myexe /usr/bin
    @chmod a+x /usr/bin/myexe
    @chmod og-w /usr/bin/myexe
    @echo "myexe successfully installed in /usr/bin"
uninstall:
    @rm -f /usr/bin/myexe
    @echo "myexe successfully un-installed from /usr/bin"
```

## Multiple makefiles in a project

- Project source divided into multiple directories
- Different developers involved
- Multiple makefiles
- Top level makefile use include directive
    * Tells `make` to suspend reading current makefile and read one or more other makefiles before continuing
    * `include ./dir2/makefile ./dir3/makefile`

## Use of Macros in a makefile

- makefile allows us to use macros or variables so that we can write it in a more generalized form
- Variables allow a test string to be defined once and substituted in multiple places later
    * `MACRONAME=value`
    * Accessed with `$(MACRONAME)`
- Example
    * We can use a macro to give options to compiler e.g., while an app is being developed, it will be compiled with no optimization flags but with debugging info included
    * We can declare a macro `CFLAGS = std=c11 -O0 -ggdb -Wall`
        + No optimization with `-O0`
        + Turn on `gdb` debugging
    * Later can use it with all compilation commands like `gcc -c file.c $(CFLAGS)`
- Example:
```
all: myexe
CC=gcc
CFLAGS= -std=c11 -O0 -Wall -g
INCLUDES=.
LIBS = -lc
OBJS= mysub.o prog1.o myadd.o mydiv.o mymul.o ./d1/mymod.o
INSTDIR = /usr/bin

myexe : $(OBJS)
    $(CC) -o myexe $(OBJS) $(LIBS)
myadd.o: myadd.c
    $(CC) -c myadd.c $(CFLAGS)
mysub.o: mysub.c
    $(CC) -c mysub.c $(CFLAGS)
mydiv.o: mydiv.c
    $(CC) -c mydiv.c $(CFLAGS)
mymul.o: mymul.c
    $(CC) -c mymul.c $(CFLAGS)
prog1.o: prog1.c mymath.h
    $(CC) -c -I.$(INCLUDES) $(CFLAGS)

include: ./d1/makefile

clean:
    rm -f $(OBJS)

install: myexe
    @if [ -d $(INSTDIR) ]; \
    then \
        cp myexe $(INSTDIR) && \
        chmod a+x $(INSTDIR)/myexe && \
        chmod og-w $(INSTDIR)/myexe && \
        echo "myexe successfully installed in $(INSTDIR)"; \
    fi

uninstall:
    @rm -f $(INSTDIR)/myexe
    @echo "myexe successfully un-installed from $(INSTDIR)"
```

