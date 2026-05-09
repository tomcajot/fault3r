.PRECIOUS: %.bin

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

