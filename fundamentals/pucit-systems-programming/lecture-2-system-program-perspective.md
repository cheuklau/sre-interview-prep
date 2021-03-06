# Lecture 2

## Compilation process

1. Start at source code files
2. Preprocessor (cpp)
    * Interpret preprocessor directives
    * Include header files (`/usr/include` includes all the standard header files)
    * Expand macros
    * Removes comments
    * `gcc -E hello.c 1> hello.i`
3. Compiler (cc)
    * Checks for syntax errors
    * Converts src to assembly of underlying processor
    * `gcc -S hello.i`
4. Assembler (as)
    * Generates relocatable object files to be used by linker
    * Contains a symbol table
    * `gcc -c hello.s`
5. Linker (ld)
    * Static vs dynamic linking
        + Static linking includes shared library code in the binary (much bigger)
    * Contains code and data for all functions defined in src file
    * Contains global symbol table
    * `gcc hello.o -o myeye`
6. Executable file
7. Stored in secondary storage as an executable image in a specific format
8. Loader
    * Process address space in main memory

## Examples
- `hello.c`
```
#include <stdio.h>
int main(){
    printf("Welcome to System Programming\n");
    return 0;
}
```

## Types of object Files

- Relocatable object file (`.o`): contains binary code and data in a form that can be combined with other relocatable object files at compile time to create an executable object file
    + Each `.o` file is created from exactly one `.c` file
    + Compilers and assemblers generate relocatable object files
- Executable object files (`a.out`): contains binary code and data in a form that can be copied directly into memory and executable
    + Linkers generates executable object files
    + Note: This is now replaced by Executable and Linking Format (ELF)
        * Organized into a number of sections
- Shared object files (`.so`): special type of relocatable object file that can be loaded into memory and linked dynamically at either load time or run time
    + Called dynamic link libraries (dlls) in Windows
    + Compilers and assemblers generate shared object files
- Core file: disk file containing memory image of the process at time of its termination
    + Generated by system in case of abnormal process termination

## ELF Formation

- Executable and Linking Format (ELF) is a binary format which is used in Linux systems
- Format for storing programs or fragments of programs on disk created by compiling and linking
- ELF simplifies task of making shared libraries and enhances dynamic loading of modules at run time
- Executable file using ELF format has ELF header, program header table and section header table
- Files that are represented in this format are:
    * Relocatable file objects (`.o`)
    * Normal executable files (`a.out`)
    * Shared object files (`.so`)
    * Core files
- `readelf -a hello.o` to show all contents of the file
- `readelf -h hello.o` to show the ELF header
- `readelf -S hello.o` to show each section including:
    * `.text` contains machine code (read and executable)
    * `.data` contains initialized global and static variables
    * `.bss` contains uninitialized variables
    * `symtab` contains symbol table
- Note: `objdump` shows similar information as `readelf`
- Assembly aside:
    * `push` and `mov` create stack frame for main function
    * `pop` and `ret` frees stack frame

## Debugger

- `gcc -ggdb hello.c`
- `gdb -q ./a.out`
```
(gdb) disassemble main
Dump of assemler code for function main:
    0x000063a <+0>: push %rbp
    ...
(gdb) break main
(gdb) info registers
rax  # These are 16 64-bit general purpose registers
rbx
rcx
...
r15
rip # Instruction pointer
cx  # Six segment registers
ss
ds
es
fs
gs
```
- `./dynamicexe` to load to memory and run

## Loading Executable File in Memory

- We have seen the executable object file via `readelf`:
1. ELF header
2. Program header tables
3. `init` section
4. `text` section
5. `rodata` section
6. `data` section
7. `bss` section
8. `.symtab`
9. `.debug`
10. `.line`
11. `.strtab`
12. Section header table
- Process address space:
1. Kernel virtual memory
    * Top of kernel space is `0xfffffff`
2. User stack (created at runtime)
    * Bottom of segment is `esp` stack pointer
    * Top of the stack is at `0xbfffffff`
3. Empty
4. Memory-mapped regions for shared libraries
5. Empty
6. Run-time heap (created by `malloc`)
    * Top of segment is `brk` pointer
7. Read/write segment (`.data`, `.bss`) - loaded from executable file
8. Read-only segment (`.init`, `.text`, `.rodata`) - loaded from executable file
    * Starts at `0x08048000`
10. Unused

## System Calls

- `man syscalls` to show different system calls available on system
- `man 2 write` to view manual for write system call
- Example: `wrapper.c`
```
#include <unistd.h>

int main(){
    char str[]={"Welcome to System Programming\n"};
    int rv = write(1, str, sizeof str);
    return rv;
}
```
- Note: `1` in above refers to stdout (file descriptor of `1` is stdout)
- `echo $?` returns 49 (number of characters in the string)
- We can avoid using library by using `syscall`
- `max syscall` to view manual
- First argument to `syscall` is the number of the system call to perform then the arguments required by that system call
- system call number will be placed in `rax` register
- other arguments will be placed in the `rdi`, `rsi`, `rdx`, `r10`, `r8`, and `r9` (max of 6 arguments)
- `/usr/include/x86/asm/unistd_64.h` contains the syscall number of write `1`
- Above example becomes:
```
#include <unistd.h>

int main(){
    char str[]={"Welcome to System Programming\n"};
    int rv = syscall(1, 1, str, sizeof str);
    return rv;
}
```
- Equivalent in assembly `syscall.nasm`:
```
global main

SECTION .data
msg: db "Welcome to System Programming", 0Ah, 0h
len_msg: equ $ - msg

SECTION .text
main:
  mov rax,1 # Placing write system call number in the rax register
  mov rdi,1 # Placing file descriptor in rdi register
  mov rsi,msg # String is placed in rsi register
  mov rdx,len_msg # Length of the string in rdx register
  syscall ; write(1, msg, len_msg); # Calls trap handler to switch to kernel mode and index syscall table for number in rax and execute the correct interrupt service routine
mov r15, rax # Place return code from rax into r15 register to return it to the main
  mov rax,60 # Place exit system call number in the rax register
  mov rdi,r15 # Place the return code from r15 into rdi register
  syscall ; exit(49) # Call exit system call
```
- `nasm -f elf64 syscall.nasm`
- `ld syscall.o -o myexe` # Need to link to standard library to print
- `./myexe`