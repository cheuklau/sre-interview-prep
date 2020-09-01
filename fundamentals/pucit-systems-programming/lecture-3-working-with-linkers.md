# Lecture 3

## Why Learn the Linking Process

- Understanding linkers help you build large programs
- Understanding linkers help you avoid dangerous programming errors
    * What happens when you create global variables with same name in multiple object files
- Understanding linking help understand how language scoping rules are implemented
    * What heppens when you declare a variable or function without static attribute
- Understanding linking help you understand other system concepts like loading and running programs, virtual memory, paging and memory mappings
- Understanding linking will enable you to exploit shared libraries
- Advantages of linkers
    1. Modularity: programs can be written as a collection of smaller source files
        * Build libraries of common function like the standard C library `/usr/lib/x86/libc.a`
    2. Efficiency: saves times e.g., if we have 10 source files and only made changes to one, we only need to compile the changed file and then relink the object files
- What do linkers do:
    1. Relocation: merge code and data sections of multiple object files into the code and data sections of the final executable
    2. Symbol resolution: linker associates each symbol reference with exactly one symbol definition
- Example:
1. Source files (`main.c` and `swap.c`)
2. Preocessed code files (`main.i` and `swap.i`)
3. Assembly code files (`main.s` and `swap.s`)
4. Object code files (`main.o` and `swap.o`)
5. `gcc main.o swap.o -o myexe` for linking
- If using a static library (`.a`) which is linked in step 5 above
    * Can run on machines not having that library
    * Downsides:
        + Size of executable of disk will be large
        + In memory, library code is duplicated on every process
        + If static library needs to be updated, all executables need to be relinked
- If using a dynamic library
    * Size of executable on disk will be smaller (just reference)
    * Only one process will have the dynamic library which will be shared by other processes
    * All executables do not need to be relinked in case of newer version
    * Dynamic linking done at:
        1. Load time: loader loads the code in the
        2. Run time: `dlopen` and `dlclose` library calls by user

## Example

- Start with `main.c` and `swap.c`
- `gcc -c *.c` to get `main.o` and `swap.o`

## What Do Linkers Do?

- Relocation:
    * For each `.c` file, compilers and assemblers generate code and data sections in each `.o` file that start at address zero
        + Linker merges separate code and data sections into single sections
        + Then relocates symbols from their relative locations in the `.o` files to their final memory locations in executable
        + Finally, updates all references to these symbols to reflect their new position
    * In the example above we have:
        + `main.o` containing:
            * `main()` as `.text`
            * `int buf[2] = {1, 2}` as data
        + `swap.o` containing:
            * `swap()` as `.text`
            * `int *bufp0=&buf[0]` as `.data`
            * `static int *bufp1` as `.bss`
        + Those two relocatable object files are merged by the linker into the executable object file:
            * `.text` contains:
                + Headers
                + System code
                + `main()`
                + `swap()`
                + More system code
            * `.data` contains:
                + System data
                + `int buf[2]={1,2}`
                + `int *bufp0=&buf[0]`
            * `.bss` contains:
                + `int *bufp1`
- Three types of symbols in the context of linkers:
    1. Global symbols: defined in one module and can be referenced by other modules
    2. External symbols: global symbols that are reference by a module but are defined in some other module
        * Normall declared with `extern` keyword
    3. Local symbols: defined and referenced exclusively by a single module
        * Any global variable or function delcared with `static` keyword is private to that module

## Symbol resolution example

- Consider `main.c`
```
#include <stdio.h>
// Global symbol
void swap();
// Global symbol
int buf[2] = {1,2};
// Global symbol
int main()
{
    // External
    swap();
    printf("buff[0]=%d, buf[1]=%d\n",buf[0],buf[1]);
    return 0;
}
```
- Consider `swap.c`
```
// External
extern int buf[];
// Global
int *bufp0 = & buf[0];
// Local
static int *bufp1;
// Global symbol
void swap()
{
    // Linker knows nothing of temp
    int temp;
    bufp1 = &bufp0;
    temp = *bufp1;
    *bufp0 = *bufp1;
    *bufp1 = temp;
}
```
- `readelf -s main.o` to see symbol table of `main.o`
    * We see linker has merged the symbols from both
- Note: If we ran `gcc --static main.o swap.o -o myexe` no symbol will be undefined because everything is statically linked
- Symbol definitions are stored by compiler in symbol table which is an array of structs
    * linker associates each symbol reference with exactly one symbol definition
    ```
    typedef struct{
        int name;
        int value;
        int size;
        char type:4,
            binding:4;
        char section;
    } Elf_Symbol;
    ```
- What if there are two symbol definitions with the same name
- Linker symbol rules:
    1. Linker resolves symbol references by associating each reference with exactly one symbol definition from symbol tables of its input relocatable object files
    2. Symbol resolution is straightforward for references to local symbols that are defined and reference in a single module
        * Reolsving references to global symbols that are defined in other modules are referenced in some other is trickier
    3. When compiler encounters a symbol that is not defined in the current module, it assumes that it is defined in some other module, generates a linker symbol table entry and leaves it for the linker to handle
        * For example, opposite code file will compile without a hitch however th elinker terminates when it cannot resolve reference to function `foo`
        ```
        void foo();
        int main(){
            foo();
            return 0;
        }
        ```
