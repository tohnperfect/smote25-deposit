#!/usr/bin/env python3
"""Workbook for the team's check of the rulings (12 November 2026): the records that rulings B and B2 moved.

Sheets: README (English and Thai: the rulings and how to check); 7_rulings_unsure (the records that fail ruling B or
B2 with medium or low confidence and are now unsure, U-rule-B); 8_rulings_excluded (those that fail with high
confidence and are now excluded under E1); 9_check_task_exclusions (exclusions of the independent AI check whose notes
tie the decision at least partly to a task that ruling C keeps in scope; a session picked them from the check's notes
on 12 November, v0.13, and lists them for the team to decide, without changing them). Each row of sheets 7 and 8
carries the facts the AI pass recorded, its reason and the reasons of the three looks of the screen; since v0.13 the
records that the independent check decided are left out of them, as its decision is final. Rows are in a random order (a hash of seed and record id), as in the earlier
workbook. Decisions come back through person_overrides.csv. Team use only: the abstracts are licensed.
Usage: python3 -I scripts/make_rulings_check.py DRAFT_DIR
Writes data/search/screening_full_2026-11-11/check/SMOTE25_rulings_check_2026-11-12_v2.xlsx (v0.13; the first version,
without sheet 9 and before the check was merged, went out with v0.12) and check/csv/7_rulings_unsure.csv,
check/csv/8_rulings_excluded.csv, check/csv/9_check_task_exclusions.csv
"""
import csv
import gzip
import hashlib
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

