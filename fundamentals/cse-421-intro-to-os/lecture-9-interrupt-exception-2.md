# Lecture 9

## Masking Interrupts

- Hardware interrupts can be either asynchronous or synchronous
- Asynchronous interrupts can be ignored or masked
    * Note: ISR is the interrupt service routine which are instructions that processor executes when an interrupt fires
    * Processor provides an interrupt mask allowing OS to choose which interrupts will trigger the ISR
    * If interrupt is masked, it will not trigger the ISR
    * If interrupt is still asserted when it is unmasked, it will trigger the ISR at that point
- Some interrupts are synchronous or not maskable
    * These typically indicate very serious conditions which must be handled immediately
    * Example: processor reset

## Why Mask Interrupts

- Choosing to ignore interrupts allows the system to prioritze certain interrupts over others
- In some cases handling certian interrupts generates other interrupts which would prevent the system from handling the origin interrupt
    * Applications could take control of devices by preventing the kernel from communicating with them
- Interrupt handlers allow OS to control access to hardware devices and protect them from direct control by untrusted apps
- Memory that contains interrupt handlers is protected from access by user apps
- One of the first things kernel does on boot is install its interrupt handlers

## Software Interrupts

- Given that OS prevents unprivileged code from directly accessing system resources, how do apps gain access to these protected resourceas?
- CPUs provide a special instruction (`syscall` on the MIPS) that generate a software (or synthetic) interrupt
- Software interrupts provide a mechanism for user code to idicate that it needs help from the kernel
- Rest of interrupt handling path is unchanged. The CPU:
    1. Enters privileged mode
    2. Records state necessary to process interrupt
    3. Jumps to a pre-determined memory location and begins executing instructions

## Making System Calls

- To access the kernel system call interface an application:
    1. Arranges arguments to the system call in an agreed-on place where kernel can find them, typically in registers or on its stack
    2. Loads a number identifying the system call it wants the kernel to perform into a pre-determined register
    3. Executes the `syscall` instruction
- `libc` provides the wrappers and the `syscall` instruction that programmers are familiar with

## Software Exceptions

- Software exception indicates that code running on the CPU has created a situation that the processor needs help to address
- Examples:
    * Divide by zero - probably kills the process
    * Attempt to use a privileged instruction - also probably kills the process
    * Attempt to use a virtual address that the CPU does not know how to translate - common exception handled transparently as part of virtual memory manangement
- Interrupts are voluntary
    * Think of the CPU as saying to the kernel: the `/bin/true` process needs you assistance
- Exceptions are non-voluntary
    * Think of CPU as saying to the kernel: I need some help with this `/bin/false` process. It just trued to divide by zero and I think it needs to be terminated
