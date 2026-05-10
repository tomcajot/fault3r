# Fault3r Software

## Installation and use

To generate a .vmem memory image for the core run the following command which will create it based on the provided c code file and a payload.vmem as well as a fault address.

`make PROG=jal_adder OBJ="adder.c" FAULT_ADDR=0×212c INJECT=payload.vmem`

This only works when the riscv toolchain is in the parent directory.
