################################################################################
# Create Project
################################################################################

if {$argc != 2 && $argc != 3} {
    puts "usage: gen_ibex.tcl SOC-DIR IBEX-DIR [RAM-FILE]"
    exit 2
}

# get command line arguments:
set soc_dir [lindex $argv 0]
set ibex_dir [lindex $argv 1]

# create project:
set _xil_proj_name_ "IbexSoC"
create_project -part xc7a200tsbg484-1 ${_xil_proj_name_} ${_xil_proj_name_}
set proj_dir [get_property directory [current_project]]

# set project properties
set obj [current_project]
set_property -name "default_lib" -value "xil_defaultlib" -objects $obj

# add source files:
set obj [get_filesets sources_1]
set src_list {}
lappend src_list "$soc_dir/rtl/ibex_soc.sv"
lappend src_list "$soc_dir/rtl/ram.sv"
lappend src_list "$soc_dir/rtl/uart.sv"
foreach file {ibex_pkg.sv ibex_core.sv ibex_alu.sv ibex_branch_predict.sv
              ibex_compressed_decoder.sv ibex_controller.sv ibex_core_tracing.sv
              ibex_counter.sv ibex_cs_registers.sv ibex_csr.sv ibex_decoder.sv
              ibex_dummy_instr.sv ibex_ex_block.sv ibex_fetch_fifo.sv
              ibex_icache.sv ibex_id_stage.sv ibex_if_stage.sv ibex_load_store_unit.sv
              ibex_multdiv_fast.sv ibex_multdiv_slow.sv ibex_pmp.sv ibex_prefetch_buffer.sv
              ibex_register_file_ff.sv ibex_register_file_fpga.sv ibex_wb_stage.sv
              ibex_tracer_pkg.sv ibex_tracer.sv} {
    lappend src_list "$ibex_dir/rtl/$file"
}
lappend src_list "$ibex_dir/syn/rtl/prim_clock_gating.v"
lappend src_list "$ibex_dir/dv/fcov/"
lappend src_list "$ibex_dir/vendor/lowrisc_ip/ip/prim/rtl/"
add_files -fileset $obj -norecurse -scan_for_includes $src_list

# add simulation only files:
set obj [get_filesets sim_1]
set src_list {}
lappend src_list "$soc_dir/rtl/ibex_soc_tb.sv"
add_files -fileset $obj -norecurse -scan_for_includes $src_list

# set top modules:
set_property top ibex_soc [get_filesets sources_1]
set_property top ibex_soc_tb [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]

# add constraint files:
set obj [get_filesets constrs_1]
add_files -fileset $obj -norecurse "$soc_dir/nexysvideo.xdc"

# set memory initialization files:
if {$argc == 3} {
    set ram_file_var "RAM_FPATH=[lindex $argv 2]"
    set_property generic "$ram_file_var" -objects [get_filesets sources_1]
    set_property generic "$ram_file_var" -objects [get_filesets sim_1]
}
