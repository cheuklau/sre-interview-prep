# Lecture 1

## System Programmer Perspective

- Application programing produce software to provide service to th user
- System programming produce software which provides services to computer hardware e.g., disk fragmenter
    * Write kernel code to manage main memory, disk space management, cpu scheduling and management of I/O devices through device drivers
- Executable uses library calls to make system calls which accesses the kernel
- System programmer writes program that may have to acquire data
    * From a file that may have been opened by some other user
    * From other programs running on the same or different machine
    * From OS itself
- After processing programs may have to write results to a shared resource which other processes are also writing or results may need to be delivered to another process asynchrnously i.e., not when process asked for it but at some later unpredictable time
- Important tasks a kernel performs:
    * File management
    * Process management
    * Memory managment
    * Information management
    * Signal handling
    * Synchronization
    * IPC
    * Device management
- Two methods program makes requets for kernel services
    * Making a system call (entry point built directly in kernel)
    * Calling lirbary routine that makes use of this system call
- System call
    * Controlled entry point into kernel code
    * Allows process to request kernel to perform privileged operation
    * System call changes process state from user to kernel mode so CPU can access protected kernel memory
    * Set of system calls is fixed; each system call identified by unique number
    * Each system call may have a set of arguments specifying info to be transfered from user to kernel space and vice versa
- System call invocation: `open()`
    1. User app makes `open()` system call
    2. Processor enters kernel mode
    3. System call table maps to code of `open()` system call
    4. Executes and returns output to user app
- System call invocation: `read()`
    1. Application uses `read()` wrapper function from glibc library
    ```
    read(fd, buffer, count); # Reads data from file associated with file descriptor fd into buffer pointed to by buf for count nbytes
    ```
    - Note: pushes arguments onto stack in reverse order
    2. glibc wrapper function invokes syscall
    ```
    read(...)
    {
        ...
        syscall(SYS_read, fd, buff, count);
        ...
        return;
    }
    ```
    - Arguments to `syscall()` are put on CPU registers
    3. Trap handler takes `syscall()` parameters from CPU registers to kernel process stack
        * It then finds the system call number (specified by `SYS_read` in previous step) to find address of system call service routine
        * Finally it transfers control to the system call service routine
    4. System call service routine
    ```
    SYS_read()
    {
        ...
        ...
        return error
    }
    ```
    - Returns results (error or success code) back to the trap handler
    5. Trap handler switches back from kernel to user mode (wrapper function) returning results
    6. Wrapper function returns back to the application program with the results
