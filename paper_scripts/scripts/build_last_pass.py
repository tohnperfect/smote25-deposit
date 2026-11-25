#!/usr/bin/env python3
"""Build records.json of the page "SMOTE25 Last Pass" (16 November 2026): everything the paper still needs from a
person, on one page, for the team lead's last pass. Parts:
  decisions    the choices only the authors can make (scope of the two large blind checks, names in the deposit,
               the approval of the final version, prior publication, a preprint, the note after the abstract)
  statements   the two statements of JAIR's submission form (importance; closest JAIR papers), drafted from the
               draft of v0.1 (claude/smote25-jair-readiness-v0.1.md) and updated to the current paper
  passages     the passages of the page "SMOTE25 Final Pass" (team/final_pass/records.json; same ids, so the
               decisions merge with scripts/merge_final_pass.py)
  samples      the 82 items of the page "SMOTE25 Samples Check, round 2" (build_d42_check.py --round2; same ids
               and keys, so the decisions merge with scripts/merge_d42_check.py --round2)
  validations  the five one-page validation summaries (benchmark/rerun42/methods/VALIDATION_SUMMARIES.md, D40)
  big          the two large blind checks, which stay on their own pages (Screen Check, D27; Section 8 Check, D41)
  notes        what happens to each team note of the draft
Usage: python3 -I scripts/build_last_pass.py <draft_dir> <samples records.json> <out_dir>
Writes out_dir/records.json (it repeats the samples' short quotes: team use only, never deposited).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

V, SAMPLES, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])


def words(t):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.,%-]*", t))


fp = json.load(open(V / 'team/final_pass/records.json', encoding='utf-8'))
passages = [dict(id=p['id'], where=p['where'], kind=p['kind'], text=p['text'], context=p.get('context', ''),
                 file=p['file']) for p in fp['items']]
sm = json.load(open(SAMPLES, encoding='utf-8'))
assert all(i['key'].startswith('r2_') for i in sm['items']), 'STOP: the samples are not those of round 2'
samples = sm['items']

# the validation summaries, one card per method (Markdown to HTML with pandoc; our own text)
md = (V / 'benchmark/rerun42/methods/VALIDATION_SUMMARIES.md').read_text(encoding='utf-8')
md = re.sub(r'^---\n.*?\n---\n', '', md, flags=re.S)
parts = re.split(r'(?m)^# ', md)
intro, validations = '', []
for p in parts:
    if not p.strip():
        continue
    title, body = p.split('\n', 1)
    body = re.sub(r'(?m)^\\newpage\s*$', '', body)
    body = re.sub(r'(?m)^Read: \[ \]\s+Questions:\s*$', '', body)
    html = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'html'], input=body, capture_output=True, text=True,
                          check=True).stdout
    if title.startswith('How to read'):
        intro = html.replace('tick it and add any question; M1 moves to fixed once all five are ticked (D40)',
                             'mark it Accept, or Question with what you want checked; M1 is fixed once all five are '
                             'accepted (D40)')
        continue
    key = re.sub(r'[^a-z0-9]', '', title.split('(')[0].lower())
    validations.append(dict(id='v_' + key, title=title.strip(), html=html))
assert len(validations) == 5, [v['title'] for v in validations]

# the explanation after the abstract (a team note in main.tex), shown in full
main = (V / 'main.tex').read_text(encoding='utf-8')
m = re.search(r'\\team\{Explanation asked for in the final pass \(remove once read\)\. (.*?)\}\n', main, re.S)
explanation = re.sub(r'\s+', ' ', m.group(1)) if m else ''
# labels as the preview numbers them (main.aux)
LAB = dict(re.findall(r'\\newlabel\{([^}]*)\}\{\{([^}]*)\}', (V / 'main.aux').read_text(encoding='utf-8', errors='replace')))
explanation = re.sub(r'\\ref\{([^}]*)\}', lambda x: LAB.get(x.group(1), '?'), explanation)
explanation = explanation.replace("``", '"').replace("''", '"').replace('~', ' ')
explanation = re.sub(r'\\(emph|textit|textbf)\{([^}]*)\}', r'\2', explanation)

decisions = [
    dict(id='d_screen', title="The authors' check of the screen (D27)",
         text="On 12 November the authors decided to check all five queues of the page \"SMOTE25 Screen Check\" "
              "before the final merge: 3,902 records. Nobody has started. Any record an author changes is changed "
              "in every count; a record nobody checks keeps the AI screen's decision. In every case the 383 records "
              "still unsure are excluded at the final merge (D28), unless an author includes them. Section 3.4 and "
              "the declarations will say exactly what the authors checked.",
         options=[dict(k='all', label='All five queues, 3,902 records, as decided',
                       detail='About 15 to 20 hours; the four authors can share it on that page.'),
                  dict(k='blind', label='The blind sample only, 600 records',
                       detail="About 2 to 3 hours: the page's first queue, 300 records the AI screen included and 300 "
                              "it excluded, shown without its decision. Section 3.4 then reports the authors' "
                              "agreement with the AI screen."),
                  dict(k='none', label='No record-by-record check',
                       detail='Section 3.4 reports the AI screen in three looks and the independent check by another '
                              'model (97.1% agreement on 596 records), and says that the authors did not check the '
                              'screen record by record.')]),
    dict(id='d_sec8', title='The checks of Section 8 (D41)',
         text="An author was to check three AI first passes blind on the page \"SMOTE25 Section 8 Check\": the harm "
              "search behind Section 8.5 and its four harms (126 records), the case search behind Section 8.4 (204 "
              "records) and the reach tags behind Section 8.1 (30 works). Nobody has started.",
         options=[dict(k='all', label='All three, 360 items, as decided', detail='About 3 to 4 hours.'),
                  dict(k='harm', label='The harm search only, 126 records',
                       detail='About 2 hours; the four harms of the abstract rest on it. The case search and the reach '
                              'tags stay reported as AI first passes.'),
                  dict(k='none', label='None',
                       detail='Sections 8.1, 8.4 and 8.5 stay reported as AI first passes, as they are now.')]),
    dict(id='d_names', title='Names in the deposited check records',
         text="The deposit (Zenodo and GitHub, at submission) is to hold the records of the authors' checks: the "
              "summaries and exports of the spot checks of WP3 and D42, and now the log of the library PDFs, whose "
              "notes name team members (for example \"Supawit: found\"). The paper itself says \"an author\" (D51).",
         options=[dict(k='keep', label='Deposit them as they are, names included', detail=''),
                  dict(k='anon', label='Deposit them with each name replaced by "an author"', detail=''),
                  dict(k='out', label='Leave these records out of the deposit', detail='')]),
    dict(id='d_final', title="The authors' approval of the final version (D47)",
         text='The declarations need the sentence "All authors approved the final version." It must be true when the '
              'paper is submitted.',
         options=[dict(k='now', label='Write it now; I will have all four approve before submitting', detail=''),
                  dict(k='later', label='Wait; I will tell you when all four have approved', detail='')]),
    dict(id='d_prior', title='Prior publication',
         text="JAIR's submission form asks about prior publication. The draft answer is \"No\": no part of this survey "
              "has been published or is under review elsewhere, and none was deposited as a thesis chapter. Only an "
              "author can confirm it.",
         options=[dict(k='none', label='Confirmed: none of this', detail=''),
                  dict(k='some', label='Some part was (say which in the note)', detail='')]),
    dict(id='d_arxiv', title='A preprint on arXiv',
         text="Under D53 the deposit's README asks readers to cite the paper's arXiv preprint and, once it is out, the "
              "journal paper. The README and the answer on prior publication depend on whether there will be a "
              "preprint.",
         options=[dict(k='yes', label='A preprint at submission', detail='I prepare the files; an author submits them '
                       'to arXiv and tells me its identifier.'),
                  dict(k='no', label='No preprint', detail='The README cites the journal paper once it is out.'),
                  dict(k='later', label='Decide later', detail='')]),
    dict(id='d_explain', title='The explanation after the abstract',
         text='You asked for this explanation in the final pass; its note says to remove it once read. It reads: '
              + explanation,
         options=[dict(k='remove', label='Read; remove it', detail=''),
                  dict(k='keep', label='Keep it for now', detail='')]),
]
assert explanation, 'STOP: the explanation note was not found in main.tex'

statements = [
    dict(id='s_importance', title='Importance (JAIR submission form, at most 150 words)', limit=150,
         text="SMOTE, published in JAIR in 2002, is among the most used methods in applied machine learning: more "
              "than 34,000 indexed works cite it, half of them outside computer science. Yet practitioners cannot tell "
              "which of its many variants to use, and researchers cannot tell which reported gains are real. This "
              "survey gives both groups tools. A six-decision template describes any interpolation oversampler and "
              "shows what 37 methods change. An audit of 1,756 dataset entries, 1,511 published comparisons and the "
              "evaluation design of 71 studies shows where reported wins come from, and a rerun on 42 reference tasks "
              "finds the variants on par with SMOTE. A systematic search tests how far these findings reach, an audit "
              "of 300 applications shows how SMOTE is used, and the independent evidence since 2018 shows when "
              "oversampling helps and when it harms."),
    dict(id='s_closest', title='The closest JAIR papers and the difference (at most 150 words)', limit=150,
         text="(1) Chawla et al. (2002), JAIR 16, proposed SMOTE. (2) Fernández et al. (2018), JAIR 61, cataloged "
              "more than 85 extensions at fifteen years by seven properties of their design and set out open "
              "challenges. Our survey differs in what it analyzes. It fixes the family by a definition and codes each "
              "method by the decisions it changes; it audits the data and the evaluation behind the published claims "
              "and reruns the variants on 42 reference tasks, which neither earlier paper did; it tests the coverage "
              "of its corpus against a systematic search; it brings in the independent benchmarks, theory and "
              "clinical evidence published since 2018; and it asks whom the technique reached and with what "
              "documented benefit and harm. (3) Wilson and Martinez (1997), JAIR 6, supplies the HVDM distance we use "
              "to measure data difficulty."),
]
for s in statements:
    s['words'] = words(s['text'])
    assert s['words'] <= s['limit'], (s['id'], s['words'])

big = [
    dict(id='b_screen', decision='d_screen', title='SMOTE25 Screen Check (D27)',
         url='https://claude.ai/artifact/2sLYYPqeUAZQc8RJZsEnUj',
         text='Five queues: the blind sample (600), the unsure records (383), the rulings exclusions (116), the '
              'coverage sample (120) and all includes (3,096 in a random order); 3,902 records in all. The page keeps '
              'every decision under your name and shows the AI decision of a blind record only after you decide.',
         todo={'all': 'Do all five queues; share the page with the co-authors by name (Editor) to split them.',
               'blind': 'Do the first queue, "Blind sample", 600 records. Leave the other queues.',
               'none': 'Nothing to do on that page.'}),
    dict(id='b_sec8', decision='d_sec8', title='SMOTE25 Section 8 Check (D41)',
         url='https://claude.ai/artifact/HjMSn5vUbPRoAbfU5vfPrJ',
         text='Three tabs: harm search (126), case search (204), reach tags (30). Blind: the AI coding of a record '
              'appears only after you save your decision. The How-to tab states each rule.',
         todo={'all': 'Do all three tabs.', 'harm': 'Do the tab "Harm search", 126 records. Leave the other two.',
               'none': 'Nothing to do on that page.'}),
]

notes = [
    ('After the abstract', 'The explanation you asked for in the final pass', 'Decisions: read and remove'),
    ('Section 2, Table 2', 'Three reviews still to read in full and two 2025 reviews to add (D44)',
     'Claude, from the five PDFs the team saved in related_work_d44/; nothing needed from you'),
    ('Section 3.4', "The authors' check of the screen (D27) and the final merge (D28)",
     'Decisions: the scope of the screen check; then the Screen Check page'),
    ('Section 3.4', 'The check of round 2 of D42 is pending', 'Samples check, here'),
    ('Section 8.1', 'The reach counts and the check of the reach tags', 'Decisions: the scope of the Section 8 checks'),
    ('Section 8.4', 'The check of the case search', 'Decisions: the scope of the Section 8 checks'),
    ('Section 8.5', 'The check of the harm search', 'Decisions: the scope of the Section 8 checks'),
    ('Section 9.2', 'The five validation summaries (D40, M1)', 'Validations, here'),
    ('Section 9.4', 'Final pass of the position (approved on 14 November)', 'Claude removes it; nothing needed'),
    ('Declarations', 'What the authors checked, in the use of AI', 'Written from your decisions and checks'),
    ('Declarations', 'The deposit and its DOI', 'Claude, when the bundle is built; publishing waits for your approval at that moment'),
    ('Declarations', 'All authors approved the final version (D47)', 'Decisions'),
    ('Checklist', 'Answers that turn "yes" once the deposit is made', 'Claude, with the deposit'),
]
after = [
    'Merge your decisions: the passages and statements (approved text tagged A; a revision redrafted from your note), '
    'the samples check (into the D42 adjudication; the counts regenerate), the validations (M1) and the decisions.',
    'If you chose to run the large checks: merge them from their pages, report what the authors checked in Sections '
    '3.4 and 8 and in the declarations, and regenerate every count.',
    'The final merge (D28): the records still unsure leave the screen, and the coverage sample takes the next records '
    'in rank order; the team will obtain no more papers, so a newcomer without a full text counts as not obtained, and '
    'the 12 reserves with a full text are coded and checked as before.',
    'Table 2 (D44): read the five related-work papers the team saved and add the two reviews of 2025.',
    'Remove every team note, rebuild, recheck every number, and send you any new sentence (for example the one that '
    'reports your checks) for a short final approval.',
    'Build the deposit (Zenodo and GitHub) and the reproducibility checklist; publishing the Zenodo record and making '
    'the repository public wait for your approval at that moment.',
]
data = dict(
    meta=dict(title='SMOTE25 Last Pass', built='16 November 2026', draft='v0.37',
              counts=dict(decisions=len(decisions), statements=len(statements), passages=len(passages),
                          samples=len(samples), validations=len(validations))),
    decisions=decisions, statements=statements, passages=passages, samples=samples, validations=validations,
    validation_intro=intro, big=big, notes=[dict(where=a, what=b, how=c) for a, b, c in notes], after=after)
ids = [x['id'] for k in ('decisions', 'statements', 'passages', 'samples', 'validations') for x in data[k]]
assert len(ids) == len(set(ids)), 'STOP: duplicate ids'
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'records.json').write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding='utf-8')
print(json.dumps(dict(data['meta']['counts'], statements_words=[s['words'] for s in statements],
                      bytes=(OUT / 'records.json').stat().st_size)))
