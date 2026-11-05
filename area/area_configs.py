#!/usr/bin/env python3
"""Compare the area of CVA6 core configurations (area_core.tcl, `make configs`).

  area_configs.py <configs dir> <target>... [-o out.md] [--src <repo copy>]

For each <target>: <configs dir>/<target>/core_util_hier_<stage>.rpt (route if
present, else opt), core_util_<stage>.rpt for the device capacity and
core_timing_route.rpt for the setup WNS. The features of each target come from
<src>/core/include/<target>_config_pkg.sv (default: the copy next to <configs dir>).
"""

import os
import re
import sys

from area_summary import (COLUMNS, find, fmt, parse_capacity, parse_hier, parse_path, parse_wns,
                          path_rows, sub, total)

CLK_NS = 40.0  # area/Makefile CLK_NS: the board's 25 MHz core clock

# blocks of cva6 in the breakdown: header, module name prefixes
BLOCKS = [
    ('Frontend', ('frontend',)),
    ('ID', ('id_stage',)),
    ('Issue', ('issue_stage',)),
    ('EX (ALU, mul/div, LSU)', ('ex_stage',)),
    ('FPU', ('fpu_wrap',)),
    ('MMU', ('cva6_mmu',)),
    ('Caches', ('wt_cache_subsystem', 'std_cache_subsystem', 'cva6_hpdcache_subsystem')),
    ('CSR', ('csr_regfile',)),
]


def config_fields(path):
    """Field -> value of the cva6_cfg struct in a config package, with the
    CVA6Config* localparams it refers to resolved."""
    text = open(path).read()
    params = dict(re.findall(r'localparam\s+(?:\S+\s+)?(CVA6Config\w+)\s*=\s*([^;]+);', text))
    fields = {}
    for name, value in re.findall(r'^\s*(\w+)\s*:\s*([^,\n]+),', text, re.M):
        m = re.match(r"\w*'\((.*)\)$", value.strip())
        value = m.group(1) if m else value.strip()
        value = params.get(value, value).strip()
        value = re.sub(r'^config_pkg::', '', value)
        fields[name] = value
    return fields


def features(f):
    """Short description of a configuration: ISA, caches, pipeline."""
    on = lambda k: f.get(k, '0') in ('1', "1'b1")
    isa = f'RV{f.get("XLEN", "?")}IM' + ''.join(
        e for e, k in (('A', 'RVA'), ('F', 'RVF'), ('D', 'RVD'), ('C', 'RVC'), ('B', 'RVB'),
                       ('H', 'RVH'), ('V', 'RVV')) if on(k))
    def size(k):
        if not f.get(k, '').isdigit():
            return '?'
        n = int(f[k])
        return f'{n // 1024} KiB' if n % 1024 == 0 else f'{n} B'
    dcache = {'WT': 'WT', 'WB': 'WB', 'HPDCACHE_WT': 'HPD-WT', 'HPDCACHE_WB': 'HPD-WB'}.get(
        f.get('DCacheType', ''), f.get('DCacheType', '?'))
    parts = [isa, 'MMU' if on('MmuPresent') else 'no MMU',
             f'I$ {size("IcacheByteSize")}, D$ {size("DcacheByteSize")} {dcache}',
             f'SB {f.get("NrScoreboardEntries", "?")}',
             f'{f.get("NrCommitPorts", "?")} commit']
    if on('SuperscalarEn'):
        parts.append('superscalar')
    if on('CvxifEn'):
        parts.append('CV-X-IF + example coprocessor' if f.get('CoproType') == 'COPRO_EXAMPLE'
                     else 'CV-X-IF port')
    return ', '.join(parts)


def blocks(cva6):
    """LUTs of each BLOCKS entry under cva6; EX without the FPU and MMU inside it."""
    out = {}
    for name, prefixes in BLOCKS:
        r = find(cva6, lambda n: n is not cva6 and n.module.startswith(prefixes))
        out[name] = r[0].values if r else None
    ex = out['EX (ALU, mul/div, LSU)']
    if ex:
        for inner in ('FPU', 'MMU'):
            if out[inner]:
                ex = sub(ex, out[inner])
        out['EX (ALU, mul/div, LSU)'] = ex
    known = [v for v in out.values() if v]
    out['Other'] = sub(cva6.values, total_values(known))
    return out


def total_values(values):
    t = {k: 0.0 for k, _ in COLUMNS}
    for v in values:
        for k in t:
            t[k] += v[k]
    return t


