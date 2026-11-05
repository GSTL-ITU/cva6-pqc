#!/usr/bin/env python3
"""Core vs SoC area summary of CVA6 on the Nexys Video, from the Vivado
utilization reports of area/area.tcl.

  area_summary.py <report dir> [-o out.md] [--depth N]

Reads soc_util_hier_<stage>.rpt (route if present, else opt), soc_util_<stage>.rpt
for the device capacity, core_util_hier_<stage>.rpt (the core synthesized out of
context) if present, the timing summaries of both, and commit.txt.

The core is the i_ariane instance (cva6: pipeline, register file, MMU, L1
instruction and data caches, AXI adapter). Everything else is the SoC: DDR3
controller (MIG), AXI crossbar and converters, debug module, boot ROM, PLIC,
CLINT, UART, timer, GPIO, SPI, clock generation and reset.
"""

import os
import re
import sys

COLUMNS = [  # key, header
    ('lut', 'LUTs'),
    ('logic', 'LUT as logic'),
    ('lutram', 'LUTRAM'),
    ('srl', 'SRL'),
    ('ff', 'FFs'),
    ('bram', 'BRAM (36 Kb)'),
    ('dsp', 'DSPs'),
]

# rows of the flat report with the device capacity
CAPACITY = {
    'lut': 'Slice LUTs',
    'lutram': 'LUT as Memory',
    'ff': 'Slice Registers',
    'bram': 'Block RAM Tile',
    'dsp': 'DSPs',
}

CORE_INSTANCE = 'i_ariane'


class Node:
    def __init__(self, name, module, depth, values):
        self.name = name
        self.module = module
        self.depth = depth
        self.values = values
        self.children = []


def parse_hier(path):
    """Root Node of the hierarchy in a report_utilization -hierarchical file."""
    header = None
    root = None
    stack = []
    for line in open(path):
        if not line.startswith('|'):
            continue
        cells = line.rstrip('\n').split('|')[1:-1]
        if header is None:
            if cells and cells[0].strip() == 'Instance':
                header = [c.strip() for c in cells]
                idx = {h: i for i, h in enumerate(header)}
            continue
        if len(cells) != len(header):
            continue
        raw = cells[0]
        depth = (len(raw) - len(raw.lstrip(' ')) - 1) // 2
        name = raw.strip()
        get = lambda h: float(cells[idx[h]].strip() or 0) if h in idx else 0.0
        values = {
            'lut': get('Total LUTs'),
            'logic': get('Logic LUTs'),
            'lutram': get('LUTRAMs'),
            'srl': get('SRLs'),
            'ff': get('FFs'),
            'bram': get('RAMB36') + get('RAMB18') / 2,
            'dsp': get('DSP Blocks') or get('DSP48 Blocks'),
        }
        node = Node(name, cells[1].strip(), depth, values)
        while stack and stack[-1].depth >= depth:
            stack.pop()
        # "(name)" rows: logic of the instance itself, already in its totals
        if name.startswith('(') and stack:
            continue
        if stack:
            stack[-1].children.append(node)
        else:
            root = node
        stack.append(node)
    if root is None:
        sys.exit(f'error: no utilization table in {path}')
    return root


def parse_capacity(path):
    """Device name and available resources from a flat report_utilization file."""
    device = '?'
    avail = {}
    for line in open(path):
        m = re.match(r'\|\s*Device\s*:\s*(\S+)', line)
        if m:
            device = m.group(1)
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        for key, label in CAPACITY.items():
            if key not in avail and cells and re.sub(r'\*', '', cells[0]) == label:
                # | Site Type | Used | Fixed | Prohibited | Available | Util% |
                try:
                    avail[key] = float(cells[-2])
                except ValueError:
                    pass
    return device, avail


def parse_wns(path):
    """Setup WNS (ns) from a report_timing_summary file, or None."""
    if not os.path.exists(path):
        return None
    lines = open(path).read().splitlines()
    for i, line in enumerate(lines):
        if line.split()[:2] == ['WNS(ns)', 'TNS(ns)']:
            return float(lines[i + 2].split()[0])
    return None


