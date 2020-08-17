# Kernel Boot Process

## From the Bootloader to the Kernel

- Press power button
- Motherboard sends signal to power supply
- Power supply provides proper electricity to compuuter
- Once motherboard receives power good signal, it tries to start CPU
- CPU resets leftover data in its registers and sets predefined values:
```
IP          0xfff0
CS selector 0xf000
CS base     0xffff0000
```
- Processor starts working in real mode (i.e., real address mode)

### Skipped: memory addressing in real mode

### Skipped: register values after reset

- After initializing and checking hardware, BIOS needs to find the bootable device
- Boot order in BIOS configuration determines which devices the BIOS boots from
- If BIOS boots from a hard drive, BIOS finds the boot sector
    * For hard drives partitioned with MBR partition, the boot sector is first 446 bytes of first sector
    * Note: final two bytes designates to BIOS that device is bootable
- BIOS loads the boot loader from the boot sector and hands control over to it
- Note: BIOS is not in RAM but in ROM

## Bootloader

- Different types of bootloaders that can boot Linux e.g., `GRUB2` and `syslinux`
- Linux kernel has a boot protocol which specifies requirements for a booootloader to implement Linux support
- Now BIOS has chosen a boot device and transferred controol to boot sector code, execution starts from `boot.img` which just points to the location of `GRUB2`'s core image
- Core image begins with `diskboot.img` stored immediately after first sector in unused space before the first partition
- `diskboot.img` loads the rest of the core image containing `GRUB2`'s kernel and drivers for handling filesystems into memory
- After loading rest of core image, it executes `grub_main` function which:
    * Initializes the console
    * Sets root device
    * Loads/parses grub config files
    * Loads modules
- At end of execution, GRUB moves to normal mode
- `grub_normal_execution` function completes the final preparations and shows a menu to select an OS
- `GRUB` executes `boot` command and boots the selected OS
- Bootloader reads and fills some fields of the kernel setup header
- Kernel header starts from:
```
    .globl hdr
hdr:
    setup_sects: .byte 0
    root_flags:  .word ROOT_RDONLY
    syssize:     .long 0
    ram_size:    .word 0
    vid_mode:    .word SVGA_MODE
    root_dev:    .word 0
    boot_flag:   .word 0xAA55
```
- Bootloader must fill in the above with values received from command line or calculated during booting
- Memory mapping after loading the kernel:
```
         | Protected-mode kernel  |
100000   +------------------------+
         | I/O memory hole        |
0A0000   +------------------------+
         | Reserved for BIOS      | Leave as much as possible unused
         ~                        ~
         | Command line           | (Can also be below the X+10000 mark)
X+10000  +------------------------+
         | Stack/heap             | For use by the kernel real-mode code.
X+08000  +------------------------+
         | Kernel setup           | The kernel real-mode code.
         | Kernel boot sector     | The kernel legacy boot sector.
       X +------------------------+
         | Boot loader            | <- Boot sector entry point 0x7C00
001000   +------------------------+
         | Reserved for MBR/BIOS  |
000800   +------------------------+
         | Typically used by MBR  |
000600   +------------------------+
         | BIOS use only          |
000000   +------------------------+
```
- Bootloader has now loaded Linux kernel into memory, filled header fields and jumped to the corresponding memory address

## Kernel Setup

- Kernel setup must configure decompressor and memory management issues
- Afterwards, kernel setup decompress actual kernel and jumps to it
- After the jump to `start_of_setup`, kernel performs the following:
    * Makes sure segment registers are equal
    * Set up stack
    * Set up bss (buffer)
    * Jump to `arch/x86/boot/main.c`

### Skipped: Details on segment registers, stack and bss

### Protected Mode

- Note: Long mode is the modoe where a 64-bit OS can access 64-bit instructions and registers
- Kernel must switch from real into protected mode
    * Real mode has very limited access to RAM (1MB)
    * Protected mode uses 32-bit over 20-bit bus, has access to 4GB RAM and paging support
- Memory management in protected mode is divided into two parts:
    1. Segmentation
    2. Paging
- Recall, addresses in real mode has base address of segment and offset from segment base
- In protected mode, size and location of each segment is stored in the Global Descriptor Table (GDT)
- Algorithm for transition from real into protected mode:
    * Disable interrupts
    * Describe and load GDT
    * Set protection enable bit in CR0 (control register 0)
    * Jump to protected mode code

### Skipped: Copying Boot Parameters into the Zero Page

### Skipped: Console Initialization

### Skipped: Heap Initialization

### CPU Validatin

- `check_cpu` function checks if kernel launches on right CPU level

### Memory Detection

- `detect_memory` provides map of available RAM to the CPU

### Keyboard Initialization

- `keyboard_init`

### Skipped: Querying

### Skipped: Video Mode Initialization

### Kernel Data Types

- char: 1 byte
- short: 2 bytes
- int: 4 bytes
- long: 8 bytes
- u8: 1 byte
- u16: 2 bytes
- u32: 4 bytes
- u64: 8 bytes

### Skip: Heap API

### Skip: Setup Video Mode

### Skip Last Preparatioon Before Transition into Prootected Mode

### Skip: Setup the Interrupt Descriptor Table

### Skip: Setupu the Global Descriptor Table

### Actual transition into protected mode

- `go_to_protected_mode`
- We loaded the IDT, GDT, disabled interrupts and can now switch the CPU into protected mode
- `protected_mode_jump` with twoo parameters: address of protected mode entry point, address of the `boot_params`

## Transition to 64-Bit Mode

### Skipped: 32 Bit Entry Point

### Skipped: Reload the Segments if Needed

### Skipped: Stack Setup and CPU Verification

### Skipped: Calculate Relocation Address

### Skipped: Reload the Segments if Needed

### Skipped: Preparation Before Entering Long Mode

### Skipped: Long Mode

### Skipped: Early Page Table Initialization


