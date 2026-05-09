# Fault3r

This projects is a configurable hardware fault-injection extension for the RISC-V Ibex core. It was built in the context of the Honours Program @ TU Delft. The according report can be found in the files above as, report.pdf.

## Installation and use

The "project.zip" is a compressed file containing the full project, the XPR file can be found under its /build/IbexSoc/ and runs on Vivado 2024.2

To run your own software on the core and inject your own instructions follow the following steps:

1. Fork the ibex repo into this project and initialise it as a submodule.
2. Generate a .vmem memory file according the instructions found in sw/README.md.
3. Remove the contents of the build/ folder.
4. run `make PROJ_DIR=build/ RAM_FILE=sw/YOUR_MEMORY_IMAGE.vmem`
5. Launch Vivado and open the .xpr project found in /build/IbexSoC/
6. Open the tesbench and set the following parameters:
   - bit FAULT: master enable. When deasserted, Fault3r is transparent and the core behaves exactly as without the extension.
   - int unsigned FAULT_PC: the instruction address at which the fault is to be triggered.
   - int unsigned FAULT_INSTRUCTION: the 32-bit instruction word that will replace the original at \texttt{FAULT_PC} when the trigger fires.
   - byte FAULT_PC_COUNT: the number of times \texttt{FAULT_PC} must be visited before the fault becomes active.
   - bit FAULT_REPEAT: if asserted, the fault fires on every visit to \texttt{FAULT_PC} from the \texttt{FAULT_PC_COUNT}-th onwards; if deasserted, it fires only on the \texttt{FAULT_PC_COUNT}-th visit and not afterwards.
7. Run the simulation.
