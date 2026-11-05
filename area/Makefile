# FPGA area of CVA6 on the Nexys Video, core vs SoC (Vivado on the host).
#
#   make -C area            copy the repo, run `make fpga` on the copy (the full
#                           bitstream flow), then the area reports: SoC from the
#                           routed design, core alone placed and routed
#   make -C area IMPL=0     core alone only synthesized (SoC is always routed)
#   make -C area reports    only rerun area.tcl on an existing build
#   make -C area summary    only rebuild area.md from existing reports
#   make -C area configs    the core alone for each of CONFIGS (other CVA6
#                           targets), from the same copy; configs.md compares them.
#                           Run without -j: a 64-bit core can take many GB in
#                           synthesis; each run is capped at MEMMAX (systemd scope)
#                           so running out kills that Vivado, not the desktop
#
# Nothing in the repository is written: the flow runs on a copy in
# build/area/nexys_video/src (the bitstream flow generates IPs, bootrom and
# add_sources.tcl inside the source tree). Output: build/area/nexys_video/area.md
# and the Vivado reports next to it.

ROOT     := $(abspath ..)
VIVADO   ?= vivado
TARGET   ?= cv32a6_ima_sv32_fpga
BOARD    := nexys_video
PART     := xc7a200tsbg484-1
XBOARD   ?= digilentinc.com:nexys_video:part0:1.2
CLK_NS   ?= 40
RISCV    ?= $(HOME)/riscv32
CROSS    ?= riscv32-unknown-elf-
IMPL     ?= 1
DEPTH    ?= 2
OUT      ?= $(ROOT)/build/area/$(BOARD)
SRC      := $(OUT)/src
BOARDS   := $(OUT)/boards

# Nexys Video board files (Vivado batch mode does not see the XHub store)
BOARD_REPO_PATHS ?= $(BOARDS)/vivado-boards-master/new/board_files
export BOARD_REPO_PATHS

# core configurations compared by `make configs` (the board's own target first).
# Not included: cv64a60ax (its config package does not set RVZiCbom, so it does
# not compile), cv64a6_imafdcv_sv39 (needs the Ara vector unit),
# cv64a6_imafdc_sv39_openpiton (OpenPiton NoC interface).
CONFIGS  ?= cv32a6_ima_sv32_fpga cv32a6_imac_sv32 cv32a60x cv32a65x \
            cv64a6_imafdc_sv39 cv64a6_imafdch_sv39 cv64a6_imafdc_sv39_wb \
            cv64a6_imafdc_sv39_hpdcache cv64a6_imafdc_sv39_hpdcache_wb
CFG_OUT  := $(OUT)/configs
CFG_RPT  := $(if $(filter 1,$(IMPL)),route,opt)
MEMMAX   ?= 20G

ROUTED := $(SRC)/corev_apu/fpga/work-fpga/ariane_xilinx_routed.dcp

.PHONY: area reports summary configs configs-summary clean

area: $(ROUTED)
	$(MAKE) --no-print-directory reports

$(BOARDS)/.done:
	mkdir -p $(BOARDS)
	curl -sL https://github.com/Digilent/vivado-boards/archive/refs/heads/master.tar.gz | \
	    tar xz -C $(BOARDS) --wildcards '*/new/board_files/nexys_video/*'
	touch $@

$(SRC)/.done:
	mkdir -p $(SRC)
	rsync -a --delete --exclude /.git --exclude /build --exclude /area $(ROOT)/ $(SRC)/
	cd $(ROOT) && echo "$$(git rev-parse --short HEAD)$$(git diff --quiet HEAD -- . ':!area' || echo ' (modified)')" > $(OUT)/commit.txt
	touch $@

# CC: the bootrom C code passes pointers as integers, an error since GCC 14
$(ROUTED): $(SRC)/.done $(BOARDS)/.done
	cd $(SRC) && $(MAKE) fpga target=$(TARGET) BOARD=$(BOARD) XILINX_BOARD=$(XBOARD) \
	    RISCV=$(RISCV) CROSSCOMPILE=$(CROSS) OBJCOPY=$(RISCV)/bin/$(CROSS)objcopy \
	    CC="$(RISCV)/bin/$(CROSS)gcc -Wno-error=int-conversion" > $(OUT)/make_fpga.log 2>&1

reports:
	cd $(OUT) && $(VIVADO) -mode batch -nojournal -log vivado.log \
	    -source $(ROOT)/area/area.tcl -tclargs $(SRC) $(OUT) $(PART) $(CLK_NS) $(IMPL) > /dev/null
	$(MAKE) --no-print-directory summary

summary:
	python3 -B $(ROOT)/area/area_summary.py $(OUT) --depth $(DEPTH) -o $(OUT)/area.md

configs: $(foreach c,$(CONFIGS),$(CFG_OUT)/$(c)/core_util_hier_$(CFG_RPT).rpt)
	$(MAKE) --no-print-directory configs-summary

$(CFG_OUT)/%/core_util_hier_$(CFG_RPT).rpt: | $(ROUTED)
	mkdir -p $(CFG_OUT)/$*
	cd $(CFG_OUT)/$* && systemd-run --user --scope -q -p MemoryMax=$(MEMMAX) -p MemorySwapMax=0 \
	    $(VIVADO) -mode batch -nojournal -log vivado.log \
	    -source $(ROOT)/area/area_core.tcl -tclargs $(SRC) $(CFG_OUT)/$* $(PART) $(CLK_NS) $(IMPL) $* > /dev/null

configs-summary:
	python3 -B $(ROOT)/area/area_configs.py $(CFG_OUT) $(CONFIGS) -o $(OUT)/configs.md

clean:
	rm -rf $(OUT)
