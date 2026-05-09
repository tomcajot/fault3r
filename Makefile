# Synthesis Makefile for Ibex

# tcl script:
GEN_IBEX_TCL := gen_ibex.tcl

# project target directory:
PROJ_DIR ?= $(shell mktemp -d)

all:
	cd $(PROJ_DIR) && vivado -mode batch -source $(abspath $(GEN_IBEX_TCL))   \
	        -tclargs $(abspath .) $(abspath ibex/) $(abspath $(RAM_FILE))