def label(node):
    """Instance name and module, or only the name for the top ("(top)" module)."""
    return node.name if node.module == '(top)' else f'{node.name} ({node.module})'


def find(node, pred, path=()):
    """First node (depth-first) for which pred(node) is true, with its ancestors."""
    if pred(node):
        return node, path
    for c in node.children:
        r = find(c, pred, path + (node,))
        if r:
            return r
    return None


def sub(a, b):
    return {k: a[k] - b[k] for k in a}


def total(nodes):
    t = {k: 0.0 for k, _ in COLUMNS}
    for n in nodes:
        for k in t:
            t[k] += n.values[k]
    return t


def fmt(v, key):
    if key == 'bram':
        return f'{v:g}'
    return f'{int(round(v)):,}'


def header(extra='share of LUTs'):
    return ['| Block | ' + ' | '.join(h for _, h in COLUMNS) + f' | {extra} |',
            '|---|' + '---:|' * (len(COLUMNS) + 1)]


def row(label, values, ref):
    cells = [fmt(values[k], k) for k, _ in COLUMNS]
    cells.append(f'{100 * values["lut"] / ref["lut"]:.1f}%' if ref['lut'] else '-')
    return '| ' + label + ' | ' + ' | '.join(cells) + ' |'


def subtree(node, ref, depth, max_depth):
    """Rows for the children of node, depth-first, down to max_depth levels."""
    out = []
    if depth > max_depth:
        return out
    pad = '&nbsp;' * (4 * depth)
    for c in sorted(node.children, key=lambda c: -c.values['lut']):
        out.append(row(f'{pad}{label(c)}', c.values, ref))
        out += subtree(c, ref, depth + 1, max_depth)
    if node.children:
        rest = sub(node.values, total(node.children))
        if any(abs(v) > 0.01 for v in rest.values()):
            out.append(row(f'{pad}*other {node.name} logic*', rest, ref))
    return out


def cva6(node):
    """The cva6 instance under an ariane instance (ariane only adds the
    CV-X-IF coprocessor, absent in this configuration), or node itself."""
    r = find(node, lambda n: n.module.startswith('cva6') and n.name == 'i_cva6')
    return r[0] if r else node


