# Interrupts

## Introduction

### What is an Interrupt?

- Event raised by software or hardware when it needs CPU's attention
- Advanced Programmable Interrupt Controller (APIC) consists of:
    * Local APIC - located on each CPU core
        + Handles CPU-specific interrupt configuration
        + Manages interrupts for CPU-specific configurations e.g., thermal sensor, timer, other locally connected I/O devices
    * I/O APIC
        + Provides multi-processor interrupt management
        + Distributes external interrupts among CPU cores
- When interrupt occurs, OS must ensure:
    * Kernel must pause execution of current process (preempt current task)
    * Kernel search handler of interrupt and transfer control (execute interrupt handler)
    * Interrupt handler completes execution, the interrupted process can resume
- Interrupt Descriptor Table (IDT) holds the addresses of each interrupt handler
- Vector number (0-255) denotes the type of interrupt or exception
    * 0-31 are reserved by the proocessor and used for processing architecture-defined exceptions and interrupts
    * 32-255 are designed as user-defined interupts usually assigned to external I/O devices to enable devices to send interrupts to processor
- Two main class of interrupts
    * External/hardware generated interrupts
        + Receives through Local APIC
    * Software-generated interrupts
        + Caused by exceptional condition in the processor itself e.g., division by zero or exiting a program with `syscall`
- Exceptions are synchronous with program execution and can be clasified as:
    * Faults - exception reported before the executioon of a faulty instructin; if corrected, it allows interrupted program to resume
    * Traps - exception reported immediately following the executin of the `trap` instructin
    * Aborts - exception that does not always report the exact instruction which caused the exception; does not allow interrupted program to be resumed
- Maskable interrupts can be blocked
- Non-maskable interrupts are always reported
- If multiple exceptions/interrupts occur at the same time, processor handles them in order of predefined priorities:
    1. Hardware reset and machine checks
    2. Trap on task switch
    3. External hardware interventions
    4. Traps on the previous instruction (breakpoints, debug traps)
    5. Nonmaskable interrupts
    6. Maskable hardware interrupts
    7. Code breakpiont fault
    8. Faults froom fetching next instruction
    9. Faults from decoding the next instruction
    10. Faults on executing an instruction
- IDT stores entry points of interrupts and exception handlers
- IDT entries are gates (interrupt gate, task gate, trap gate)

## Skipped: Start to Dive into Interrupts

## Interrupt Handlers

### Debug and Breakpoint Exceptioons

- `debug` exception occurs when a debug event occurs e.g., attempt to change the contents of a debug register
- These registers allow to set breakpooints on the code and read or write data to trace it
- Debug registers may only be accessed in privileged mode and an attempt to read or write the debug registers when executing at any other privilege level causes a general protection fault exceptioon
- Debug has vector `1`
- `breakpoint` exception occurs when processoor executes int `3` instruction
- Unlike debug exception, breakpoint may occur in user space
- Exception handlers have to parts:
    1. Generic part (same for all exception handlers)
        * Save general purpose registers on the stack, switch to kernel stack if exception came from userspace and transfer cntrol to second part
    2. Does work based on exception type e.g., page fault exception handler should find virtual page for given address, invalid opcode exception handler should send `sigkill` signal, etc
- After we allocoate space for the general purpose registers, we check if the exception came from userspace or not
- If it came from userspace, we move back to interrupted proocess stack

## Skipped: Initialization of Non-Early Interrupt Gates

## Implementation of Some Exception Handlers

- Previously, we discussed settig interrupt gates to IDT.
- Done in the `trap_init` function.
- In this part, we will see implementation of the exception handler for these gates.
- The `idtentry` macro defines exception entry points:
```
idtentry divide_error			        do_divide_error			       has_error_code=0
idtentry overflow			            do_overflow			           has_error_code=0
idtentry invalid_op			            do_invalid_op			       has_error_code=0
idtentry bounds				            do_bounds			           has_error_code=0
idtentry device_not_available		    do_device_not_available		   has_error_code=0
idtentry coprocessor_segment_overrun	do_coprocessor_segment_overrun has_error_code=0
idtentry invalid_TSS			        do_invalid_TSS			       has_error_code=1
idtentry segment_not_present		    do_segment_not_present		   has_error_code=1
idtentry spurious_interrupt_bug		    do_spurious_interrupt_bug	   has_error_code=0
idtentry coprocessor_error		        do_coprocessor_error		   has_error_code=0
idtentry alignment_check		        do_alignment_check		       has_error_code=1
idtentry simd_coprocessor_error		    do_simd_coprocessor_error	   has_error_code=0
```
- `idtentry` macro allocates place for registers on the stack, pushes dummy error code for the stack consistency if an interrupt/exception has no error code, checks the segment selector in the `cs` segment register and switches depending on the previouos state (user or kernel space)
- After all of the above is done, it makes the call to the actual interrupt/exception handler
- After handler finishes its work, `idtentry` macro restores stack and general purpose registers of an uninterrupted task and exectutes `iret` function

### Skipped: Trap Handlers

### Skipped: Double Fault

### Skipped: Device not Available Exception Handler

### Skipped: General Protectioon Fault Exception Handler

## Handling Non-Maskable Interrupts

- Hardware interrupt that cannot be ignored
- Non-maskable interrupt can be generated by:
    * External hardware asserts the non-maskable interrupt pin on the CPU
    * Proocessor receives a message on the system bus or the APIC serial bus with delivery mode NMI

### Skipped: Range Exceeded Exception

### Skipped: Coprocessor Exception and SIMD Exception

## Dive into External Hardware Interrupts

- Interrupts are signals that are sent across the Interrupt Request Line by a hardware or software
- External hardware interrupts allow devices e.g., keyboard, mouse, etc to indicate that it needs attention of the processor
- Once processor receives interrupt request, it will temporary stop execution of the running program and invoke a special routine which depends on the interrupt
- Routine is called interrupt handler which is found in the Interrupt Vector table located at fixed address in memoory
- After interrupt is handled, the proocessoor resumes the interrupted process

## Skipped: Initialization of External Hardware Interrupts Structures

## Softirq, Tasklets, Workqueues

- Three types of deferred interrupts in the Linux kernel:
    1. softirqs
    2. tasklets
    3. workqueue

### Softirqs

- Each processor has its oown thread `ksoftirqd`
- There are 10 types of softirq:
```
~$ cat /proc/softirqs
                    CPU0       CPU1       CPU2       CPU3       CPU4       CPU5       CPU6       CPU7
          HI:          5          0          0          0          0          0          0          0
       TIMER:     332519     310498     289555     272913     282535     279467     282895     270979
      NET_TX:       2320          0          0          2          1          1          0          0
      NET_RX:     270221        225        338        281        311        262        430        265
       BLOCK:     134282         32         40         10         12          7          8          8
BLOCK_IOPOLL:          0          0          0          0          0          0          0          0
     TASKLET:     196835          2          3          0          0          0          0          0
       SCHED:     161852     146745     129539     126064     127998     128014     120243     117391
     HRTIMER:          0          0          0          0          0          0          0          0
         RCU:     337707     289397     251874     239796     254377     254898
```

### Skipped: Tasklets

### Workqueue

- Tasklets are built on softirq concept
- Tasklets are softirq that can be allocated and initialized at runtime and tasklets of the same type cannot be run on multiple processors at a time
- Work queue is similar to tasklets except worqueue functioons run in the context of a kernel process whereas tasklet functioons run in the software interrupt context

## Last Part