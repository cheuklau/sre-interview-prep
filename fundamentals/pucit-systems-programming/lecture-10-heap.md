# Lecture 10

## Allocating, using and freeing memory on Heap

- Last lecture we went over the user stack which was at the top of the process address space just below kernel virtual memory
- In this lecture we talk about the heap which starts at the end of the data segment (loaded from the executable file)

## Heap Allocators

- Allocators come in two basic types
    * Both require application to explictly allocate blocks
    * They differ about which entity is responsible for freeing allocated blocks
    * Two types:
        1. Explicit allocators
            + Require app to explicitly free any allocated blocks
            + Example is C standard library which provides an explict allocator called `malloc`
            + C allocates a block by calling the `malloc` function and frees a block by calling `free`
            + In C++ we normally use the `new` and `delete` operators
        2. Implicit allocators
            + Require the allocator to detect when an allocated block is no longer used by the program and then free the block
            + Implicit allocators are also known as garbage collectors and the process of automatically freeing unused allocated blocks is known as garbage collection
            + Example are higher-level languages e.g., Lisp, ML and Java

## Malloc family in C

- `malloc()` allocates size bytes from the heap and returns a pointer to the start of the newly allocated block of memory
    * On failure, returns `NULL` and sets `errno` to indicate error
- `calloc()` allocates space for specific number of objects each of a specific size
    * Returns pointer to the start of the newly allocated block of memory
    * Unlink `malloc()`, `calloc()` initializes the allocated memory to zero
- `realloc()` used to resize block of memory previously allocated by one of the functions in `malloc()` package
    * Ptr arguement is the pointer to the block of memory that is to be resized
    * On success it returns a pointer to the location of the resized block, which may be different from its location before the call
- `free()` deallocates the block of memory pointed to by its pointer argument which should be an address previously returned by functions of `malloc` package

## Example: 1D array on heap

- Start with following address space (bottom to top):
    * Low address
    * Data section
        + `.text` ending at `&etext` pointer
        + `.data` ending at `&edata` pointer
        + `.bss` ending at `&end` pointer
    * `brk` pointing to the start of the heap
    * `rsp` pointing to the top of the stack
- When program executes: `char*str=(char*)malloc(sizeof(char)*10);`
    * Request to allocate space in heap for 10 characters (10 bytes)
    * `str` is created on the stack and it points to the unnamed memory in the heap
    * The `brk` pointer has also moved up due to the increase in heap size
        + Note that `brk` has not moved up only 10 bytes but rather some multiple of page size
- We use this new memory and then eventually we are done and call `free(str)`
    * Note that `brk` is not moved by `free()`
    * The freed blocks are added to the pool of blocks that can be used for future calls to `malloc()`
    * Also note that `str` still exists on the stack (until function that created variable is out of scope)

## Example: 2D array on heap

- Code:
```
int i, int rows = 4, cols = 12;
char ** names = (char**)malloc(sizeof(char*) * rows);
for(i=0; i<rows; i++)
    names[i]=(char*)malloc(sizeof(char)*cols);
...
...
for(i=0; i<rows; i++)
    free(names[i]);
free(names);
```
- In the above example:
    * `names` is a stack variable pointing to unnamed memory on heap containing 1D array of size 4 made up of character pointers
    * When for loop gets executed each of the original 1D array elements (4 total) will point to an additional 1D array of size 12
    * At the end we free each of the 1D array of size 12
    * The original 1D array of size 4 is still on heap until we call free for the last time
    * Note that `names` is still on stack and will be freed automatically as program exits

# Example

