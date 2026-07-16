#!/bin/bash

# Change the target to your desired configuration
export DV_TARGET="cv32a60x"

# If you want to change the simulator (default: veri-testharness,spike)
# and number of cores (default: 8), modify this part
export DV_SIMULATORS=veri-testharness,spike
export NUM_JOBS=8

############################################################################################

TEST_NAME="test_kyber"

cd $ROOT_PROJECT
make clean
cd $ROOT_PROJECT/verif/sim
make clean_all

python3 cva6.py \
    --target $DV_TARGET \
    --iss=$DV_SIMULATORS \
    --iss_yaml=cva6.yaml \
    --issrun_opts="+time_out=500000000" \
    --iss_timeout 100000 \
    --c_tests ../tests/custom/kyber/test/test_kyber.c \
    --linker=../../config/gen_from_riscv_config/linker/link.ld \
    --gcc_opts="-O3 -static -mcmodel=medany -fvisibility=hidden -nostdlib -nostartfiles \
    -g ../tests/custom/common/syscalls.c ../tests/custom/common/crt.S \
    ../tests/custom/kyber/cbd.c \
    ../tests/custom/kyber/fips202.c \
    ../tests/custom/kyber/indcpa.c \
    ../tests/custom/kyber/kem.c \
    ../tests/custom/kyber/ntt.c \
    ../tests/custom/kyber/poly.c \
    ../tests/custom/kyber/polyvec.c \
    ../tests/custom/kyber/randombytes.c \
    ../tests/custom/kyber/reduce.c \
    ../tests/custom/kyber/symmetric-shake.c \
    ../tests/custom/kyber/verify.c \
    ../tests/custom/kyber/test/test_print.c \
    -lgcc -I../tests/custom/env -I../tests/custom/common -I../tests/custom/kyber"

LATEST_OUT_DIR=$(ls -td out_* | head -n 1)
# If log file size exceeds this value, file is not copied to pqc_tests (default: 50 MB)
MAX_LOGFILE_SIZE=50000000

if [ -n $LATEST_OUT_DIR ]; then
    LOG_FILE=$LATEST_OUT_DIR/veri-testharness_sim/$TEST_NAME.$DV_TARGET.log
    LOG_ISS_FILE=$LATEST_OUT_DIR/veri-testharness_sim/$TEST_NAME.$DV_TARGET.log.iss

    if [ -f $LOG_FILE ]; then
        FILE_SIZE=$(wc -c < $LOG_FILE)
        if [ $FILE_SIZE -le $MAX_LOGFILE_SIZE ]; then
            cp $LOG_FILE ../../pqc_tests/$TEST_NAME.log
        else
            echo "Log file size exceeds the maximum limit, copy aborted."
        fi
    else
        echo "WARNING: .log file could not be found!"
    fi

    if [ -f $LOG_ISS_FILE ]; then
        cp $LOG_ISS_FILE ../../pqc_tests/$TEST_NAME.log.iss
    else
        echo "WARNING: .log.iss file could not be found!"
    fi
else
    echo "WARNING: out_* folder could not be found!"
fi

cd $ROOT_PROJECT