def main(argv):
    args = argv[1:]
    out_path = None
    src = None
    if '-o' in args:
        i = args.index('-o')
        out_path = args[i + 1]
        del args[i:i + 2]
    if '--src' in args:
        i = args.index('--src')
        src = args[i + 1]
        del args[i:i + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    cdir, targets = args[0], args[1:]
    src = src or os.path.join(os.path.dirname(os.path.abspath(cdir)), 'src')

    rows = []
    avail = {}
    device = '?'
    for t in targets:
        d = f'{cdir}/{t}'
        stage = 'route' if os.path.exists(f'{d}/core_util_hier_route.rpt') else 'opt'
        if not os.path.exists(f'{d}/core_util_hier_{stage}.rpt'):
            rows.append((t, None))
            continue
        root = parse_hier(f'{d}/core_util_hier_{stage}.rpt')
        device, avail = parse_capacity(f'{d}/core_util_{stage}.rpt')
        core = find(root, lambda n: n.name == 'i_ariane')
        core = core[0] if core else root
        cva6 = find(core, lambda n: n.name == 'i_cva6')
        cva6 = cva6[0] if cva6 else core
        pkg = f'{src}/core/include/{t}_config_pkg.sv'
        rows.append((t, {
            'stage': stage,
            'core': core.values,
            'cva6': cva6.values,
            'blocks': blocks(cva6),
            'wns': parse_wns(f'{d}/core_timing_route.rpt'),
            # the first path of the timing summary is the worst setup path
            'path': parse_path(f'{d}/core_timing_route.rpt'),
            'features': features(config_fields(pkg)) if os.path.exists(pkg) else '?',
        }))

    stages = {r['stage'] for _, r in rows if r}
    stage_text = ' and '.join({'opt': 'after synthesis and opt_design',
                               'route': 'after place and route'}[s] for s in sorted(stages))
    lines = ['# CVA6 core configurations: FPGA area', '',
             f'The core alone (`ariane`, out of context) on {device}, {stage_text}, '
             f'clock constraint {CLK_NS:g} ns (25 MHz, the Nexys Video core clock). '
             'Every configuration with the board build\'s settings (`build_fpga_config` of '
             '`ariane_xilinx`) and FpgaEn on, so register files, FIFOs and branch predictors '
             'use LUTRAM/BRAM as on the board.', '',
             '## Summary', '',
             '| Configuration | LUTs | LUT as logic | LUTRAM | FFs | BRAM (36 Kb) | DSPs '
             '| cva6 LUTs (without coprocessor) | % device LUTs | WNS (ns) |',
             '|---|' + '---:|' * 9]
    for t, r in rows:
        if r is None:
            lines.append(f'| `{t}` | *failed* |' + ' |' * 8)
            continue
        v = r['core']
        wns = f'{r["wns"]:+.3f}' if r['wns'] is not None else '-'
        share = f'{100 * v["lut"] / avail["lut"]:.1f}%' if avail.get('lut') else '-'
        lines.append(f'| `{t}` | ' + ' | '.join(
            fmt(v[k], k) for k in ('lut', 'logic', 'lutram', 'ff', 'bram', 'dsp'))
            + f' | {fmt(r["cva6"]["lut"], "lut")} | {share} | {wns} |')
    lines.append('')

    lines += ['## Features', '', '| Configuration | Features |', '|---|---|']
    for t, r in rows:
        lines.append(f'| `{t}` | {r["features"] if r else "-"} |')
    lines += ['', 'SB: scoreboard entries. D$ types: WT write-through, WB write-back, '
              'HPD HPDcache. CV-X-IF port: the coprocessor interface of cva6, with no coprocessor; '
              '+ example coprocessor: `ariane` also instantiates cvxif_example_coprocessor, '
              'which is in the totals but not in the "cva6 LUTs" column.', '']

    paths = [(t, r['path']) for t, r in rows if r and r['path']]
    if paths:
        lines += ['## Critical path', '']
        lines += path_rows([(f'`{t}`', p) for t, p in paths])
        lines += ['', 'Setup at the slow process corner, all at the same '
                  f'{CLK_NS:g} ns constraint. Min period is requirement - slack. It is how far '
                  'each routed result could be clocked, not the best that configuration could '
                  'reach: the tools stop optimizing once timing is met, so configurations with '
                  'much slack are understated the most, and the Fmax column is not a fair '
                  'ranking of the configurations.', '']
        lines += [f'- `{t}`: `{p["source"]}` to `{p["dest"]}`' for t, p in paths]
        lines.append('')

    names = [b for b, _ in BLOCKS] + ['Other']
    for key, title in (('lut', 'LUTs'), ('ff', 'FFs'), ('bram', 'BRAM (36 Kb)')):
        lines += [f'## {title} by block', '',
                  '| Configuration | ' + ' | '.join(names) + ' |',
                  '|---|' + '---:|' * len(names)]
        for t, r in rows:
            if r is None:
                continue
            cells = [fmt(r['blocks'][b][key], key) if r['blocks'][b] else '-' for b in names]
            lines.append(f'| `{t}` | ' + ' | '.join(cells) + ' |')
        lines.append('')

    lines += [
        'Blocks of `cva6`: EX is ex_stage without the FPU and the MMU (which sit inside it); '
        '"Other" is the rest of cva6 (commit stage, controller, register files mapped to '
        'LUTRAM, performance counters, glue); it can be slightly negative because '
        'phys_opt_design moves and replicates logic across hierarchy boundaries. BRAM counts 36 Kb blocks (a RAMB18 is half). '
        'The WNS is at the 40 ns constraint, so it only shows how much margin is left; '
        'it is not an Fmax.',
        '',
    ]
    text = '\n'.join(lines)
    if out_path:
        open(out_path, 'w').write(text)
    print(text)


if __name__ == '__main__':
    main(sys.argv)
