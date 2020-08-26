# Lecture 21

## SSDs vs HDDs

- Some important technology
    * Stable storage: storage that does not lose its contents when the computer is turned off
- Today we have two main categories of stable storage with very different characteristics
    1. HDD, spinning disk or harddrive: stable storage device constructed of rotating magnetic platters
    2. SSD or flash drive: stable storage constructed of non-moving non-volatile memory
- HDDs are bigger, slower and cheaper than SSDs
- HDDs and SSDs lead to very different system designs

## Why Study Spinning Disks?

- Flash is the future but HDDs still around
- Hierarchical file systems are dead, long live search
- Local search is still built on top of hierarchical file systems today
- New storage technologies will completely alter the way that OS store data but new solutions will benefit from and probably resemble earlier efforts

## Disk Parts

- Platter:
    * Circular flat disk on which magnetic data is stored
    * Constructed of a rigid non-magnetic material coated with a very thin layer of magnetic material
    * Can have data written on both sides
- Spindle
    * Drive shaft on which multiple platters are mounted and spun between 4200 and 15000 RPM
- Head
    * Actuator that reads and writes data onto the magnetic surface of the platters while rotating at tens of nanometers over the platter surface

## Disk Locations

- Track
    * Think of a lane on a race track running around the platter
- Sector
    * Resembles a slice of pie cut out of a single platter
- Cylinder
    * Imagine the intersection between a cylinder and the set of platters
    * Composed of a set of vertically-aligned tracks on all platters

## Spinning Disks are Different

- Spinning disks are fundamentally different from other system components we have discussed so far
- Difference in kind: disks move
- Difference in degree: disks are slow
- Difference in integration: disks are devices, and less tightly coupled to the abstraction built on top of them

## Disks Move, Ergo Disks are Slow

- Electronics time scale: time for electron to flow from one part of the computer or chip to another (fast)
- Mechanics time scale: time necessary for a physical object to move from one point to another (comparatively slow)

## Disks Move, Ergo Disks Fail

- Disks can fail by parts
    * Many disks ship with sectors already broken; OS detect and ignore these sectors
    * Sectors may fail over time, potentially resulting in data loss
- Disks can fail catastrophically
    * Head crash occurs when a jolt sends the disk heads crashing into the magnetic surface, scarping off material and destroying the platter
    * When this happens, you have about 20 seconds to say goodbye

## Head Crash

- We will discuss RAID, a clever way to use multiple disks to create a more reliable and better-performing device that looks like a single disk
- Many interesting approaches to fault tolerance began with people thinking about spinning disks

## Disks are Slow

- Disks frequently bottleneck other parts of the OS
- OS play some of our usual games with disks to try and hide disk latency
    * Use past to predict the future
    * Use a cache
    * Procrastination
- Contrast with memory latencies which are hidden transparetnly by the processor