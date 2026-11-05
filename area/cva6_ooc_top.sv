// Top for synthesizing the CVA6 core alone (out of context), with the same
// configuration as the core in corev_apu/fpga/src/ariane_xilinx.sv: the target's
// cva6_config_pkg (cv32a6_ima_sv32_fpga on the board, any other with
// area_core.tcl) through build_fpga_config, and the same ariane wrapper (cva6 +
// the CV-X-IF example coprocessor when CvxifEn).
//
// FpgaEn is forced on, which only the FPGA target sets itself: register files,
// FIFOs and branch predictors then map to LUTRAM/BRAM instead of flip-flops.
// TechnoCut is forced off (cv32a60x, cv32a65x set it): the caches then use the
// generic SRAM wrappers (BRAM) instead of an ASIC macro left as a black box.
//
// The ports are those of the core in the SoC: AXI to the crossbar, interrupts,
// debug request. The RVFI probes (trace) are left open here; in ariane_xilinx
// they only feed cva6_rvfi and the instruction tracer, which are SoC blocks.
// Boot address and hart ID are constants, as in ariane_xilinx.

`include "rvfi_types.svh"

module cva6_ooc_top (
  input  logic              clk_i,
  input  logic              rst_ni,
  input  logic [1:0]        irq_i,
  input  logic              ipi_i,
  input  logic              time_irq_i,
  input  logic              debug_req_i,
  output ariane_axi::req_t  noc_req_o,
  input  ariane_axi::resp_t noc_resp_i
);

// same as build_fpga_config in ariane_xilinx.sv, plus FpgaEn and TechnoCut
function automatic config_pkg::cva6_cfg_t build_fpga_config(config_pkg::cva6_user_cfg_t CVA6UserCfg);
  config_pkg::cva6_user_cfg_t cfg = CVA6UserCfg;
  cfg.FpgaEn = bit'(1);
  cfg.TechnoCut = bit'(0);
  cfg.RVZiCond = bit'(0);
  cfg.NrNonIdempotentRules = unsigned'(1);
  cfg.NonIdempotentAddrBase = 1024'({64'b0});
  cfg.NonIdempotentLength = 1024'({ariane_soc::DRAMBase});
  return build_config_pkg::build_config(cfg);
endfunction

localparam config_pkg::cva6_cfg_t CVA6Cfg = build_fpga_config(cva6_config_pkg::cva6_cfg);

localparam type rvfi_probes_instr_t = `RVFI_PROBES_INSTR_T(CVA6Cfg);
localparam type rvfi_probes_csr_t = `RVFI_PROBES_CSR_T(CVA6Cfg);
localparam type rvfi_probes_t = struct packed {
  logic csr;
  rvfi_probes_instr_t instr;
};

ariane #(
    .CVA6Cfg ( CVA6Cfg ),
    .rvfi_probes_instr_t ( rvfi_probes_instr_t ),
    .rvfi_probes_csr_t ( rvfi_probes_csr_t ),
    .rvfi_probes_t ( rvfi_probes_t )
) i_ariane (
    .clk_i        ( clk_i               ),
    .rst_ni       ( rst_ni              ),
    .boot_addr_i  ( ariane_soc::ROMBase ),
    .hart_id_i    ( '0                  ),
    .irq_i        ( irq_i               ),
    .ipi_i        ( ipi_i               ),
    .time_irq_i   ( time_irq_i          ),
    .rvfi_probes_o(                     ),
    .debug_req_i  ( debug_req_i         ),
    .noc_req_o    ( noc_req_o           ),
    .noc_resp_i   ( noc_resp_i          )
);

endmodule
