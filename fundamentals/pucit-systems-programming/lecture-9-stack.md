# Lecture 9

## Process Address Space

- 32-bit logical address space consists of (from top to bottom):
    * Kernel virtual memory (invisible to user code)
        + Goes from `0xc0000000` to `0xffffffff`
        + This is almost 1/4th of the process address space
    * User stack (created at run time)
        + Bottom of user stack set by `%esp` (stack pointer)
    * Empty
    * Memory-mapped regions for shared libraries
    * Empty
    * Run-time heap (created by `malloc`)
        + Goes from `&end` to `brk`
        + Note: When program starts, heap is empty so `&end` and `brk` points to the same address
    * Loaded from executable file:
        + Read/write segment (`.data`, `.bss`)
            - `.bss` for uninitialized data which goes from `&edata` to `&end` pointers
            - `.data` for initialize data which goes from `&etext` to `&edata` pointers
        + Read-only segment (`.init`, `.text`, `.rodata`) - this is the code
    * Unused
        + Starts from `0x00000000` to `0x0804800`
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
extern int extext, edata, end;
int I = 54 // Initialized global variable
int J; // Uninitialized global variable
int main(int argc, char *argv[]){
    int i = 10; // stack variable
    int *ii = NULL; // stack variable
    printf("Page size: %d\n\n", getpagesize());
    printf("main = %p\n", main);
    printf("&etext = %p\n\n", &etext);
    printf("&I(initialized var) = %p\n", &I);
    printf("&edata = %p\n", &edata);
    printf("&J(uninitialized var) = %p\n", &J);
    printf("&end = %p\n\n", &end);
    ii = (int *) malloc(sizeof(int));
    print("ii (addr of heap) = %p\n\n", ii)
    printf("&argc = %p\n", &argc);
    printf("&i = %p\n", &i);
    printf("&ii = %p\n", &ii);
    return 0
}
```
- Running above program will show address of:
    * main (below the etext)
    * initialized, uninitialized variables
    * heap
    * arguments on the stack
- Translated to physical addresses using page translation scheme
- If we run program multiple times, we see that the addresses on the stack differ each time
    * Most modern OS performs address space randomization for the stack for security reasons
    * We can turn it off by `echo 0 | sudo tee /proc/sys/kernel/randomize_va_space`

## Command Line Arguments and Environment Variables

- Example:
```
int main(int argc, char *argv[]){
    printf("No of arguments passed are: %d\n", argc);
    printf("Parameters are:\n");
    for (int i = 0; argv[i] != NULL; i++)
        printf("argv[%d]:%s \n", i, argv[i]);
    return 0;
}
```
- If we run `cat /etc/passwd`
    * `int argc` is going to be 2
    * `char * argv[]` is a pointer to
        0. `cat\0`
        1. `/etc/passwd\0`
        2. `\0`
- If we run `ls -l /bin`
    * `int argc` is going to be 3
    * `char * argv[]` is a pointer to
        0. `ls\0`
        1. `-l\0`
        2. `/bin\0`
        3. `\0`
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char *argv[]){
    if (strcmp(argv[0], "./hello")==0)
        printf("I am called by the name hello\n");
    else
        printf("I am called by the name bye\n");
    return 0;
}
```
- `gcc cmdarg_ex2.c -o hello`
- `gcc cmdarg_ex2.c -o bye`
- Note that above two executables are identical, just different names
    * If we run `./hello` we get back `I am called by the name hello`
    * If we run `./bye` we get back `I am called by the name bye`
    * This proves that the path to the executable is the first command line argument

## Environment Variables

- `env` to view env variables
- `set | less` to display env variables as well
- `HISTSIZE=250` to change env var `HISTSIZE` (this only changes for current shell)
- To update permanently, change the bash profile

## Accessing Environment Variables

- Example:
```
inte extern char **environ;
int main(){
    printf("\n Environment variable passed are:\n");
    for (int i = 0; environ[i] != NULL; i++)
        printf("environ[%d]:%s\n", i, environ[i]);
    return 0;
}
```
- Above reads environment vars passed to it from the shell and displays them

## Modifying Environment Variables

- The way we can change env vars in the shell, we can also change them within a C program as well as create a new env var
```
char *getenv(coonst char *name)
int putenv(char * string)
int setenv(const char *name, const char *val, int overwrite)
int unsertenv(const char *name)
int clearenv()
```
- Reasons to modify env vars:
    * Build a suitable env for a process to run
    * Form of IPC since a child gets a copy of its parent's env vars at the time it is created
- Example:
```
#include <stdio.h>
#include <stdlib.h>
int main()
{
    char * historysize = getenv("HISTSIZE");
    printf("Original value of HISTSIZE: %s\n", historysize);
    putenv("HISTSIZE=500");
    historysize = getenv("HISTSIZE");
    printf("Changed value of HISTSIZE after getenv: %s\n", historysize);
    setenv("HISTSIZE", "300", 1); // The 1 at the end means to overwrite
    historysize = getenv("HISTSIZE");
    printf("Changed value of HISTSIZE after setenv: %s\n", historysize);
    return 0;
}
```

## Layout of a Process Stack

