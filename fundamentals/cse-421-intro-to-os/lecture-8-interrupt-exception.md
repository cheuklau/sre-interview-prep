# Lecture 8

## wait() and exit()

- Until a process both calls `exit()` and has its exit code collected via `wait()` traces of it remains on the system
    * Its return code is retained by the kernel
    * Its PID is also retained
- Processes that have `exit()` but have not had their exit code collected are called zombies
- What happens if a process's parent exits first
    * Orphaned process is assigned the `init` process as a parent which will collect its exit code when it exits
    * Also known as reparenting
- How do we prevent zombies from taking over the machine?
    * A process's parent receives `SIGCHILD` signal when a child calls `exit()` alerting it to the chance to retrieve child's exit status
    * On some systems a process can choose to have its children automatically repeased by ignoring this signal
    * On bash the relevant command is `disown` which allows children to continue running as daemons even after bash exits
- Parent may want to peek at exit status of its child to check on it
    * Systems support a non-blocking `wait()` for this purpose:
        + Block `wait()` will block until the child exits unless it has already exited in which case it returns immediately
        + Non-blocking `wait()` will not block instead its return status indicates if child has exited and if so what exit code it was

## Simple Shell
```
while (1) {
  input = readLine();
  returnCode = fork();
  if (returnCode == 0) {
    exec(input);
  } else {
    wait(returnCode);
  }
}
```

## Aside: errno

- Potential confusion between kernel system calls and wrappers implemented in `libc`
    * `exit()` system call vs. `exit()` C library function call
    * The C library wraps system calls and changes their return codes

## Multiplexing and Abstracting the CPU

- What are the limitations or problems with hardware resource OS is trying to address?
- What are the mechanisms to allow processor to be shared?
    * Interrupt and context switching
- What are the consequences for programmers of processor multiplexing?
    * Concurrency and synchronization
- How do we deisgn good policies ensuring processor sharing meets needs of user
    * Processor scheduling

## Operating System Privilege

- Implementing most of the process-related system calls we have discussed does not require these special privileges
    * Example: look at user-space threading libraries e.g., `pthreads`
    * They provide functionality similar to `fork()`, `exec()`, `exit()`, `wait()` system calls we discussed

## Multiplexing Requires Privileges

- In order to divide resources between processes, system needs a trusted and privileged entity that can
    * Divide the resources
    * Enforce the division

## OS Does not Trust Processes

- Some processes are malicious and buggy

## Privileged Execution

- CPUs implement a mechanism allowing OS to manage resources: kernel (or privileged) mode
- Being in kernel mode may mean that the executing node
    * Has access to special instructions
    * Has a different view of memory
- When CPU is in kernel mode there are special instructions that can be executed
    * Instructions usually modify important global state controlling how resources are shared
- When CPU not in kernel mode, it does not allow these instructions to be executed

## Protection Boundaries

- Goal:
    * Only trusted kernel code runs in kernel mode
    * Untrusted user code always runs in user mode
- CPU implements mechanisms to transition between user and kernel mode
- Many modern CPUs implement more than two protection modes
    * x86 processors have four protection rings from `0` (most privileged) to `3` (least privileged)
    * For many years OS running on x86 used only `0` and `3`
    * Recently this has become more interesting because of OS virtualization which uses the other rings

## Terminology

- Application refers to code running without privileges or in unprivileged or user mode
- Kernel means code running in privileged or kernel mode
- What makes kernel special: it is ht eone application allowed to execute code in kernel mode

## Bootstrapping Privilege

- Why is the OS allowed to run in the kernel mode
    * You installed the machine that way (what it means to install an OS - choose a particular applciation to grant special privileges to)
    * On booot the CPU starts out executing the kernel code in privileged mode which is how privilege is bootstrapped
    * Kernel is responsible for lowering the privilege level before executing user code

## Traps

- When a normal app does something that causes the system to enter kernel mode we sometimes refer to this as trapping into the kernel
- Frequently think about the thread that trapped into the kernel as running in the kernel after the trap occurs
    * On some level this is accurate
        + Same stream of instructions
    * On some level this is inaccurate
        + Kernel thread has its own stack and has saved the state of the trapping user thread
        + So in a way the user thread has been paused while the kernel performs some task on its behalf

## Privilege Transitions

- Transition into the kernel or into privileged mode typically occurs for one of three reasons:
    1. Hardware interrupt: hardware device requests attention
    2. Software interrupt: software requests attention or system call
    3. Software exception: software needs attention
- What is difference between requesting and needing attention?

## Hardware Interrupts

- Hardware interrupts are used to signal that a particular device needs attention e.g.,
    * Disk read completed
    * Network packet received
    * Timer fired
- Processors implement multiple interrupt lines
    * Input wires on which a logic transition (or level) will trigger an interrupt
- When an interrupt is triggered (interrupt request or IRQ), the processor:
    1. Enters privileged mode
    2. Records state necessary to process the interrupt
    3. Jumps to a pre-determined memory location and begins executing instructions
- Instructions that the processor executes when an interrupt fires are called the interrupt service routine (ISR)