- Three types of linker symbols (global, external and local) are either strong or weak:
    1. Strong: function names and initialized globals
        * Example (both are strong):
        ```
        int foo=5;
        p1() {

        }
        ```
    2. Weak: uninitialized globals
        * Example (first weak, second weak):
        ```
        int foo;
        p2() {

        }
        ```
- Linker symbol rules continued:
    1. Multiple strong symbols are not allowed
    2. Given a strong symbol and multiple weak symbols, chose the strong symbol
    3. If there are multiple weak symbols, choose arbitrary one

## Example

- `f1.c`
```
int main()
{
    return 0;
}
```
- `f2.c`
```
int main()
{
    return 0;
}
```
- `gcc -c *.c` to compile both
- `gcc f1.o f2.o -o myexe`
    * Fails because there are two conflicting strong symbols (`multiple definition of main`)
- In general always avoid use of global variables or at least initialize them so you get an error when you link two strong variables
    * Otherwise bugs are hard to catch

## Static Libraries

- Concantenate related relocatable object files into a single file with an index called an archive
- Enhance the linker so that it tries to resolve unresolved external references by looking for the symbols in one or more archives
- If an archive member file resolve reference, link it to the executable
- To make the process fast `.a` files cotnains an index for the symbols in all files
- Example:
    * Files `atoi.c`, `printf.c`, ..., `random.c`
    * Running all in translator results in `atoi.o`, `printf.o`, ..., `random.o`
    * Run through archiver to get `libc.a` which si the C standard library
    * `ar -rs libc.a atoi.o printf.o ... random.o`
- Example:
    * `ar -x /usr/lib/x86/libc.a` extracts all `.o` files making up `libc.a`
    * Above extracts 1576 object code files (`.o`) in c library
- Example:
    * We have `mymath.h`, `mysub.c`, `myadd.c`, `mymul.c`, `mydiv.c`
    * `gcc -c *.c` to create `.o` files
    * `ar -rs libarifmath.a myadd.o mysub.o mydiv.o mymul.o`
        + Note that libraries need to start with `lib` and end with `.a`
    * `ar -t libarifmath.a` shows the `.o` files
    * Write driver code (`prog1.c`) to use this library:
    ```
    #include <stdio.h>
    #include <mymath.h>
    int main(){
        double x, y;
        ...
        double ans1 = myadd(x, y)
    }
    ```
    * `gcc -c prog1.c -I /path/to/mymath.h`
    * `gcc prog1.o -o myexe -larifmath -L /path/to/larifmath`
    * `./myexe` to run
- Summary of above example:
    1. We created a static library called `libarifmath.a` which uses the relocatable object files `add.o`, `sub.o`, `div.o` and `mul.o` compiled using `gcc` from c code
    2. We wrote a driver code called `driver.c` that uses `mymath.h` header and used `gcc` to compile it to the relocatable object file `driver.o`
    3. We use a linker to create an executable that links `driver.o` to `libarifmath.a` and the standard c static library `libc.a` (needed for `printf.o`)
    4. We end up with a fully-linked executable object file `driver`

## Linking with Static Library

- Linker's algorithm for resolving external references:
    1. Scan `.o` and `.a` files in the command line order
    2. During scan, keep list of current unresolved references
    3. As each new `.o` or `.a` file obj is encountered, try to resolve each unresolved reference in the list against the symbols defined in obj
    4. If any entries in the unresolved list at end of scan then error

## Limitations of Static Libraries

- Size of executable is large
- Duplication of executables stored on disk
- Duplication in executables running in memory
    * Suppose you are executing 10 c-programs all using `scanf` then ten copies of `scanf` will be in memory
- Minor bug fixes of system libraries require each app to be explicitly relinked

## Modern Solution: Shared Libraries

- Object files that contain code and data that are loaded and linked into an app dynamically either at load or run time
- In UNIX, these are called shared objects (`.so`)

## Dynamic Libraries

- Shared library is similar to static library because it is also a group of object files
    * However shared library is different than static as the linked and loader both behave differently for a dynamic library
- Code that can be loaded and executed at any address without being modified by the linker is known as position-independent code
    * `-fPIC` option to `gcc` specifies that the compiler should generate position independent code
    * This is necessary for shared libraries since there is no way of knowing at link time where the shared library code will be located in memory
- Steps to create a shared library:
    1. Compile each `.c` file with `-fPIC` flag to create object files:
    ```
    gcc -c -fPIC myadd.c mysub.c mydiv.c mymul.c
    ```
    2. Produce a shared object which can be linked with other objects to form an executable
    ```
    gcc -shared myadd.o mysub.o mydiv.o mymul.o -o libarifmath.so
    ```
- Example
    * Same code as before for math library
    * `gcc -c -fPIC *.c` to generate the `.o` files
    * `gcc -shared *.o -o libarifmath.so`
    * `objdump -d -M intel libarifmath.so` to show assmebly code of each function e.g., `myadd`, `mymul`, etc
    * driver program is unchanged as before to use this shared library
    * `gcc -c prog1.c -I /path/to/header` to create `prog1.o`
    * `gcc prog1.o -o myexe -larifmath -L /path/to/larifmath`
    * `file myexe` will show information on the file including the fact that it is dynamically linked
    * `ldd myexe` shows that it depends on `libarifmath.so`
    * `nm myexe` to show symbol table which shows `mydiv`, `mymul`, `myadd`, `mysub` are still undefined as linking will be performed at load time
    * `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path/to/larifmath`
    * `./myexe` will now be able to find the shared library we created