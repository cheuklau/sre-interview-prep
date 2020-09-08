# Lecture 30

## Memory mapped files

- Memory-mapped file is mostly a segment of virtual memory that has been assigned a direct byte-for-byte correlation with some portion of a file on disk
- Memory mapped I/O lets us map a file on disk into a buffer in process address space so that when we fetch bytes from buffer, the corresponding bytes of the file are read
    * Similarly when we store data in the buffer the corresponding bytes are automatically written to the file
    * This lets us perform I/O without using `read()` or `write()` system calls
- There are two types of memory mapped files:
    1. Persisted/file mapping
    2. Non-persisted/anonymous mapping

## Location of Memory Mapping in Virtual Memory

- Virtual memory address from top to bottom:
    * `argv, environ`
    * Stack
    * Empty space for stack to grow down
    * Shared memory, memory mappings and share libraries placed here
    * Empty space for heap to grow up
    * Heap
    * Unitialized data (`bss`)
    * Initialized data
    * Text (program code)

## Shared File Mapping

- Multiple processes mapping the same region of a file share the same physical pages of memory
    * Whenever a process tries to write, the modifications to the contents of the mapping are carried through to the file
- Main uses of shared file mapping is:
    * Memory-mapped I/O
    * IPC in a manner similar to System-V shared memory segments between related or unrelated processes

## Private File Mapping

- Modifications are not visible to other processes
    * Multiple processes mapping the same file initially share the same physical pages of memory
    * Whenever a process tries to write, copy-on-write technique is employed so that changes to the mapping by one process are invisible to other processes
- The main use of private file mapping is initalizing a process's text and initialized data segments from the corresponding parts of a binary executable file or a shared library file

## mmap() system call

- `mmap()` system call is used to request the creation of memory mappings in the address space of the calling process
    * On success, it returns the starting address of the mapping
- First argument `addr` argument indicates the virtual address at which mapping is to be located
    * Preferably, we should give NULL so that kernel chooses a suitable address for the mapping that doesn't conflict with any existing mapping
- Second argument `len` specifies the size of the mapping in bytes
    * To map an entire file, we put `len` as size of the file
    * Normally kernel creates mappings rounded up to the next multiple of the page size
- Third argument `pro` is a bit mask specifying the permissions (`PROT_READ`, `PROT_WRITE`, `PROT_EXEC`)
- Fourth argument `flags` can be `MAP_PRIVATE` or `MAP_SHARED`
- Fifth argument `fd` is file descriptor identifying file to be mapped
- Sixth argument `offset` specifies starting point of the mapped file
    * To map entire file specify `offset` as 0 and `len` as size of the file
- Last two arguments are ignored for non-persisted or anonymous mapping
    * We normally put `-1` for `fd` and a zero for `offset` for anonymous mapping

## msync() system call

- `int msync(void *addr, size_t len, int flag)`
- `msync()` function causes changes in part or all of the memory segment to be written back to (or read from) the mapped file
- The first argument `addr` is the address that is returned by the `mmap()` call
- The second argument `len` specifies the length of mapping
- Third argument `flags` controls how the update should be performed:
    1. `MS_ASYNC` request update and returns immediately
    2. `MS_SYNC` request update and waits for it to complete
    3. `MS_INVALIDATE` invalidate other mappings of same file

## munmap() system call

- Unmaps the memory mapped region pointed to by `add` with length `len`
- Normally we unmap an entire mapping
    * Specify `addr` as the address returned by `mmap()` called previously
    * Specify same length value as was used to call `mmap()` called previously

## Example

- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <string.h>

int main(int argc, char* argv[]){
//open a file
   int fd = open("f1.txt", O_RDONLY);
//get size of the file
   int fsize = lseek(fd, 0, SEEK_END);
//memory map the file
   char* filedata = mmap(NULL, fsize, PROT_READ, MAP_PRIVATE, fd, 0);
   printf("Data in the file is:\n%s", filedata);
//Need to free the mapped memory
   munmap(filedata, fsize);
//munmap does not close the file discriptor, so we need to do that
   close(fd);
   return 0;
}
```
- Example to show mmap files are inherited by child:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <string.h>

int main(int argc, char* argv[]){
//open a file
   int fd = open("f1.txt", O_RDONLY);
//get attributes of the file
   struct stat sbuff;
   fstat(fd, &sbuff);
   int fsize = sbuff.st_size;
//memory map the file
   char* filedata = mmap(NULL, fsize, PROT_READ, MAP_SHARED, fd, 0);
//create a child process
   pid_t cpid = fork();
   if(cpid==0){
      printf("Child access memory mapped file:\n%s", filedata);
      munmap(filedata, fsize);
      close(fd);
      exit(0);
   }
   else{
      waitpid(cpid, NULL,0);
      printf("Parent access memory mapped file:\n%s", filedata);
      munmap(filedata, fsize);
      close(fd);
      exit(0);
   }
   return 0;
}
```
- Example:
```
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <string.h>

int main(int argc, char* argv[]){
   int fd = open("f1.txt", O_RDWR);
// Stretch the file size to the new size
   lseek(fd, 100, SEEK_END);
    write(fd, "", 1);

//get attributes of the file
   struct stat sbuff;
   fstat(fd, &sbuff);
   int fsize = sbuff.st_size;

//memory map the file
   char* filedata = mmap(NULL, fsize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
   printf("Data of f1.txt that is mapped in memory is:\n%s", filedata);

//now write something in the file (remember the cfo is at the end)
   char *newdata = "This is GR8\n";
   strcat(filedata, newdata);
   printf("New data in the memory mapped region is:\n%s", filedata);
//sync it
   msync(filedata, fsize, MS_SYNC);
   munmap(filedata, fsize);
   close(fd);
   return 0;
}
```