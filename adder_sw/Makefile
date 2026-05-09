# # Generic Makefile for Ibex applications
# # Specify program name with PROG, object files with OBJ

# SW_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# RISCV_CC   := ../riscv32/bin/riscv32-unknown-elf-gcc
# RISCV_DUMP := ../riscv32/bin/riscv32-unknown-elf-objdump

# LD_SCRIPT := $(SW_DIR)/link.ld

# CFLAGS = -march=rv32im -mabi=ilp32 -static -mcmodel=medany \
#          -fvisibility=hidden -nostdlib -nostartfiles -Wall \
#          -I$(SW_DIR)/lib/

# # add crt0 to object files
# RISCV_OBJ := $(SW_DIR)/crt0.o $(OBJ)

# all: $(PROG).vmem

# dump: $(PROG).elf
# 	$(RISCV_DUMP) -D $<

# $(PROG).elf: $(RISCV_OBJ) $(LD_SCRIPT)
# 	$(RISCV_CC) $(CFLAGS) -T $(LD_SCRIPT) $(RISCV_OBJ) -o $@

# %.o: %.c
# 	$(RISCV_CC) $(CFLAGS) -c -o $@ $<

# %.o: %.S
# 	$(RISCV_CC) $(CFLAGS) -c -o $@ $<

# %.vmem: %.bin
# 	python3 bin2vmem.py $< > $@

# %.bin: %.elf
# 	../riscv32/bin/riscv32-unknown-elf-objcopy -O binary $^ $@

# clean:
# 	rm -f *.o *.elf *.bin *.vmem



# ---------------------------------------------------------------------
#  Generic Makefile for Ibex applications
#
#  • Define   PROG = <name-without-extension>  on the command line
#  • Define   OBJ  = <list of *.o or *.c>      on the command line
#
#     $ make PROG=aes OBJ="aes.o utils.o"
# ---------------------------------------------------------------------

SW_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# ---------- RISC-V toolchain --------------------------------------------------
RISCV_PREFIX ?= ../riscv32/bin/riscv32-unknown-elf-
RISCV_CC     := $(RISCV_PREFIX)gcc
RISCV_DUMP   := $(RISCV_PREFIX)objdump
RISCV_OBJCOPY:= $(RISCV_PREFIX)objcopy

# ---------- Linker script -----------------------------------------------------
LD_SCRIPT := $(SW_DIR)/link.ld

# ---------- Compiler / linker flags ------------------------------------------
CFLAGS  = -march=rv32im -mabi=ilp32 -static -mcmodel=medany \
          -fvisibility=hidden -nostdlib -nostartfiles -Wall \
          -I$(SW_DIR)/lib/

# Ask the linker to write a map file alongside the ELF
LDFLAGS = -Wl,-Map=$(PROG).map,--cref

# ---------- Object list -------------------------------------------------------
# crt0.o is mandatory; add user-supplied objects afterwards
RISCV_OBJ := $(SW_DIR)/crt0.o $(OBJ)

# ---------------------------------------------------------------------
# Default target: build everything that the simulation needs
# ---------------------------------------------------------------------
.PHONY: all
all: $(PROG).vmem $(PROG).dump $(PROG).map

# ---------------------------------------------------------------------
# Build rules
# ---------------------------------------------------------------------

# Final ELF (linker writes $(PROG).map as a side-effect)
$(PROG).elf: $(RISCV_OBJ) $(LD_SCRIPT)
	$(RISCV_CC) $(CFLAGS) $(LDFLAGS) -T $(LD_SCRIPT) $(RISCV_OBJ) -o $@

# Human-readable disassembly
$(PROG).dump: $(PROG).elf
	$(RISCV_DUMP) -D $< > $@

# Touch rule so Make realises the map now exists
$(PROG).map: $(PROG).elf
	@true

# Compile C and assembly sources
%.o: %.c
	$(RISCV_CC) $(CFLAGS) -c -o $@ $<
%.o: %.S
	$(RISCV_CC) $(CFLAGS) -c -o $@ $<

# ELF ➜ BIN ➜ VMEM
%.bin: %.elf
	$(RISCV_OBJCOPY) -O binary $< $@
%.vmem: %.bin
	python3 bin2vmem.py $< > $@

# ---------------------------------------------------------------------
# House-keeping
# ---------------------------------------------------------------------
.PHONY: clean
clean:
	rm -f *.o *.elf *.bin *.vmem *.dump *.map