- How stack grows and shrinks as functions are called and returns
- Stack grows from high to low addresses in Intel architectures
- Upper portion of the process stack from bottom to to the top (note: these are just the command line arguments and environment variables):
    * `0xbfffffff`
    * Null-terminated environment variable strings
    * Null-terminated commandline arg strings
    * Unused
    * `envp[n] == NULL`
    * `envp[n-1]`
    * ...
    * `envp[0]`
    * `argv[argc] = NULL`
    * `argv[argc-1]`
    * ...
    * `argv[0]`
    * Dynamic linker variables
    * `envp` # Pointer to `envp[0] to envp[n]`
    * `argv` # Pointer to `argv[0] to argv[argc]`
    * `argc` # Number of arguments passed to main (null terminated strings passed in as arguments)
    * `0xbffffa7c`
    * Stack frame for main
- After the command line arguments and environment variables spanning `0xbffffff` to `0xbffffa7c`
    * `rbp` frame pointer to where Function Stack Frames (FSF) begins containing `main()`
    * `rsp` pointer to the top of the FSF
- When `main()` begins executing, the process stack contains only one function stack frame (activation record)
- Activation record is used to:
    * Store local variables
    * Pass arguments to the functions
    * Store return address
    * Store base pointer

## Function Calling Convention

- Function calling convention means:
    1. How function arguments are passed?
        * Via Stack
        * Via Registers
        * Mix of the two
    2. Order in which function argments are passed?
    3. Who is responsible for creating FSF?
    4. Who is responsible for unwinding the stack?

## Stack Growing and Shrinking

- Suppose `main()` calls another function `foo()`
- The sequence of steps for creation of FSF of `foo()`:
    * Arguments are pushed on the stack in reverse order
    * Contents of `rip` (return address) is also pushed on the stack
    * Contents of `rbp` containing starting address of `main` stack frame is saveed on stack for later use
    * `rbp` is moved to where `rsp` is pointing to create new stack frame pointer of function `foo()`
    * Space created for local variables by moving `rsp` down or to lower address
- The stack from previous now looks like:
    * FSF of `main()` with `rbp` now pointing to where FSF ends
    * Function arguments
    * Function return address
    * `rbp` (function pointer of main)
    * Local variables
    * `rsp` pointing to top of the stack
- Here is a concrete example:
```
int main(...){
    ...
    return foo(2, 3, 4)
}
void foo(int a, int b, int c){
    int xx = a+2;
    int yy = b+2;
    int zz = c+2;
    int sum = xx + yy + zz;
    return sum;
}
```
- Stack layout:
    * FSF of `main()`
    * `rbp` pointer to where FSF ends
    * `4`
    * `3`
    * `2`
    * `rip`
    * `rbp`
    * `xx`
    * `yy`
    * `zz`
    * `sum`
    * `rsp` pointer to the top of stack
- Finally when `foo()` function executes `return` statement, memory on the stack is automatically and efficiently reclaimed:
    * Saved base pointer is popped and placed in `rbp` which moves starting address of `main` FSF
    * Saved return address is popped and placed in `rip`
    * Stack is shrunk by moving `rsp` further up to where `rbp` is pointing
- In the previous example, we just end up with the following stack layout:
    * `rbp` points to the start of FSF
    * FSF of `main()`
    * `rsp` points to the end of FSF

## Buffer Overflow

- Buffer overflow is a bug which occurs when more data is written to a block of memory than it can handle
- Example:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void display(char* str){
    char buff[10];
    strcpy(buff, str);
    printf("The command line received is: %s \n", buff);
}

int main(int argc, char * argv[]){
    if(argc > 1)
        display(argv[1]);
    else
        printf("No command line received.\n");
    exit(0);
}
```
- `gcc bufferovflow.c`
- `./a.out arif` works fine for printing
- `./a.out "Learning is fun with arif"` results in a segmentation fault
    * We only allocated a `buff` of size 10 but the user is providing more than 17 characters
    * Why is 17 the limit even though we set a size of 10?
    * Lets look at the stack:
        + FSF of `main()`
        + `rbp` pointer pointing to end of FSF
        + `*str` which is the input variable to the `display` function
        + `rip` which is the return address `display` needs to return to
        + `rbp` which is needed to move `rbp` to the end of FSF
        + `buff` which is set to a size of 10
    * If we write too many chars into `buff`, we start overwriting `rbp` and `rip` on the stack
    * If `rip` is overwritten then the `display` function will not know where to return to
    * This causes a segmentation fault
    * Note: `7` is the size of `rbp` which is why we were allowed to write `17` chars

## Non-Local Goto

- C goto statement jumps from one instruction to anotehr
    * Not possible to jump between functions
- This can be performed using a `longjmp`
- Example of shortjump:
```
#include <stdio.h>
int main(){
    printf("Start of loop.\n");
    int ctr=1;
    label1:
    printf("PUCIT\n");
    ctr++;
    if (ctr == 6)
        goto label2;
    goto label1;
    label2:
    printf("Out of loop\n");
    return 0;
}
```
- Example of failing to jump between functions:
```
#include <stdio.h>
void f1();
void f2();
int main(){
    printf("Im in main.\n");
    f1();
    return 0;
}
void f1(){
    label: printf("Im in f1()\n");
    f2();
}
void f2(){
    printf("Im in f2()\n");
    goto label;
}
```
- Above fails because we cannot jump between functions
- Example of working long jump:
```
#include <stdio.h>
#include <setjmp.h>
static jmp_buf envbuf;
void func();
int main(){
    int i;
    printf("This is main()");
    if ((i = setjump(envbuf)) == 0){
        printf("Value of i = %d\n", i);
        func();
        printf("This will not be printed");
    }
    printf("This is main() again");
    printf("Value of i = %d\n", i);
    return 0;
}
void func(){
    printf("This is func()");
    longjmp(envbuf, 52);
}
```
