# Fault3r Software

## Installation and use

To generate a .vmem memory image for the core run the following command which will create it based on the provided c code file.

`make PROG=sw OBJ="sw.c"`

This only works when the riscv toolchain is in the parent directory.
