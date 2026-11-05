# FPGA area (and timing) of the CVA6 core alone (out of context), for any
# target configuration.
#
#   vivado -mode batch -source area/area_core.tcl -tclargs <src> <out_dir> <part> <clk_period_ns> <impl> <target>
#
# <src>    a copy of the repository on which `make fpga` has run (area/Makefile);
#          its corev_apu/fpga/scripts/add_sources.tcl gives the sources, with
#          the configuration package of the board build swapped for <target>'s
# <impl>   0: synthesis + opt_design only; 1: also place and route + timing
# <target> a core/include/<target>_config_pkg.sv
#
# Reports (in <out_dir>): core_util_<stage>.rpt, core_util_hier_<stage>.rpt,
# core_timing_route.rpt (impl=1 only); <stage> is "opt" or "route".
#
# area.tcl sources this file (with core_area_lib set) for the board's own target.

# configuration package of the board build (make fpga target=...)
set board_target cv32a6_ima_sv32_fpga

proc core_area {src out_dir part clk_period impl target} {
  global board_target
  set fpga_dir $src/corev_apu/fpga
  file mkdir $out_dir

  # Out of context, so its ports get no I/O buffers and nothing outside it can
  # optimize it away or merge with it. Same sources, include directories and
  # synthesis options (retiming) as run.tcl; the clock is the board's core clock.
  set_part $part
  set f [open $fpga_dir/scripts/add_sources.tcl]
  set sources [string map [list \
    /core/include/${board_target}_config_pkg.sv /core/include/${target}_config_pkg.sv] [read $f]]
  close $f
  if {![file exists $src/core/include/${target}_config_pkg.sv]} {
    error "no configuration package for $target"
  }
  cd $fpga_dir
  eval $sources
  cd $out_dir
  read_verilog -sv $::core_area_dir/cva6_ooc_top.sv
  # board header as a global include, as in run.tcl (ariane_xilinx.sv needs it)
  read_verilog -sv [list $fpga_dir/src/nexys_video.svh $src/vendor/pulp-platform/common_cells/include/common_cells/registers.svh]
  set_property -dict {file_type {Verilog Header} is_global_include 1} \
    [get_files [list *nexys_video.svh *common_cells/registers.svh]]
  set include_dirs [list \
    $fpga_dir/src/axi_sd_bridge/include \
    $src/vendor/pulp-platform/common_cells/include \
    $src/vendor/pulp-platform/axi/include \
    $src/core/cache_subsystem/hpdcache/rtl/include \
    $src/corev_apu/register_interface/include \
    $src/corev_apu/instr_tracing/ITI/include \
    $src/core/include]
  synth_design -top cva6_ooc_top -part $part -mode out_of_context \
    -include_dirs $include_dirs -global_retiming on
  create_clock -name clk -period $clk_period [get_ports clk_i]
  opt_design
  report_utilization -file core_util_opt.rpt
  report_utilization -hierarchical -hierarchical_depth 8 -file core_util_hier_opt.rpt
  if {$impl} {
    place_design
    phys_opt_design
    route_design
    report_utilization -file core_util_route.rpt
    report_utilization -hierarchical -hierarchical_depth 8 -file core_util_hier_route.rpt
    report_timing_summary -max_paths 20 -file core_timing_route.rpt
  }
  close_design
  # the next run starts from an empty in-memory project
  set files [get_files -quiet]
  if {[llength $files]} { remove_files $files }
}

set core_area_dir [file dirname [file normalize [info script]]]

# run directly (not sourced by area.tcl)
if {![info exists core_area_lib]} {
  set_param general.maxThreads 8
  core_area [file normalize [lindex $argv 0]] [file normalize [lindex $argv 1]] \
    [lindex $argv 2] [lindex $argv 3] [lindex $argv 4] [lindex $argv 5]
  puts "INFO: reports written to [file normalize [lindex $argv 1]]"
}
