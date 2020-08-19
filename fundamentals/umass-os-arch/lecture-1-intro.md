# Lecture 1: Introduction

## What is an Operating System

- Interface between user and architecture
- Implements a VM that is easier to program than raw hardware
- Divides resources between processes
- Key features:
  1. Services: standard services which hardware implements e.g., file system, virtual memory, networking, CPU scheduling, time-sharing
  2. Coordination: multiple apps and users to achieve fairness and efficiency (throughput) e.g., concurrency, memory protection, networking, security
  3. Goal: machine is convenient to use and efficient
- History of computers:
  1. Single-user computers
    * One user at a time
    * Computer executes one function at a time
  2. Batch processing
    * Execute multiple jobs in batch
    * Users submit jobs
    * Human schedule jobs
    * OS loads and runs jobs
    * More efficient use of machine
  3. Overlap I/O and computation
    * Allow CPU to execute while waiting for I/O
    * Add buffering: data fills buffer and then output
    * Add interrupt handling: I/O events trigger a signal (interrupt)
    * More efficient use of machine
  4. Multiprogramming
    * Several programs run simultaneously
    * Run one job until I/O
    * Run another job
    * OS manages interactions: which jobs to run, protect program's memory from others, decides which to resume when CPU available
  5. The renaissance (1970s)
    * Users share system via terminals
    * UNIX era
      + Shell composable commands
      + No distnction between programs and data
  6. Industrial revolution (1980s)
    * Widespread use of PCs
    * Simple OS (DOS, MacOS)
      + No multiprogramming, concurrency, memory protection, virtual memory, etc
      + Later: networking, file-sharing, remote printing
      + GUI added to OS
  7. Modern era (1990s to present)
    * Real operating systems on PCs
    * Different modalities
      + Real-time
      + Sensor/embedded
      + Parallel: multiple processors on a single machine
      + Distributed: multiple networked processors
  8. Architectural trends
    * Almost every computer component now 9 orders of magnitude faster, larger and cheaper
    * Moore's law: number of transistors doubles every two years
      + Starting to be a problem due to energy and heat