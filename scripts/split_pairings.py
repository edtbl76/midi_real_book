#!/usr/bin/env python3
"""
Restructure ensemble directories to be keyed by unique bassist+guitarist pairs.

Usage:
  python3 scripts/split_pairings.py --dry-run   # preview all operations
  python3 scripts/split_pairings.py             # execute
"""
import re
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
PAIRINGS = ROOT / "Work" / "etude_pairings.md"
ENSEMBLES = ROOT / "ensembles"
SKIP_NAMES = {'ensembles.11tydata.js'}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def label_to_dir(label):
    return re.sub(r'\s*/\s*', ' - ', label).strip()


def last_name(full_name):
    return full_name.strip().split()[-1]


def extract_names(field):
    """Parse 'Name (Instrument), Name2' → ['Name', 'Name2']."""
    if not field or field == '—':
        return []
    return [
        re.sub(r'\s*\([^)]+\)', '', part).strip()
        for part in field.split(',')
        if re.sub(r'\s*\([^)]+\)', '', part).strip() not in ('', '—')
    ]


# ---------------------------------------------------------------------------
# Parse etude_pairings.md
# ---------------------------------------------------------------------------

def parse_pairings():
    text = PAIRINGS.read_text(encoding='utf-8')
    pairs = []

    for m in re.finditer(r'^\|\s*\d+\s*\|(.+)$', text, re.MULTILINE):
        fields = [f.strip() for f in m.group(1).split('|')]
        if len(fields) < 11:
            continue

        bassist, g1, g2, g3, g4, labels_str = fields[0:6]
        drummer, keys, other, style = fields[6:10]
        band_influence = fields[10] if len(fields) > 10 else ''

        guitarists = [g for g in [g1, g2, g3, g4] if g and g != '—']
        raw_labels = [l.strip() for l in labels_str.split(';') if l.strip() and l.strip() != '—']
        supporting = extract_names(drummer) + extract_names(keys) + extract_names(other)

        if not guitarists:
            label = raw_labels[0] if raw_labels else '—'
            pairs.append(dict(
                bassist=bassist, guitarist=None, label=label,
                row_guitarists=[], supporting=supporting,
            ))
        else:
            for i, guitarist in enumerate(guitarists):
                label = raw_labels[i] if i < len(raw_labels) else raw_labels[-1]
                pairs.append(dict(
                    bassist=bassist, guitarist=guitarist, label=label,
                    row_guitarists=guitarists, supporting=supporting,
                ))

    return pairs


# ---------------------------------------------------------------------------
# Determine target directory names
# ---------------------------------------------------------------------------

def compute_target_names(pairs):
    label_groups = defaultdict(list)
    for p in pairs:
        label_groups[p['label']].append(p)

    names = []
    for p in pairs:
        group = label_groups[p['label']]
        if len(group) == 1:
            names.append(label_to_dir(p['label']))
        else:
            g_last = last_name(p['guitarist']) if p['guitarist'] else 'none'
            # Disambiguate by guitarist last name first
            same_g = [q for q in group if q is not p and last_name(q['guitarist'] or '') == g_last]
            if same_g:
                b_last = last_name(p['bassist'])
                names.append(label_to_dir(f"{p['label']} - {g_last} ({b_last})"))
            else:
                names.append(label_to_dir(f"{p['label']} - {g_last}"))

    return names


# ---------------------------------------------------------------------------
# Classify clean vs affected
# ---------------------------------------------------------------------------

def classify(pairs, target_names):
    label_count = defaultdict(int)
    for p in pairs:
        label_count[p['label']] += 1

    clean, affected = [], []
    for p, t in zip(pairs, target_names):
        is_clean = (label_count[p['label']] == 1 and len(p['row_guitarists']) <= 1)
        (clean if is_clean else affected).append((p, t))
    return clean, affected


# ---------------------------------------------------------------------------
# Find existing source directory for a label
# ---------------------------------------------------------------------------

def find_source_dir(label):
    norm = label_to_dir(label)
    exact = ENSEMBLES / norm
    if exact.is_dir() and (exact / 'ensemble.md').exists():
        return exact
    # Case-insensitive fallback
    nl = norm.lower()
    for d in ENSEMBLES.iterdir():
        if d.name in SKIP_NAMES:
            continue
        if d.is_dir() and d.name.lower() == nl and (d / 'ensemble.md').exists():
            return d
    return None


# ---------------------------------------------------------------------------
# Markdown content filter — strip player sections not in keep list
# ---------------------------------------------------------------------------

def filter_markdown(content, keep_players):
    system_h2 = {'context', 'players', 'references'}
    keep_lower = {p.lower() for p in keep_players}

    h2_names = re.findall(r'^## (.+)$', content, re.MULTILINE)
    to_remove = [n for n in h2_names if n.lower() not in system_h2 and n.lower() not in keep_lower]

    for name in to_remove:
        # Remove h2 block: ## Name through to next ##
        content = re.sub(rf'\n## {re.escape(name)}\n[\s\S]*?(?=\n## |\Z)', '', content)
        # Remove Players table row
        content = '\n'.join(
            l for l in content.split('\n') if f'[{name}]' not in l
        )

    return content


def make_keep(pair):
    keep = [pair['bassist']]
    if pair['guitarist']:
        keep.append(pair['guitarist'])
    keep.extend(pair['supporting'])
    return keep