csv.field_size_limit(10**9)
R = Path(sys.argv[1])
S = R / 'data/search/screening_full_2026-11-11'
meta = {r['rec']: r for r in csv.DictReader(gzip.open(R / 'data/search/2026-11-11/wp4_records_merged.csv.gz', 'rt', encoding='utf-8'))}
dec = {r['rec']: r for r in csv.DictReader(open(S / 'decisions/screen_decisions.csv', encoding='utf-8'))}
rb = {r['rec']: r for r in csv.DictReader(open(S / 'rule_b/rule_b_decisions.csv', encoding='utf-8'))}
fin = {r['rec']: r for r in csv.DictReader(open(S / 'final/screen_final.csv', encoding='utf-8'))}
third = {}
for f in sorted((S / 'adjudication/out').glob('batch*_screened.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        third[r['rec']] = r
rank = lambda seed, rec: hashlib.sha256(f'{seed}:{rec}'.encode()).hexdigest()
doi = lambda m: f"https://doi.org/{m['doi']}" if m['doi'] else ''
INC = ['I1-new-variant', 'I1-hybrid', 'I1-generative', 'I1-multiclass', 'I1-other']
EXC = ['E1', 'E2', 'E-NOGEN', 'E-REVIEW', 'E-COMPARE', 'E-LANG', 'E-OTHER']


def looks(rec):
    f, t = fin.get(rec, {}), third.get(rec)
    parts = [f"1st: {f.get('first_decision', '')} {f.get('first_code', '')}: {f.get('first_reason', '')}"]
    if f.get('second_decision'):
        parts.append(f"2nd: {f['second_decision']} {f['second_code']}: {f['second_reason']}")
    if t:
        parts.append(f"3rd: {t['decision']} {t['reason_code']}: {t['reason']}")
    return '\n'.join(parts)


COLS = ['rank', 'rec', 'year', 'title', 'abstract', 'venue', 'doi_link', 'ai_decision', 'ai_code', 'ai_ruling', 'ai_facts',
        'ai_confidence', 'ai_reason', 'screen_reasons', 'person_decision', 'person_code', 'checker', 'note']
WID = {'rank': 6, 'rec': 9, 'year': 6, 'title': 40, 'abstract': 70, 'venue': 22, 'doi_link': 22, 'ai_decision': 10,
       'ai_code': 10, 'ai_ruling': 8, 'ai_facts': 30, 'ai_confidence': 10, 'ai_reason': 50, 'screen_reasons': 60,
       'person_decision': 12, 'person_code': 14, 'checker': 8, 'note': 30}
PERSON = {'person_decision', 'person_code', 'checker', 'note'}


def rows_for(final, seed):
    recs = sorted((k for k, r in rb.items() if r['final'] == final and dec[k]['decided_by'].startswith('rulings B and B2')),
                  key=lambda k: rank(seed, k))
    out = []
    for i, k in enumerate(recs, 1):
        m, f = meta[k], rb[k]
        out.append({'rank': i, 'rec': k, 'year': m['year'], 'title': m['title'], 'abstract': m['abstract'] or '[no abstract]',
                    'venue': m['venue'], 'doi_link': doi(m), 'ai_decision': dec[k]['decision'], 'ai_code': dec[k]['code'],
                    'ai_ruling': f['rule'], 'ai_facts': f"scheme {f['scheme']}; generator {f['generator']}; presented "
                    f"{f['presented']}; compared {f['compared']}; task {f['task']}", 'ai_confidence': f['confidence'],
                    'ai_reason': f['reason'], 'screen_reasons': looks(k)})
    return out


s7, s8 = rows_for('unsure', 20261122), rows_for('exclude', 20261123)
# v0.13: exclusions of the independent check whose notes tie the decision at least partly to a task that ruling C keeps
# in scope (segmentation, detection, ranking, zero-shot learning); picked from the notes by a session, for the team
TASK_EXCL = ['R17698', 'R02563', 'R13287', 'R16630', 'R17454', 'R15345', 'R03286', 'R07337']
ret = sorted((S / 'check/returns').glob('RETURN_screen_decisions_*_v3.csv'))
cnote = {r['rec']: r for r in csv.DictReader(open(ret[0], encoding='utf-8-sig'))} if ret else {}
s9 = []
for i, k in enumerate(TASK_EXCL, 1):
    m = meta[k]
    s9.append({'rank': i, 'rec': k, 'year': m['year'], 'title': m['title'], 'abstract': m['abstract'] or '[no abstract]',
               'venue': m['venue'], 'doi_link': doi(m), 'ai_decision': dec[k]['decision'], 'ai_code': dec[k]['code'],
               'ai_ruling': 'C?', 'ai_facts': '', 'ai_confidence': '', 'ai_reason': cnote.get(k, {}).get('note', ''),
               'screen_reasons': looks(k)})
    if dec[k]['decided_by'] != 'independent AI check' or dec[k]['decision'] != 'exclude':
        raise SystemExit(f'STOP: {k} is not an exclusion of the independent check')
(S / 'check/csv').mkdir(parents=True, exist_ok=True)
for name, rows in (('7_rulings_unsure', s7), ('8_rulings_excluded', s8), ('9_check_task_exclusions', s9)):
    with open(S / f'check/csv/{name}.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(rows)

wb = Workbook()
HEAD, FILL, YOU = Font(bold=True, color='FFFFFF'), PatternFill('solid', fgColor='4F4F4F'), PatternFill('solid', fgColor='FFF2CC')


def sheet(name, rows):
    ws = wb.create_sheet(name)
    ws.append(COLS)
    for c in ws[1]:
        c.font, c.fill = HEAD, FILL
        c.alignment = Alignment(wrap_text=True, vertical='top')
    for r in rows:
        ws.append([r.get(c, '') for c in COLS])
    for i, c in enumerate(COLS):
        ws.column_dimensions[ws.cell(1, i + 1).column_letter].width = WID.get(c, 14)
        if c in PERSON:
            for row in ws.iter_rows(min_row=2, min_col=i + 1, max_col=i + 1):
                for cell in row:
                    cell.fill = YOU
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'C2'
    for col, options in (('person_decision', ['include', 'exclude', 'unsure']), ('person_code', INC + EXC)):
        dv = DataValidation(type='list', formula1='"' + ','.join(options) + '"', allow_blank=True)
        letter = ws.cell(1, COLS.index(col) + 1).column_letter
        dv.add(f'{letter}2:{letter}{len(rows) + 1}')
        ws.add_data_validation(dv)
    ws.auto_filter.ref = ws.dimensions


readme = wb.active
readme.title = 'README'
EN = [
    'SMOTE25: the team\'s check of the rulings of the screen. Draft v0.13, 12 November 2026 (version 2 of this workbook; it replaces the one sent with v0.12).',
    'Team use only: the abstracts are licensed (Scopus). Do not share outside the team or deposit.',
    '',
    f'WHY. On 11 and 12 November the team lead narrowed criterion I1 by rulings B, B2 and C (below). AI sessions (Claude Opus 5.5) read',
    f'the {len(rb):,} records that the screen had included and recorded, from title and abstract, whether each method is the paper\'s own;',
    f'a script applied the rulings. Of the records that the independent AI check (another model) did not decide, {len(s8)} fail them with',
    f'  high confidence and are now excluded (sheet 8) and {len(s7)} fail them with medium or low confidence and are now unsure (sheet 7).',
    f'Sheet 9 lists {len(s9)} exclusions of the independent check whose notes tie them at least partly to the task (segmentation, detection,',
    '  ranking, zero-shot learning), which ruling C keeps in scope: decide whether each should be included.',
    'The independent check has also decided the 1,222 records of sheet 1 of SMOTE25_team_check_2026-11-11.xlsx; the authors\' check of',
    '  that sheet still counts and replaces the AI decisions. Your decisions replace the AI\'s, and the paper reports who decided what.',
    '',
    'THE RULINGS (use them also for sheets 1 to 3 of SMOTE25_team_check_2026-11-11.xlsx, whose README predates them)',
    'B.  A chain of existing resampling steps (SMOTE-family oversamplers, undersamplers, cleaners such as Tomek links or ENN, clustering,',
    '    SMOTE inside an existing ensemble, an existing sampler in a latent or PCA space, a choice among existing samplers) counts as the',
    '    paper\'s own method only if the paper presents it as its contribution AND compares it with at least one other way of resampling.',
    'B2. A standard generator used without a stated change (plain GAN, conditional GAN, WGAN-GP, CTGAN, VAE, diffusion model, language',
    '    model, KDE or GMM sampling, copula, standard data augmentation) never counts as the paper\'s own, also when it is chained with',
    '    other steps and compared.',
    'C.  The task does not decide scope: segmentation, regression recast as classes, survival analysis, object detection, continual and',
    '    zero-shot learning and ranking count like classification.',
    'Still the paper\'s own: a new or changed SMOTE variant or oversampler (also an "improved" or newly named one whose change the abstract',
    '  does not describe); a new or modified generative model (a stated change to its architecture, loss, training, conditioning or',
    '  sampling); a multiclass oversampling scheme of its own; a new way of applying SMOTE (for example a search for how much to',
    '  oversample, or a new allocation of synthetic examples).',
    '',
    'HOW. Sheet 7_rulings_unsure (about 1 min each): decide include (with an I1 code) or exclude (E1 when the method is not the paper\'s',
    '  own under B or B2; another code if another criterion fails). Mark unsure only if the full text is needed and you cannot open it.',
    'Sheet 8_rulings_excluded: leave person_decision empty if you agree with the exclusion; write include and a code if you do not.',
    'Sheet 9_check_task_exclusions: as sheet 8; ai_reason holds the note of the independent check.',
    'The columns ai_facts, ai_reason and screen_reasons show what the AI pass and the three looks of the screen recorded.',
    'Work in rank order (any first part is itself a random sample) and write your initials in checker. Send the filled workbook back;',
    'a session copies your decisions into person_overrides.csv and regenerates every count, figure and table of the paper.',
]
TH = [
    '',
    'สรุปภาษาไทย',
    'วันที่ 11 และ 12 พฤศจิกายน หัวหน้าทีมกำหนดหลักเกณฑ์เพิ่มเติม B, B2 และ C ให้เกณฑ์ I1 แคบลง AI (Claude Opus 5.5) อ่านชื่อเรื่องและบทคัดย่อของ',
    f'{len(rb):,} รายการที่ผ่านการคัดกรอง แล้วบันทึกว่าวิธีในแต่ละบทความเป็นวิธีของบทความเองหรือไม่ จากนั้นสคริปต์นำหลักเกณฑ์ไปใช้',
    f'ในรายการที่ AI ตรวจสอบอิสระ (อีกโมเดลหนึ่ง) ไม่ได้ตัดสิน มี {len(s8)} รายการไม่ผ่านหลักเกณฑ์ด้วยความมั่นใจสูงและถูกคัดออก (ชีต 8) อีก {len(s7)} รายการไม่ผ่านด้วยความมั่นใจปานกลางหรือต่ำ จึงเป็น unsure (ชีต 7)',
    f'ชีต 9 คือ {len(s9)} รายการที่ AI ตรวจสอบอิสระคัดออกโดยอ้างถึงประเภทงานบางส่วน (segmentation, detection, ranking, zero-shot) ซึ่งหลักเกณฑ์ C ถือว่าอยู่ในขอบเขต โปรดตัดสินว่าควร include หรือไม่',
    'B: การนำวิธี resampling ที่มีอยู่แล้วมาต่อกัน นับเป็นวิธีของบทความเองก็ต่อเมื่อบทความนำเสนอเป็นผลงานของตน และเปรียบเทียบกับวิธี resampling อื่นอย่างน้อยหนึ่งวิธี',
    'B2: generator มาตรฐานที่ใช้โดยไม่ได้ระบุการเปลี่ยนแปลง (GAN, VAE, diffusion, language model, KDE, GMM, copula, data augmentation มาตรฐาน)',
    'ไม่นับเป็นวิธีของบทความเองเลย แม้จะต่อกับขั้นตอนอื่นและมีการเปรียบเทียบ',
    'C: ประเภทงานไม่เป็นตัวตัดสินขอบเขต เช่น segmentation, regression ที่แปลงเป็นคลาส, survival, object detection นับเหมือน classification',
    'หลักเกณฑ์เหล่านี้ใช้กับการตรวจชีต 1 ถึง 3 ของไฟล์ SMOTE25_team_check_2026-11-11.xlsx ด้วย',
    'ชีต 7: ตัดสิน include (พร้อมรหัส I1) หรือ exclude (E1 ถ้าไม่ใช่วิธีของบทความเองตาม B หรือ B2) ใส่ unsure เฉพาะเมื่อต้องอ่านฉบับเต็มแต่เปิดไม่ได้',
    'ชีต 8 และ 9: ถ้าเห็นด้วยกับการคัดออกให้เว้นว่าง ถ้าไม่เห็นด้วยให้ใส่ include พร้อมรหัส',
    'ทำตามลำดับ rank ใส่ชื่อย่อในคอลัมน์ checker แล้วส่งไฟล์ที่กรอกแล้วกลับมา',
]
for line in EN + TH:
    readme.append([line])
readme.column_dimensions['A'].width = 140
readme['A1'].font = Font(bold=True)
sheet('7_rulings_unsure', s7)
sheet('8_rulings_excluded', s8)
sheet('9_check_task_exclusions', s9)
out = S / 'check/SMOTE25_rulings_check_2026-11-12_v2.xlsx'
wb.save(out)
print(f'wrote {out.relative_to(R)}: 7_rulings_unsure {len(s7)}, 8_rulings_excluded {len(s8)}, 9_check_task_exclusions {len(s9)}')
