# FPGA area (and timing) of CVA6 on the Nexys Video: the whole SoC
# (ariane_xilinx) as built by `make fpga`, and the core alone (out of context).
#
#   vivado -mode batch -source area/area.tcl -tclargs <src> <out_dir> <part> <clk_period_ns> <impl>
#
# <src>  a copy of the repository on which `make fpga` has run (area/Makefile):
#        the SoC numbers come from its synthesis and implementation runs, the
#        core is synthesized from its corev_apu/fpga/scripts/add_sources.tcl
# <impl> 0: core synthesis + opt_design only; 1: also place and route + timing
#
# Reports (in <out_dir>):
#   soc_util_<stage>.rpt       utilization of ariane_xilinx (core + SoC + DDR3 + clocks)
#   soc_util_hier_<stage>.rpt  the same per hierarchy level (core vs SoC blocks)
#   soc_timing_route.rpt       timing summary of the routed bitstream design
#   core_util_<stage>.rpt      the core (cva6_ooc_top: ariane) alone, out of context
#   core_util_hier_<stage>.rpt the same per hierarchy level
#   core_timing_route.rpt      its timing summary at the board's core clock (impl=1 only)
# <stage> is "opt" (after synthesis and opt_design) or "route".

set src [file normalize [lindex $argv 0]]
set out_dir [file normalize [lindex $argv 1]]
set part [lindex $argv 2]
set clk_period [lindex $argv 3]
set impl [lindex $argv 4]
set area_dir [file dirname [file normalize [info script]]]
set fpga_dir $src/corev_apu/fpga

file mkdir $out_dir
cd $out_dir
set_param general.maxThreads 8

proc write_reports {prefix stage} {
  report_utilization -file ${prefix}_util_${stage}.rpt
  report_utilization -hierarchical -hierarchical_depth 8 -file ${prefix}_util_hier_${stage}.rpt
}

# ---- SoC: the checkpoints of the bitstream flow (corev_apu/fpga/scripts/run.tcl),
# which its Makefile copies to work-fpga/
open_checkpoint $fpga_dir/work-fpga/ariane_xilinx_opt.dcp
write_reports soc opt
close_design

open_checkpoint $fpga_dir/work-fpga/ariane_xilinx_routed.dcp
write_reports soc route
report_timing_summary -max_paths 20 -file soc_timing_route.rpt
close_design

# ---- Core alone (out of context), the board's target: area_core.tcl
set core_area_lib 1
source $area_dir/area_core.tcl
core_area $src $out_dir $part $clk_period $impl $board_target

puts "INFO: reports written to $out_dir"
