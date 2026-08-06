#!/bin/bash

# Change the target to your desired configuration
export DV_TARGET="cv32a60x"
# You can modify this to change the Falcon parameter (9 for Falcon-512, 10 for Falcon-1024)
FALCON_LOGN=9

# If you want to change the simulator (default: veri-testharness,spike)
# and number of cores (default: 8), modify this part
export DV_SIMULATORS=veri-testharness,spike
export NUM_JOBS=8

# Set this to 1 if you want to print clock cycles (through UART)
# This will create mismatches between spike and verilator logs
PRINT_CYCLES=0

# Set this to 1 if you want a detailed report on instruction counts and ratios
PROFILE=0

# Set these to 1 if you want to logs these values and their hamming weights
# WARNING: File sizes might be large!
# ALU operand a-b and result (ex-stage)
LOG_ALU=0
# x0 to x31 (id-stage)
LOG_REGFILE=0
# load-store results (ex-stage)
LOG_LSU=0
 
############################################################################################

TEST_NAME="test_falcon"

cd $ROOT_PROJECT
make clean
cd $ROOT_PROJECT/verif/sim
make clean_all

export EXTRA_FLAGS=""
if [ $PRINT_CYCLES -eq 1 ]; then
    export EXTRA_FLAGS+=" -DPRINT_CYCLES"
fi
export PQC_TESTS_CFLAGS=""
if [ $LOG_ALU -eq 1 ]; then
    echo "ALU logging is enabled. Logs can be found in '${TEST_NAME}_alu_cycle_trace.log' in cva6-pqc/pqc_tests"
    export PQC_TESTS_CFLAGS+=" -DLOG_ALU -DTEST_NAME=$TEST_NAME"
fi
if [ $LOG_REGFILE -eq 1 ]; then
    echo "Register file logging is enabled. Logs can be found in '${TEST_NAME}_rf_cycle_trace.log' in cva6-pqc/pqc_tests"
    export PQC_TESTS_CFLAGS+=" -DLOG_REGFILE -DTEST_NAME=$TEST_NAME"
fi
if [ $LOG_LSU -eq 1 ]; then
    echo "Load-store unit logging is enabled. Logs can be found in '${TEST_NAME}_lsu_cycle_trace.log' in cva6-pqc/pqc_tests"
    export PQC_TESTS_CFLAGS+=" -DLOG_LSU -DTEST_NAME=$TEST_NAME"
fi
export EXTRA_FLAGS+=" -DFALCON_LOGN=$FALCON_LOGN"

# NOTE: The list of .c files below is based on the standard reference implementation of Falcon.
# Adjust them if your specific Falcon implementation combines or renames them.
python3 cva6.py \
    --target $DV_TARGET \
    --iss=$DV_SIMULATORS \
    --iss_yaml=cva6.yaml \
    --issrun_opts="+time_out=5000000000" \
    --iss_timeout 1000000 \
    --c_tests ../tests/custom/falcon/test/test_falcon.c \
    --linker=../../config/gen_from_riscv_config/linker/link.ld \
    --gcc_opts="-O3 -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles \
    -g ../tests/custom/common/syscalls.c ../tests/custom/common/crt.S \
    ../tests/custom/falcon/codec.c \
    ../tests/custom/falcon/common.c \
    ../tests/custom/falcon/falcon.c \
    ../tests/custom/falcon/fft.c \
    ../tests/custom/falcon/fpr.c \
    ../tests/custom/falcon/keygen.c \
    ../tests/custom/falcon/rng.c \
    ../tests/custom/falcon/shake.c \
    ../tests/custom/falcon/sign.c \
    ../tests/custom/falcon/vrfy.c \
    ../tests/custom/falcon/test/test_print.c \
    -lgcc -I../tests/custom/env -I../tests/custom/common -I../tests/custom/falcon $EXTRA_FLAGS"

LATEST_OUT_DIR=$(ls -td out_* | head -n 1)
# If log file size exceeds this value, file is not copied to pqc_tests (default: 50 MB)
MAX_LOGFILE_SIZE=50000000

if [ -n $LATEST_OUT_DIR ]; then
    LOG_FILE=$LATEST_OUT_DIR/veri-testharness_sim/$TEST_NAME.$DV_TARGET.log
    LOG_ISS_FILE=$LATEST_OUT_DIR/veri-testharness_sim/$TEST_NAME.$DV_TARGET.log.iss

    if [ -f $LOG_FILE ]; then
        FILE_SIZE=$(wc -c < $LOG_FILE)
        if [ $FILE_SIZE -le $MAX_LOGFILE_SIZE ]; then
            echo "Copying log file into pqc_tests/$TEST_NAME.log"
            cp $LOG_FILE ../../pqc_tests/$TEST_NAME.log
        else
            echo "Log file size exceeds the maximum limit, copy aborted."
        fi
    else
        echo "WARNING: .log file could not be found!"
    fi

    if [ -f $LOG_ISS_FILE ]; then
        echo "Copying log.iss file into pqc_tests/$TEST_NAME.log.iss"
        cp $LOG_ISS_FILE ../../pqc_tests/$TEST_NAME.log.iss
    else
        echo "WARNING: .log.iss file could not be found!"
    fi

    if [ $PROFILE -eq 1 ]; then
        echo "Running CSV profiler for $TEST_NAME ..."

        CSV_FILE=$(find $LATEST_OUT_DIR/veri-testharness_sim -name "$TEST_NAME.$DV_TARGET.csv" | head -n 1)
        OBJ_FILE=$(find $LATEST_OUT_DIR/directed_tests -name "$TEST_NAME*.o" | head -n 1)

        if [ -f $CSV_FILE ] && [ -f $OBJ_FILE ]; then
            PROFILE_OUT_PATH="../../pqc_tests/${TEST_NAME}_profile.txt"

            echo "Generating profile report: pqc_tests/${TEST_NAME}_profile.txt"
            python3 ../../pqc_tests/profile_csv.py $OBJ_FILE $CSV_FILE $PROFILE_OUT_PATH
        else
            echo "WARNING: Profile files are missing!"
            [ ! -f $CSV_FILE ] && echo "    -> CSV file not found in $LATEST_OUT_DIR"
            [ ! -f $OBJ_FILE ] && echo "    -> Compiled Object/ELF file not found in $LATEST_OUT_DIR"
        fi
    fi
else
    echo "WARNING: out_* folder could not be found!"
fi

cd $ROOT_PROJECT