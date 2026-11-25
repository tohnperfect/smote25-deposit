#!/usr/bin/env python3
"""Run one script of the team's Data section (a copy of it) in isolated mode.

python3 -I keeps the current directory and PYTHON* variables out of sys.path; the script's own folder (build/) is
appended at the END of sys.path, so the team's helper modules (analyse_dataset_usage, reconcile_counts) import while
standard-library and installed names still resolve first (checked 12 Nov 2026: no build/ module shadows one).
Usage: python3 -I run_team.py "<copy>/Data section/build/<script>.py" [args...]
"""
import runpy
import sys
from pathlib import Path

script = Path(sys.argv[1]).resolve()
sys.path.append(str(script.parent))
sys.argv = [str(script)] + sys.argv[2:]
runpy.run_path(str(script), run_name='__main__')
