# Lecture 7

## Producer-Consumer

- Recall producer consumer problem from previous lecture
- Skeleton code:
```
int count = 0;
void produce(item) {
  while (count == FULL) {
    // do something
  }
  put(buffer, item);
  count++;
}

item consume() {
  while (count == 0) {
    // do something
  }
  item = get(buffer, item);
  count--;
  return item;
}
```
- Which synchronization primitive is a good fit for above problem?
    * Conditional variables: there is a variable `count` and conditions that require waiting (full, empty)
- Modification using a conditional variable:
```
int count = 0;
struct * cv countCV;
struct * lock countLock;
void produce(item) {
  lock_acquire(countLock);
  while (count == FULL) {
    cv_wait(countCV, countLock);
  }
  put(buffer, item);
  count++;
  lock_release(countLock);
}

item consume() {
  lock_acquire(countLock);
  while (count == 0) {
    cv_wait(countCV, countLock);
  }
  item = get(buffer, item);
  count--;
  lock_release(countLock);
  return item;
}
```
- `cv_wait()` has to be called with lock held and returns with the lock held
- Any time you call `cv_wait()`, you must call `cv_signal()` or `cv_broadcast()`
- Modification with `cv_broadcast()`:
```
int count = 0;
struct * cv countCV;
struct * lock countLock;
void produce(item) {
  lock_acquire(countLock);
  while (count == FULL) {
    cv_wait(countCV, countLock);
  }
  put(buffer, item);
  count++;
  cv_broadcast(countCV, countLock);
  lock_release(countLock);
}

item consume() {
  lock_acquire(countLock);
  while (count == 0) {
    cv_wait(countCV, countLock);
  }
  item = get(buffer, item);
  count--;
  cv_broadcast(countCV, countLock);
  lock_release(countLock);
  return item;
}
```
- This works, but does it work well?
- If buffer is neither full nor empty, no one should be in `cv_wait()`
- Only broadcast when the state of the buffer has changed (empty to non-empty and full to non-full):
```
int count = 0;
struct * cv countCV;
struct * lock countLock;
void produce(item) {
  lock_acquire(countLock);
  while (count == FULL) {
    cv_wait(countCV, countLock);
  }
  put(buffer, item);
  count++;
  if (count == 1) {
    cv_broadcast(countCV, countLock);
  }
  lock_release(countLock);
}

item consume() {
  lock_acquire(countLock);
  while (count == 0) {
    cv_wait(countCV, countLock);
  }
  item = get(buffer, item);
  count--;
  if (count == FULL - 1) {
    cv_broadcast(countCV, countLock);
  }
  lock_release(countLock);
  return item;
}
```
- Using `cv_broadcast()` wakes up every other waiting thread
- What if we use `cv_signal()`
    * Using `cv_signal()` would require us to know which thread to wake up
    * Waking up all the threads lets scheduler make the decision of which thread to wake up

## Using the Right Tool

- Usually one primitive that is more appropriate than others
- When approaching synchronization problems:
    1. Identify the constraints
    2. Identify shared state
    3. Choose a primitive
    4. Pair waking and sleeping
    5. Look out for multiple resource allocations: can lead to deadlocks
    6. Walk thorugh simple examples and corner cases before beginning ot code

## Review fork()

- `fork()` returns twice
```
returnCode = fork();
if (returnCode == 0) {
  # I am the child.
} else {
  # I am the parent.
}
```
- Child thread returns executing at same point its parent called `fork()`
    * One ception: `fork()` returns twice, PID to parent and 0 to child
- All contents of memory in parent and child are identical
- Both child and parent have same files open at same position
    * Since they are sharing file handles, changes to file offset made by parent or child will be reflected in the other
- Copying all state is expensive especially when next thing a process frequently does is start to load a new binary that desroys most of the state `fork()` copied
- Several solutions:
    1. Optimize existing semantics through copy-on-write which is a clever memory-management optimization
    2. Change semantics e.g., `vfork()` which will fail if child does anything other than immediately load a new executable (does not copy address space)

## Review The Tree of Life

- `fork()` established a parent-child relationship between two processes
- `pstree` utility allows you to visualize above relationships

## Process Lifecycle

- Change: `exec()`
- Death: `exit()`
- Afterlife: `wait()`

## Change exec()

- `exec()` family of system calls replaces the calling process with a new process loaded from a file
- Executable file must contain a complete blueprint indicating how the address space should look after `exec()` completes
    * What should the contents of memory be?
    * Where should the first thread start executing?
- Linux use ELF (executable and linkable format) as the standard describing the information in the executable file is structured

## readelf

- `readelf -l /bin/true`
```
Elf file type is EXEC (executable file)
Entry point 0x8048x90
THere are 8 program headers. Starting at offset 52

Program headers
Type    Offset    VirtAddr   PhysAddr  FileSiz MemSiz   Flg  Align
PWDR    0x000034  0x80808034 0x0xx4034 0x00100 0x00100  R E  0x4
INTERP
 [ Requesting program interpreter /lib/ld-linux.so.2 ]
LOAD
LOAD
DYNAMIC
NOTE
GNU_STACK
...
```

## exec() Argument Passing

- The process calling `exec()` passes arguments to the process that will replace it through the kernel
    * Kernel retrieves arguments from the process after the call to `exec()`
    * Pushes them into memory of th eprocess where the replacement process can find them when it starts executing
    * This is where main gets `argc` and `argv`
- `exec()` also has an interesting return, almost the dual of `fork()`: `exec()` never returns
- By convention, exec does not modify the file table of the calling process. Why not?
    * Remember pipes?
        + Don't undo all the hard work that `fork()` put into duplicating the file table

## Our Simple Shell

- Simple shell:
```
while (1) {
  input = readLine();
  returnCode = fork();
  # If I am the child
  if (returnCode == 0) {
    exec(input);
  }
}
```

## exec() challenges

- Most challenging part of `exec()` is making sure that on failure `exec()` can return to the calling process
    * Can't make destructive changes to the parent's address space until we are sure things will succeed
    * Process is just an abstraction and provides a lot of flexibility: can prepare a separate address space and swap it in when we are done

## exit()

- Processes choose the moment of their own end by calling `exit()`
- Process passes an exit code to the `exit()` function
- What happens to this exit code?

## wait()

- When a process `exit()` the kernel holds the exit code which can be retrieved by the exiting child's parent
- The parent retrieves this exit code by calling `wait()`, the last of the primary process-related system calls