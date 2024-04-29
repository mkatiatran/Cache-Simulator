# Cache Simulator README

## Overview

This is a cache simulator meant to demonstrate how cache and 
memory accesses affect the static and dynamic energy 
of a computer system. In our case a simple computer system with an L1 instruction cache, L1 data cache, L2 unified cache 
and DRAM. It utilizes a combination of Python scripts and a Bash script to run simulations and analyze the results redirected to a text file called formatted_output.txt. 

## Features

- Simulates cache memory behavior based on associativity 
- Provides statistics such as cache hits, misses, energy consumption, mean, and standard deviation.
- Supports many customizable cache configurations but intended for varying associativity. 

## Prerequisites

- Python 3.x
- Bash shell
- mean_and_std.py: Python script for calculating mean and standard deviation
- with_penalties.py: Python script to run memory traces on a simulated memory system

## Usage

### Running the Cache Simulator

1. Set up the input trace files in the desired format. Each line in the trace file represents a memory access. 
   Trace files, script.sh, mean_and_std.py and with_penalties.py must all be in the same directory. 

2. Configure the cache parameters in the `script.sh` script.

3. Execute the cache simulator by running the `script.sh` script, note that the 
script.sh script may have numbers added after it, like script-2.sh, so you need 
to change script.sh to the correct name:

   chmod +x script.sh
   ./script.sh

### Running a Single Trace File 
In script.sh replace the file in FILE_NAMES_TEST=("047.tomcatv.din") with any of the dinero file names. The output to formatted.txt will be a summary of cache hits and misses averaged over 10 iterations of that file for associativity of 2, 4 and 8. 

### Customize Associativity 
Replace the values in ASSOCS=(2 4 8) with a value or values 
of your choice. 
