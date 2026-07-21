import sys
import csv
import subprocess


def get_symbol_table(elf_file):
    # Get function symbols, start and end addresses and sizes from elf file
    cmd = f"$RISCV/bin/riscv32-unknown-elf-nm -S --defined-only {elf_file}" 
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Symbol table couldn't be saved. Command: {cmd}");
        sys.exit(1)
    
    symbols = []
    # Example symbol line: 80008220 00000016 T pqcrystals_kyber512_ref_polyvec_ntt
    for line in output.strip().split('\n'):
        parts = line.split()
        if len(parts) == 4 and parts[2].upper() in ['T', 't']:
            addr = int(parts[0], 16) & 0xFFFFFFFF
            size = int(parts[1], 16)
            name = parts[3]
            #print(f"ADDR: {addr}, SIZE: {size}, NAME: {name}")
            symbols.append({
                'name': name,
                'start': addr,
                'end': addr + size
            })
    
    return symbols


def find_function(pc_addr, symbols):
    # Finds which symbol the given PC address belongs to
    pc_32 = pc_addr & 0xFFFFFFFF

    for sym in symbols:
        #print(f"SYM[START]: {sym['start']}, PC_32: {pc_32}, SYM[END]: {sym['end']}")
        if sym['start'] <= pc_32 < sym['end']:
            return sym['name']
    
    return "Other / Startup / Lib"


def analyze_csv(csv_file, symbols):
    # Reads sim CSV file and matches PC addresses and functions
    print(f"Reading CSV file: {csv_file} ...")

    func_counts = {}
    total_instructions = 0

    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = [h.strip() for h in next(reader)] # First line is column names

            # Detect PC column index
            pc_idx = None
            for idx, col in enumerate(header):
                if 'pc' in col.lower():
                    pc_idx = idx
                    break

            if pc_idx is None:
                print("ERROR: Could not find a PC column in CSV file!")
                print(f"Existing columns: {header}")
                sys.exit(1)
            
            print("Matching instruction trece...")

            for row in reader:
                if not row or len(row) <= pc_idx:
                    continue
                
                raw_pc = row[pc_idx].strip()
                if not raw_pc:
                    continue

                # Hex/Int conversion
                try:
                    pc = int(raw_pc, 16)
                except ValueError:
                    continue

                func_name = find_function(pc, symbols)
                func_counts[func_name] = func_counts.get(func_name, 0) + 1
                total_instructions += 1    
    
    except Exception as e:
        print(f"ERROR: Could not read CSV: {e}")
        sys.exit(1)
    
    return func_counts, total_instructions


def print_report(func_counts, total_instructions, output_filename="profile_report.txt"):
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f"{'Function Name':<75} | {'Instruction Count':<15} | {'Ratio (%)':<8}\n")
        f.write("-" * 105 + "\n")

        sorted_funcs = sorted(func_counts.items(), key=lambda x: x[1], reverse=True)

        for func, count in sorted_funcs:
            ratio = (count / total_instructions) * 100
            f.write(f"{func:<75} | {count:<17,d} | {ratio:>6.2f}%\n")
        
        print(f"Report saved successfully: {output_filename}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("ERROR: Not enough arguments provided!")
        print("Usage: python3 profile_csv.py <ELF/O_FILE> <SIM_CSV_FILE> [OUTPUT_TXT_FILE]")
        sys.exit(1)
    
    elf_file = sys.argv[1]
    csv_file = sys.argv[2]
    out_file = sys.argv[3] if len(sys.argv) >= 4 else "profile_report.txt"

    symbols = get_symbol_table(elf_file)
    func_counts, total_instructions = analyze_csv(csv_file, symbols)
    print_report(func_counts, total_instructions, out_file)
