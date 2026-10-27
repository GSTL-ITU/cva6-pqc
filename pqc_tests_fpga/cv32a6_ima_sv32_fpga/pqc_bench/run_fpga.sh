#!/bin/sh
# Runs one ELF on CVA6 on the Nexys Video without touching the board:
# (optionally) programs the bitstream, starts the UART logger, loads the ELF
# with OpenOCD + GDB (both in the hornet-dev Docker image, or any image with
# openocd, riscv-none-elf-gdb and pyserial), and waits for the end of the output.
#
#   run_fpga.sh <prog.elf> <log> [until text] [--trigger] [--bit <bitstream>]
#
#   BIT=<bitstream>  program it first (Vivado on the host)
#   PORT=/dev/ttyUSB0 (USB-UART), IMAGE=hornet-dev:latest, TIMEOUT=3600 s
set -e
elf=$(realpath "$1"); log=$(realpath -m "$2"); until=${3:-"result "}; shift 3 2>/dev/null || shift $#
trigger=""
for a in "$@"; do [ "$a" = "--trigger" ] && trigger="--trigger"; done
port=${PORT:-/dev/ttyUSB0}
image=${IMAGE:-hornet-dev:latest}
limit=${TIMEOUT:-3600}
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../.." && pwd)
mkdir -p "$(dirname "$log")"

if [ -n "$BIT" ]; then
    printf 'open_hw_manager\nconnect_hw_server\nopen_hw_target\nset d [lindex [get_hw_devices xc7a200t*] 0]\ncurrent_hw_device $d\nset_property PROGRAM.FILE {%s} $d\nprogram_hw_devices $d\nclose_hw_manager\n' "$(realpath "$BIT")" > "$log.program.tcl"
    vivado -mode batch -nojournal -nolog -source "$log.program.tcl" > "$log.jtag" 2>&1
fi
# OpenOCD needs the FTDI that Vivado's hardware server keeps open
pkill -x hw_server 2>/dev/null || true
sleep 1

# the JTAG/UART bridge of the board (Digilent FT2232)
bus=$(lsusb -d 0403:6010 | head -1 | sed -E 's/Bus ([0-9]+) Device ([0-9]+).*/\1\/\2/')
[ -n "$bus" ] || { echo "no FT2232 (0403:6010) found" >&2; exit 1; }

docker run --rm --device "$port" -u "$(id -u):$(id -g)" --group-add "$(stat -c %g "$port")" \
    -v "$here:$here" -v "$(dirname "$log"):$(dirname "$log")" "$image" \
    timeout "$limit" python3 "$here/uart_log.py" --port "$port" --log "$log" --until "$until" --timeout "$limit" $trigger \
    > "$log.console" 2>&1 &
logger=$!
sleep 2

# OpenOCD stays connected while the program runs (stopping it disturbs the core)
ocd=cva6-openocd-$$
docker run -d --rm --name "$ocd" --network host --device "/dev/bus/usb/$bus" -u "$(id -u):$(id -g)" --group-add 0 \
    -v "$here:$here" -v "$(dirname "$elf"):$(dirname "$elf")" -v "$(dirname "$log"):$(dirname "$log")" \
    "$image" sh -c "openocd -f '$here/nexys_video.cfg' > '$log.openocd' 2>&1" > /dev/null
for i in $(seq 30); do grep -q 'Listening on port 3333' "$log.openocd" 2>/dev/null && break; sleep 1; done
docker exec "$ocd" riscv-none-elf-gdb -batch -ex 'set confirm off' -ex 'target extended-remote localhost:3333' \
    -ex load -ex 'info registers pc' -ex 'monitor resume' -ex detach "$elf" > "$log.gdb" 2>&1 || true

rc=0
wait $logger || rc=1
docker kill "$ocd" > /dev/null 2>&1 || true
if [ $rc = 0 ]; then
    echo "done: $log"
else
    echo "no complete output, see $log.console $log.openocd $log.gdb" >&2
    exit 1
fi
