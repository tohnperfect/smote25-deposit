#!/usr/bin/env python3
"""Build an offline copy of the page "SMOTE25 Final Pass": one HTML file that runs in a browser without a network,
keeps the reader's decisions in that browser and exports the same CSV as the online page (13 November 2026).

Usage: python3 -I scripts/build_final_pass_offline.py <records.json> <template.html> <out.html> <date> [decided.csv ...]
                                                    [--new-since <older records.json>]
With --new-since, only the passages whose text is not in the older page are kept (an addendum to an earlier copy).
The passages decided in the CSV exports given (online page or earlier offline copies) are left out.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

argv = sys.argv[1:]
older = None
if '--new-since' in argv:
    k = argv.index('--new-since')
    older = Path(argv[k + 1])
    del argv[k:k + 2]
rec, tpl, out, date = Path(argv[0]), Path(argv[1]), Path(argv[2]), argv[3]
data = json.loads(rec.read_text(encoding='utf-8'))
decided = {}
for p in argv[4:]:
    with open(p, newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['decision'] in ('approve', 'revise'):
                decided[r['passage_id']] = r['decision']
items = [i for i in data['items'] if i['id'] not in decided]
if older:
    seen = {i['text'] for i in json.loads(older.read_text(encoding='utf-8'))['items']}
    items = [i for i in items if i['text'] not in seen]
known = {i['id'] for i in data['items']}
if not older:
    assert set(decided) <= known, sorted(set(decided) - known)
n_ok = sum(1 for v in decided.values() if v == 'approve')
n_rev = len(decided) - n_ok
build_id = hashlib.sha1(('|'.join(i['id'] for i in items) + date).encode()).hexdigest()[:12]
payload = {
    'build_id': build_id,
    'subtitle': ((f"Offline addendum made {date} from draft {data['draft']}: the {len(items)} passages that are new since the "
                  f"offline copy of the earlier page (parts of the abstract and two table notes that the earlier page missed, and "
                  f"the passage redrafted at your request). Decide them here; the earlier offline copy keeps its own decisions.")
                 if older else
                 (f"Offline copy made {date} from draft {data['draft']}: the {len(items)} passages still waiting for "
                  f"approval. Everything decided earlier, online or offline, is merged into this draft and left out; "
                  f"redrafts, answers to your questions and cut text are marked.")
                 if not decided else
                 (f"Offline copy made {date} from draft {data['draft']}: the {len(items)} passages that a session wrote "
                  f"(tags S and R, and one E paragraph with an M7 edit) and that were not yet decided. The {len(decided)} "
                  f"passages decided on the online page are left out ({n_ok} approved, {n_rev} to revise).")),
    'note': (f"Built {date} from {rec.name} of draft {data['draft']} ({len(items)} of {data['n']} passages; build "
             f"{build_id}). The file holds the unpublished text of the paper: keep it within the team."),
    'items': items,
}
text = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')
html = tpl.read_text(encoding='utf-8')
assert html.count('__DATA__') == 1
out.write_text(html.replace('__DATA__', text), encoding='utf-8')
print(json.dumps({'passages': len(items), 'left_out': len(decided), 'approved': n_ok, 'revise': n_rev,
                  'm7_left': sum(1 for i in items if i['m7']), 'build_id': build_id, 'bytes': out.stat().st_size}))