# ---------------------------------------------------------------------------
# Build operations — grouped by source directory
# ---------------------------------------------------------------------------

def build_ops(affected):
    # Group all affected pairs by their source directory
    src_to_pairs = defaultdict(list)
    no_src = []

    for p, t in affected:
        src = find_source_dir(p['label'])
        if src:
            src_to_pairs[src].append((p, t))
        else:
            no_src.append((p, t))

    ops = []

    for src, pairs_from_src in src_to_pairs.items():
        # Split into: pairs that keep the source name vs pairs that need a new name
        keep_name = [(p, t) for p, t in pairs_from_src if (ENSEMBLES / t) == src]
        new_name  = [(p, t) for p, t in pairs_from_src if (ENSEMBLES / t) != src]

        # Pairs that keep the source name: EDIT in place (trim wrong players)
        for p, t in keep_name:
            ops.append({'type': 'EDIT', 'src': src, 'dst': src, 'keep': make_keep(p), 'pair': p})

        if not new_name:
            pass  # All pairs keep the name; no renames or deletes needed

        elif len(new_name) == 1 and not keep_name:
            # Exactly one pair needs a new name → RENAME (cheaper than copy+delete)
            p, t = new_name[0]
            ops.append({'type': 'RENAME_EDIT', 'src': src, 'dst': ENSEMBLES / t,
                        'keep': make_keep(p), 'pair': p})

        else:
            # Multiple pairs need new names → COPY each, then DELETE original
            for p, t in new_name:
                ops.append({'type': 'COPY_EDIT', 'src': src, 'dst': ENSEMBLES / t,
                            'keep': make_keep(p), 'pair': p})
            if not keep_name:
                ops.append({'type': 'DELETE', 'src': src})

    for p, t in no_src:
        ops.append({'type': 'MISSING', 'label': p['label'], 'pair': p})

    return ops


# ---------------------------------------------------------------------------
# Execute or preview
# ---------------------------------------------------------------------------

def execute(ops, dry_run):
    copied_srcs = set()

    for op in ops:
        t = op['type']

        if t == 'MISSING':
            p = op['pair']
            print(f"  [WARN] No source dir for label '{op['label']}' "
                  f"({p['bassist']} + {p['guitarist']})")

        elif t == 'EDIT':
            src, keep = op['src'], op['keep']
            print(f"  EDIT    {src.name}")
            print(f"          keep: {keep}")
            if not dry_run:
                md = (src / 'ensemble.md').read_text(encoding='utf-8')
                (src / 'ensemble.md').write_text(filter_markdown(md, keep), encoding='utf-8')

        elif t == 'RENAME_EDIT':
            src, dst, keep = op['src'], op['dst'], op['keep']
            print(f"  RENAME  {src.name}  →  {dst.name}")
            print(f"          keep: {keep}")
            if not dry_run:
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                md = (dst / 'ensemble.md').read_text(encoding='utf-8')
                (dst / 'ensemble.md').write_text(filter_markdown(md, keep), encoding='utf-8')
                shutil.rmtree(src)

        elif t == 'COPY_EDIT':
            src, dst, keep = op['src'], op['dst'], op['keep']
            print(f"  COPY    {src.name}  →  {dst.name}")
            print(f"          keep: {keep}")
            if not dry_run:
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                md = (dst / 'ensemble.md').read_text(encoding='utf-8')
                (dst / 'ensemble.md').write_text(filter_markdown(md, keep), encoding='utf-8')
                copied_srcs.add(src)

        elif t == 'DELETE':
            src = op['src']
            if dry_run or src in copied_srcs:
                print(f"  DELETE  {src.name}")
                if not dry_run:
                    shutil.rmtree(src)
            else:
                print(f"  [SKIP DELETE] {src.name} — copies not yet confirmed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    pairs = parse_pairings()
    target_names = compute_target_names(pairs)
    clean, affected = classify(pairs, target_names)

    print(f"Parsed {len(pairs)} unique bassist+guitarist pairs")
    print(f"  Clean  (no action):  {len(clean)}")
    print(f"  Affected (restructure): {len(affected)}")
    print()

    if args.dry_run:
        print("=== Clean records (untouched) ===")
        for p, t in clean:
            g = p['guitarist'] or '(none)'
            src = find_source_dir(p['label'])
            status = '✓' if src else '? NO DIR'
            print(f"  {status}  {t}  [{p['bassist']} + {g}]")
        print()

    print("=== Operations for affected records ===")
    ops = build_ops(affected)
    execute(ops, dry_run=args.dry_run)

    print()
    if args.dry_run:
        total_new = sum(1 for o in ops if o['type'] in ('COPY_EDIT', 'RENAME_EDIT'))
        total_edit = sum(1 for o in ops if o['type'] == 'EDIT')
        total_del = sum(1 for o in ops if o['type'] == 'DELETE')
        total_warn = sum(1 for o in ops if o['type'] == 'MISSING')
        print(f"Summary: {total_edit} edits, {total_new} copies/renames, "
              f"{total_del} deletes, {total_warn} missing")
        print("[dry-run] No changes made.")
    else:
        print("Done. Run `npm run build` next.")


if __name__ == '__main__':
    main()