def main(argv):
    args = argv[1:]
    out_path = None
    max_depth = 2
    if '-o' in args:
        i = args.index('-o')
        out_path = args[i + 1]
        del args[i:i + 2]
    if '--depth' in args:
        i = args.index('--depth')
        max_depth = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    rdir = args[0]

    stage = 'route' if os.path.exists(f'{rdir}/soc_util_hier_route.rpt') else 'opt'
    root = parse_hier(f'{rdir}/soc_util_hier_{stage}.rpt')
    device, avail = parse_capacity(f'{rdir}/soc_util_{stage}.rpt')
    core_stage = 'route' if os.path.exists(f'{rdir}/core_util_hier_route.rpt') else 'opt'
    ooc_path = f'{rdir}/core_util_hier_{core_stage}.rpt'
    ooc = parse_hier(ooc_path) if os.path.exists(ooc_path) else None
    if ooc is not None:
        # the ariane instance, without the few cells left in cva6_ooc_top itself
        found = find(ooc, lambda n: n.name == CORE_INSTANCE)
        ooc = found[0] if found else ooc
    commit = open(f'{rdir}/commit.txt').read().strip() if os.path.exists(f'{rdir}/commit.txt') else '?'

    found = find(root, lambda n: n.name == CORE_INSTANCE)
    if not found:
        sys.exit(f'error: no {CORE_INSTANCE} instance in the SoC report')
    core, ancestors = found
    soc_only = sub(root.values, core.values)
    mig = find(root, lambda n: n.module.startswith('xlnx_mig_7_ddr3'))
    stage_text = {'opt': 'after synthesis and opt_design',
                  'route': 'after place and route'}

    lines = ['# CVA6 FPGA area: core vs SoC', '',
             f'Device {device}, RTL at commit `{commit}`, target `cv32a6_ima_sv32_fpga`, '
             f'25 MHz core clock. Whole design {stage_text[stage]} (the bitstream flow, '
             f'`make fpga`); core alone {stage_text[core_stage]}.', '']
    timing = [(n, parse_wns(f'{rdir}/{p}_timing_route.rpt')) for n, p in
              (('whole design', 'soc'), ('core alone', 'core'))]
    timing = [f'{n} {w:+.3f} ns' for n, w in timing if w is not None]
    if timing:
        lines += ['Setup WNS: ' + ', '.join(timing) + '.', '']
    lines += ['## Summary', '']
    lines += header('share of device LUTs')
    dev = {'lut': avail.get('lut', 0)}
    lines.append(row(f'**Whole design** (`{root.name}`)', root.values, dev))
    lines.append(row(f'**Core** in the SoC (`{core.name}`)', core.values, dev))
    if ooc is not None:
        lines.append(row('**Core** alone (out of context)', ooc.values, dev))
    lines.append(row('**SoC without core**', soc_only, dev))
    if mig:
        lines.append(row('**SoC without core and DDR3 controller**',
                         sub(soc_only, mig[0].values), dev))
    lines.append('')
    lines.append('Device usage of the whole design: ' + ', '.join(
        f'{h} {100 * root.values[k] / avail[k]:.1f}% (of {fmt(avail[k], k)})'
        for k, h in COLUMNS if avail.get(k)) + '.')
    lines.append('')

    lines += ['## Core breakdown', '',
              f'`{"/".join(a.name for a in ancestors + (core,))}` in the SoC, '
              'largest blocks first; "share" is the part of the core\'s LUTs.', '']
    lines += header()
    lines.append(row(f'**Core** ({core.module})', core.values, core.values))
    lines += subtree(cva6(core), core.values, 1, max_depth)
    lines.append('')

    lines += ['## SoC breakdown', '', '"share" is the part of the whole design\'s LUTs.', '']
    lines += header()
    lines.append(row(f'**Whole design** ({label(root)})', root.values, root.values))
    # every block on the path down to the core, the core included
    listed = []
    for parent in ancestors:
        for c in sorted(parent.children, key=lambda c: -c.values['lut']):
            if c not in ancestors:
                lines.append(row(f'&nbsp;&nbsp;&nbsp;&nbsp;{label(c)}', c.values, root.values))
                listed.append(c)
    glue = sub(root.values, total(listed))
    if any(abs(v) > 0.01 for v in glue.values()):
        lines.append(row('&nbsp;&nbsp;&nbsp;&nbsp;*flattened into the top: boot ROM, DPTI controller '
                         'and FIFOs, clock and reset*',
                         glue, root.values))
    lines.append('')

    if ooc is not None:
        lines += ['## Core alone (out of context)', '',
                  f'Numbers {stage_text[core_stage]}. `area/cva6_ooc_top.sv`: the same '
                  '`ariane` instance and configuration as in `ariane_xilinx`, synthesized as '
                  'the top with `-mode out_of_context` (no I/O buffers; nothing outside the '
                  'core can optimize or absorb its logic). The RVFI trace port is left open, '
                  'as it only feeds SoC-side tracing blocks.', '']
        lines += header()
        lines.append(row('**Core** (ariane)', ooc.values, ooc.values))
        lines += subtree(cva6(ooc), ooc.values, 1, max_depth)
        lines.append('')

    lines += [
        'BRAM counts 36 Kb blocks (a RAMB18 is half). "LUTs" is LUT as logic + LUTRAM + SRL.',
        'Small modules that Vivado flattens into their parent show up in the "other" rows.',
        'After place and route these rows can be slightly negative: phys_opt_design moves',
        'and replicates logic across hierarchy boundaries.',
        '',
    ]
    text = '\n'.join(lines)
    if out_path:
        open(out_path, 'w').write(text)
    print(text)


if __name__ == '__main__':
    main(sys.argv)