- If a process continuously calls `malloc()` without calling `free` what happens?
- Program:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MB 1024*1024
int main(){
    char* ptr = NULL;
    int ctr = 0;
    while(1){
        ptr = (char *) malloc(MB); # Continuously calling malloc for 1M of memory on heap
        memset(ptr, '\0', MB);     # Initializing allocated memory with null byte
        printf("Currently allocating %d MB\n", ++ctr);
    }
    exit(0);
}
```
- It continues until it stops at 3622 MB before the call fails and the process is killed
- If we comment out the `memset` call, we see that we have crossed the previous limit of 3622 MB.
    * Program allocates 623137 MB. Why?
- The second run was just allocating the memory but not using it.
- Linux OS defers page allocation until you actually use the memory by adding data to that block (linux optimistic allocating scheme).

## Heap: Behind the Curtain

## System call: brk()

- Resizing the heap is actually telling the kernel to adjust the process's program break which lies initially just above the end of the uninitizlied data segment (i.e., `end` variable)
- `brk()` is a system call that sets the program break to location specified by `end_data_segment`
    * Since virtual memory is allocated in pages, this request is rounded up to the page boundary
    * Any attempt to lower the prgram break than `end` results in segmentation fault
- The upper limit to which the program break can be set depends on a range of factors like:
    * Process resource limit for size of data segment
    * Location of memory mappings, shared memory segment and shared libraries

## Library call: sbrk()

- `sbrk()` is a C library wrapper implemented on top of `brk()`
    * It increments the program break by increment bytes
- On success `sbrk()` returns a pointer to the end of the heap before `sbrk()` was called i.e., pointer to the start of new area
- So calling `sbrk(0)` returns the current setting of the program without changing it
- On failure, `-1` is returned with `errno ENOMEM`

# Example

- After a process calls `malloc()`, which in turn calls `brk()`, what is the new location of program break `brk`?
- Program:
```
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(int argc, char** argv){
    printf("Before any allocation brk is at: %p\n", sbrk(0));
    char* a = (char*) malloc(100);
    printf("After first allocation brk is at %p\n", sbrk(0));
    char* a = (char*) malloc(100);
    printf("After second allocation brk is at %p\n", sbrk(0));
    char* a = (char*) malloc(100);
    printf("After third allocation brk is at %p\n", sbrk(0));
    char* a = (char*) malloc(100);
    printf("After fourth allocation brk is at %p\n", sbrk(0));
}
```
- `gcc brk.c`
- `./a.out`
- When we run program, we see that original address is `0x55555575600` then after first call it becomes `0x555555777000` but remains the same
- After first call, `brk` moves over 100KB then remains the same for subsequent calls
- As we previously mentioned, `brk` jumps up with some multiple of the page size (not just what we called with `malloc`)

## Basic Heap Allocator

- At the start of the process, `brk` and `end` points to the same location
- First call to `malloc` program break `brk` moves ahead some multiple of page size ahead
    * Provides contiguous memory area to play with
    * Within this area, program continuously allocates and frees chunks of memory
    * After some time we have some allocated and some free blocks within this area
- Structure of allocated block on heap:
    * Length of allocated block (`L`)
    * Memory for use
    * Address returned is where the memory for `L` ends
- Structure of free block on heap (implemented as doubly-linked list):
    * Length of free block (L)
    * Pointer to previous free block
    * Pointer to next free block
    * Remaining bytes of the free block
- When program calls `malloc` the allocator:
    1. Scans the linked list of free memory blocks using one of the contiguous memory allocation algorithms (first fit, best fit, next fit)
    2. Assigns the block
    3. Update the data structures
- If no block on the free list is large enough then `malloc()` calls `sbrk()` to allocate more memory
- To reduce the number of calls to `sbrk()`, `malloc()` does not allocate exact number of bytes required but rather increase the prgram break in large units (some multiple of virtual memory page size) and putting the excess memory onto the free list
- When proces calls `free()` how does it know as to how much memory it needs to free?
    * When you call `free()`, it returns the address of the end of `L` so the 8 bytes previous to that address (`L`) contains the size of the allocated block
    * This is how `free` knows how much memory it needs to free and makes the allocated block a free block later on
- Does calling `free()` have any effect on program `brk`?
    * No, it just puts an allocated block into the list of free blocks
- Coalescing freed memory
    * When you call `free()`, you put a chunk of memory back on the free list
    * There may be times when the chunk immediately before it in memory and/or chunk immediately after it in memory are also free
    * If so, it makes sense to merge the free chunks into one free chunk
    * This is called coalescing free chunks

## Why Not Use brk() or sbrk()

- C program uses `malloc` faimily of functions to allocate and deallocate memory on heap instead of `brk()` and `sbrk()` because:
    1. `malloc` functions are standardized as part of C
    2. `malloc` functions are easier to use in threaded programs
    3. `malloc` functions provide a simpler interface that allows memory to be allocated in small units
    4. `malloc` functions allow us to deallocate blocks of memory
- Why `free()` does not lower the program break?
    * Rather adds the block of memory to a list of free blocks to be used by future calls to `malloc()`
    * This is done for following reasons:
        + Block of memory freed is somewhere in the middle of the heap rather than at the end so lowering program break is not possible
        * Minimizes the numbers of `sbrk()` calls that program must perform
- Example:
```
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char** argv){
    int size = atoi(argv[1]);
    char* a = (char*) malloc(size);
    char* b = (char*) malloc(size);
    char* c = (char*) malloc(size);
    char* d = (char*) malloc(size);
    printf("a = %p\nb = %p\nc = %p\nd = %p\n", a, b, c, d);
}
```
- When we compile and run we see that:
```
a = 0x555555756010
b = 0x555555756030
c = 0x555555756050
d = 0x555555756070
```
- The above are differences of about 32 bytes even though we only requested one via `./a.out 1`
- So when a process requests 1-24B on heap, the memory allocated is 32B?
- Or when a process requests 25-40B on heap, the memory allocated is 48B? etc

## Points to Ponder for Heaps

- Common programming errors while using heap
    1. Reading/writing freed memory areas
    2. Reading/writing memory addresses before/after the allocated memory using faulty pointer arithmetic
    3. Freeing same piece of allocated memory more than once
    4. Freeing heap memory by a pointer that wasn't obtained by a call to `malloc`
    5. Memory leaks i.e., not freeing memory and keep just allocating it
- `malloc` debugging libraries
    * To use these libraries we need to link our program against a particular library instead of `malloc` package in the standard C library
    * These libraries operate at slower run-time, increased memory consumption or both
    * Should only use them for debugging purposes and then return to linking with the standard `malloc` package for production versions of app
    * Example libraries:
        1. Electric Fence
        2. Valgrind
- Assume we have a program `hellobug.c` which tries to access an address space that has already been freed
- `sudo apt-get install electric-fence`
- `gcc -ggdb hellobug.c -lefence`
    * We added `ggdb` to also add the debugging symbols
    * And linked to the `libefence` library
- When we run `./a.out` we get segmentation fault (before it ran sucessfully) with the following output files:
    * View the `core` file which contains the core dump (memory image of the process at the time of its abnormal termination)
    * `gdb a.out core`
        + We get the exact line of the segmentation fault where we tried to assign `arr[0]='b';` after `arr` has been freed
- `valgrind` is a suite of command line tools for debugging and profiling
    * `memcheck` is the default which is a memory error detector
    * `cachegrind` is a cache and branch-prediction profiler; help you make your program run faster
    * `callgrind` is a call graph generating cache profiler
    * `helgrind` is a thread error detector
    * `drd` is also a thread error detector
- When using `valgrind` recommended to compile with options like no optimization `-O0` and include debugging info `-g`
    * `gcc -Wall -std=c99 -O0 -g prog1.c`
- `valgrind ./a.out`
- Example:
    * We have program that used `=` instead of `==` for an if-comparison.
    * Compiling and running will pass since if statement will always evaluate to true
    * If we run `gcc -Wall faultyprogram.c` to compile we will get a warning about it
    * Next function tries to access `ptr[13]` after only `malloc` 10 characters
    * Compiling and running will pass since we are still accessing a valid memory location
    * `valgrind ./a.out` will show 1 error from 1 context and show the function that error occurred in
    * Next function tries to write `ptr[5]='a'` after freeing it
    * Compiling and running will issue a seg fault (does not give line number that caused the problem)
    * `gdb core` or `valgrind ./a.out` to check out what the problem is
    * Next function tries to free the same memory twice
    * Compiling and running will give a core dump which we can inspect via `gdb core` or analyze with `valgrind ./.a.out` which will show `1 alloc and 2 frees`
    * Next function does not free the memory at all
    * Compiling and running will work fine
    * `valgrind ./a.out` will show `LEAK SUMMARY` which will say we lost `10 bytes in 1 block`
    * Next function tries to call another function which creates an array on stack and returning that to the original function
        + In general we dont want to access stacks across functions
        + Correct approach is to allocate memory on heap in second function, which is available across function calls
