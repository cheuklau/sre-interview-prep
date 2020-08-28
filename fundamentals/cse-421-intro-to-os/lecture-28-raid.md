# Lecture 28

## Redundant Arrays of Inexpensive Disks

- Big idea: several cheap things can be better than one expensive thing

## RAID: Problems

- What is the problem that the RAID paper identifies
    * Computer CPUs are getting faster
    * Computer memory is getting faster
    * Hard drives are not keeping up
- What is the problem with the RAID solution?
    8 Many cheap things fail much more frequently than one expensive thing
    * So need to plan to handle failures

## RAID 1 (Common)

- RAID 1 (mirroring)
    * Two duplicate disks
    * Writes must go to both disks, reads can come from either
    * Performance: better for reads
    * Capacity: unchanged

## RAID 2 (Uncommon)

- RAID 2
    * Byte-level striping: single error disk
    * Hamming codes to detect failures and correct errors
    * Most reads and writes require all disks
    * Capacity: improved

## RAID 3 (Uncommon)

- RAID 3
    * Only correct errors since disks can detect when they fail
    * Byte-level striping, single parity disk
    * Most reads and writes require all disks
    * Capacity: improved

## RAID 4 (Uncommon)

- RAID 4
    * Block-level striping, single parity disk
    * Better distribution of reads between disks due to larger stripe size
    * But all writes all must access the parity disk
    * Performance: improved for reads

## RAID 5 (Full Victory)

- RAID 5
    * Block-level striping
    * Multiple parity disks
    * Better distribution of writes between disks
    * Performance: improved for writes

## RAID 0 (Non-RAID)

- RAID 0
    * Each disk stores half of the data
    * No error correction or redundancy
    * Performance: fantastic
    * Capacity: fantastic
    * Redundancy: none

## RAID: Redundancy

- RAID arrays can tolerate the failure of one (or more) disks
- Once one fails, the array is vulnerable to data loss
- An admin must replace the disks and then rebuild the array
