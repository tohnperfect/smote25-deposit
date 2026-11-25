#!/usr/bin/env python3
"""Rerun the two model scripts of the Data section at full precision (12 November 2026).

The Data section's scripts round odds ratios and their limits to three decimals before writing them, and the paper prints
two. Rounding twice can move the second decimal: an odds ratio of 1.2145 is written as 1.215 and then printed as 1.22,
where one rounding gives 1.21. This tool copies a Data section into a scratch folder, changes only the number of
decimals of the round() calls of build/hypotheses.py and build/difficulty_outcomes.py (three or four decimals become
six; the percentages of win shares, one decimal, become five), reruns the two scripts there with run_team.py, and
checks that every value of the full-precision outputs rounds back to the value the unchanged scripts wrote (so the
change touches the rounding and nothing else). It writes the two outputs to <out_dir>/full_precision/.
scripts/gen_model_variants.py reads them when they are present, and the paper rounds once, from them.

Usage: python3 -I full_precision.py "<copy>/Data section" <out_dir>
  <copy> is a Data section whose out/ holds the outputs of the unchanged scripts (for D35: the patched copy, after the
  rerun of data/d35/README.md step 3). The copy itself is not changed.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
RUNNER = Path(__file__).resolve().parent / 'run_team.py'
SCRIPTS = {
    'hypotheses.py': [(r'round\(100 \* k / n, 1\)', 'round(100 * k / n, 5)', 1),
                      (r'round\(100 \* lo, 1\), round\(100 \* hi, 1\)', 'round(100 * lo, 5), round(100 * hi, 5)', 1),
                      (r', 3\)', ', 6)', None), (r', 4\)', ', 6)', None)],
    'difficulty_outcomes.py': [(r', 3\)', ', 6)', None), (r', 4\)\)', ', 6))', None)],
}
OUTPUTS = {'hypotheses.py': 'hypotheses.json', 'difficulty_outcomes.py': 'difficulty_outcomes.json'}


def leaves(o, path=()):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, path + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, path + (i,))
    else:
        yield path, o


def get(o, path):
    for k in path:
        o = o[k]
    return o


def decimals(x):
    s = repr(x)
    return len(s.split('.')[1]) if '.' in s and 'e' not in s else 0


def main():
    tmp = Path(tempfile.mkdtemp(prefix='fullprec_'))
    work = tmp / 'Data section'
    shutil.copytree(SRC, work)
    (OUT / 'full_precision').mkdir(parents=True, exist_ok=True)
    report = {}
    for script, subs in SCRIPTS.items():
        f = work / 'build' / script
        t = f.read_text(encoding='utf-8')
        for pat, rep, expect in subs:
            t, n = re.subn(pat, rep, t)
            if expect is not None and n != expect:
                raise SystemExit(f'STOP: {script}: {pat} replaced {n} times, expected {expect}')
        f.write_text(t, encoding='utf-8')
        r = subprocess.run([sys.executable, '-I', str(RUNNER), str(f)], cwd=tmp, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f'STOP: {script} failed:\n{r.stderr[-2000:]}')
        full = json.loads((work / 'out' / OUTPUTS[script]).read_text(encoding='utf-8'))
        orig = json.loads((SRC / 'out' / OUTPUTS[script]).read_text(encoding='utf-8'))
        checked = 0
        for path, v in leaves(orig):
            if isinstance(v, float):
                w = get(full, path)
                d = decimals(v)
                # the unchanged script rounded the same number to d (or more) decimals, so the full value lies within
                # half a unit of the stored value's last decimal
                if abs(w - v) > 0.5 * 10 ** -d + 1e-9:
                    raise SystemExit(f'STOP: {OUTPUTS[script]} {path}: full {w} does not round to {v}')
                checked += 1
        shutil.copy2(work / 'out' / OUTPUTS[script], OUT / 'full_precision' / OUTPUTS[script])
        report[OUTPUTS[script]] = checked
    shutil.rmtree(tmp)
    print(json.dumps({'source': str(SRC), 'written': str(OUT / 'full_precision'), 'values_checked': report}, indent=1))


if __name__ == '__main__':
    main()
