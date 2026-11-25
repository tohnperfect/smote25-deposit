#!/bin/bash
# SMOTE25, the TabPFN arm of the rerun (D43), on the MacBook: all 42 tasks (since v0.24, 14 Nov 2026).
# The cloud's two CPU cores took 24.5 s for one fit of 1,280 rows, about seven hours for the 36 small tasks alone,
# so the whole arm runs here on the Apple GPU: first the 36 tasks of at most 2,308 rows, then the six of at least
# 4,000 rows (smoke detection included), one job per split.
# Run in Terminal:  bash ~/Downloads/SMOTE25/benchmark/SMOTE25_benchmark_run/tabpfn_phase/run_tabpfn_mac.sh
# Needs: the TabPFN-3.5 license accepted at https://platform.priorlabs.ai (Licenses; accepted on 14 Nov 2026) and
# the API key (API Keys page). The script asks for the key and keeps it only in this run's environment; run42.py
# stops TabPFN from copying it to ~/.cache/tabpfn. Safe to rerun after an interruption: finished cells are skipped.
set -euo pipefail
B="$HOME/Downloads/SMOTE25/benchmark/SMOTE25_benchmark_run"
P="$B/tabpfn_phase"
R="$B/rerun42"
[ -d "$R/bench" ] && [ -d "$R/src" ] || { echo "Cannot find $R/bench and $R/src (the rerun bundle of 11 Nov)."; exit 1; }
cd "$P"
# the Python environment: made once; the packages are installed whenever one of them is missing (an install that was
# stopped half-way is completed on the next run)
[ -x venv/bin/python ] || { echo "Making a Python environment in $P/venv"; python3 -m venv venv; }
if ! ./venv/bin/python -c "import numpy, pandas, sklearn, imblearn, joblib, scipy, torch, tabpfn" 2>/dev/null; then
  echo "Installing the Python packages. torch is large: this takes 5 to 15 minutes; let it run."
  ./venv/bin/pip install --upgrade pip
  ./venv/bin/pip install torch "tabpfn==10.0.0" numpy pandas scikit-learn imbalanced-learn joblib scipy
fi
./venv/bin/python -c "import tabpfn, torch; print('tabpfn', tabpfn.__version__, '| torch', torch.__version__, '| Apple GPU (MPS):', torch.backends.mps.is_available())"
# the rerun's own copy of the benchmark, with the TabPFN learner added to run42.py (the only change)
cp "$P/run42.py" "$R/bench/rerun42/scripts/run42.py"
# the check file that marks all 42 tasks available (it exists once the Kaggle file of smoke detection was added)
K="$R/tasks42_check_kaggle.csv"; [ -f "$K" ] || K="$R/tasks42_check.csv"
if [ -z "${TABPFN_TOKEN:-}" ]; then read -r -s -p "TabPFN API key (not stored): " TABPFN_TOKEN; echo; fi
export TABPFN_TOKEN TABPFN_NO_BROWSER=1 SMOTE25_TABPFN_DEVICE="${SMOTE25_TABPFN_DEVICE:-mps}" PYTORCH_ENABLE_MPS_FALLBACK=1
mkdir -p "$P/results_tabpfn_mac"
# cells that failed in an earlier run (for example, out of memory on the GPU) or were cut off are dropped, so that this
# run tries them again; the cells that failed in the last run stay in the results with their error
./venv/bin/python - "$P/results_tabpfn_mac" <<'PY' | tee -a "$P/run_mac.log"
import json, pathlib, sys
dropped = 0
for p in pathlib.Path(sys.argv[1]).glob('*.jsonl'):
    keep = []
    for line in p.read_text().splitlines():
        try:
            x = json.loads(line)
        except json.JSONDecodeError:
            dropped += bool(line.strip())
            continue
        if x.get('status') == 'error':
            dropped += 1
            continue
        keep.append(line)
    p.write_text(''.join(l + '\n' for l in keep))
print(f'== cells dropped to run again (failed or cut off in an earlier run): {dropped}')
PY
run() {
  ./venv/bin/python -I "$R/bench/rerun42/scripts/run42.py" --bench "$R/bench" --src "$R/src" --check "$K" \
    --out "$P/results_tabpfn_mac" --methods none,SMOTE --learners TabPFN --jobs 1 "$@" 2>&1 | tee -a "$P/run_mac.log"
}
echo "== $(date): the 36 tasks of at most 2,308 rows" | tee -a "$P/run_mac.log"
run --max-n 2308
echo "== $(date): the six tasks of at least 4,000 rows, one job per split" | tee -a "$P/run_mac.log"
run --min-n 4000 --split-folds || echo "== the large tasks stopped early (see run_mac.log); rerun the script to resume" | tee -a "$P/run_mac.log"
echo "== $(date): finished" | tee -a "$P/run_mac.log"
unset TABPFN_TOKEN
tar -czf "$P/results_tabpfn_mac.tgz" -C "$P" results_tabpfn_mac run_mac.log
echo "Done. A Claude session can copy $P/results_tabpfn_mac.tgz from here."
