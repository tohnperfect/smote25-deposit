#!/usr/bin/env python3
"""Merge the screeners' decisions of the WP5 harm search into one table and a summary.

Writes harm_search_records.csv (one row per record: bibliographic fields, the queries that found it and every
screening field; team use only, because the quote column copies text of the abstracts), work/summary.json and
work/includes.md (the includes and unsure records with their reasons, for the person who checks).
Stops unless every record of every batch is decided and passes the checks of harm_tools.py.
v0.10: a row of person_overrides.csv (pmid, decision, code, harms, comparison, finding, note; empty fields keep the
screener's value) replaces the AI screener's fields for that record, and the record is marked decided_by
"team correction"; the counts of Section 8.5 regenerate from the result (scripts/search_numbers.py).
Usage: python3 -I scripts/build_results.py
"""
import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harm_tools as T  # noqa: E402

HERE = T.HERE


def main():
    recs = json.load(open(T.RECS, encoding='utf-8'))
    nb = (len(recs) + T.SIZE - 1) // T.SIZE
    rows = []
    for b in range(1, nb + 1):
        part, dec = T.batch(b), T.done(b)
        if len(dec) != len(part):
            sys.exit(f'STOP: batch {b:02d} has {len(dec)} of {len(part)} decisions')
        for row, rec in zip(dec, part):
            errs = T.check_row(row, rec)
            if errs:
                sys.exit(f'STOP: batch {b:02d} PMID {rec["pmid"]}: {errs}')
            rows.append(dict(pmid=rec['pmid'], year=rec['year'], journal=rec['journal'], title=rec['title'],
                             doi=rec['doi'], publication_types='; '.join(rec['publication_types']),
                             queries='+'.join(rec['queries']), batch=f'{b:02d}',
                             **{k: row[k] for k in T.KEYS if k != 'pmid'}, decided_by='AI screener'))
    over = {}
    op = os.path.join(HERE, 'person_overrides.csv')
    if os.path.exists(op):
        for o in csv.DictReader(open(op, encoding='utf-8')):
            if (o.get('pmid') or '').strip():
                over[o['pmid'].strip()] = o
    for r in rows:
        o = over.get(r['pmid'])
        if o:
            for k in ('decision', 'code', 'harms', 'comparison', 'finding'):
                if (o.get(k) or '').strip():
                    r[k] = o[k].strip()
            r['decided_by'] = 'team correction'
    unknown = sorted(set(over) - {r['pmid'] for r in rows})
    if unknown:
        sys.exit(f'STOP: person_overrides.csv names PMIDs not in the records: {unknown}')
    cols = list(rows[0].keys())
    with open(os.path.join(HERE, 'harm_search_records.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    inc = [r for r in rows if r['decision'] == 'include']
    uns = [r for r in rows if r['decision'] == 'unsure']
    summary = {
        'records': len(rows),
        'decision': dict(Counter(r['decision'] for r in rows)),
        'code': dict(Counter(r['code'] for r in rows)),
        'by_query': {q: dict(Counter(r['decision'] for r in rows if q in r['queries'].split('+')))
                     for q in ('H1', 'H2', 'H3', 'H4')},
        'includes_by_harm': dict(Counter(r['code'] for r in inc)),
        'includes_by_finding': {c: dict(Counter(r['finding'] for r in inc if r['code'] == c))
                                for c in sorted({r['code'] for r in inc})},
        'includes_by_comparison': dict(Counter(r['comparison'] for r in inc)),
        'includes_by_data': dict(Counter(r['data'] for r in inc)),
        'harm_measure_reported_without_comparison': dict(Counter(
            h for r in rows if r['code'] == 'X-no-comparison' for h in r['harms'].split(';') if h.strip())),
        'confidence': dict(Counter(r['confidence'] for r in rows)),
        'team_corrections': sum(1 for r in rows if r['decided_by'] == 'team correction'),
    }
    json.dump(summary, open(os.path.join(HERE, 'work', 'summary.json'), 'w', encoding='utf-8'), indent=1)
    with open(os.path.join(HERE, 'work', 'includes.md'), 'w', encoding='utf-8') as fh:
        for title, group in (('Includes', inc), ('Unsure', uns)):
            fh.write(f'## {title} ({len(group)})\n\n')
            for r in sorted(group, key=lambda r: (r['code'], -int(r['year'] or 0))):
                fh.write(f"* **{r['pmid']}** ({r['year']}, {r['journal']}): {r['title']}  \n"
                         f"  {r['code']}; harms {r['harms'] or 'none'}; comparison {r['comparison']}; finding {r['finding']}; "
                         f"data {r['data']}; {r['domain']}; confidence {r['confidence']}.  \n  {r['reason']}\n")
            fh.write('\n')
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
