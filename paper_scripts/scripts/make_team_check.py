#!/usr/bin/env python3
"""Workbook for the team's check of the AI work of WP4 and WP5 (11 November 2026): what to check, and how.

Sheets: README (English and Thai); 1_unsure (every record the screen left unsure); 2_includes and 3_exclusions (a
random 300 of each, for the agreement of the authors with the AI screen); 4_coverage_codes and 5_useaudit_codes (the AI
codes of the two samples, to confirm or correct); 6_pdf_downloads (the papers the samples still need); codes (legend).
Random draws use a hash of (seed, record id), as the samples do. Team use only: the abstracts are licensed.
Usage: python3 -I scripts/make_team_check.py DRAFT_DIR
Writes data/search/screening_full_2026-11-11/check/SMOTE25_team_check_2026-11-11.xlsx
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
dec = list(csv.DictReader(open(S / 'decisions/screen_decisions.csv', encoding='utf-8')))
fin = {r['rec']: r for r in csv.DictReader(open(S / 'final/screen_final.csv', encoding='utf-8'))}
third = {}
for f in sorted((S / 'adjudication/out').glob('batch*_screened.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        third[r['rec']] = r
rank = lambda seed, rec: hashlib.sha256(f'{seed}:{rec}'.encode()).hexdigest()
doi = lambda m: f"https://doi.org/{m['doi']}" if m['doi'] else ''

INC = ['I1-new-variant', 'I1-hybrid', 'I1-generative', 'I1-multiclass', 'I1-other']
EXC = ['E1', 'E2', 'E-NOGEN', 'E-REVIEW', 'E-COMPARE', 'E-LANG', 'E-OTHER']
wb = Workbook()
HEAD = Font(bold=True, color='FFFFFF')
FILL = PatternFill('solid', fgColor='4F4F4F')
YOU = PatternFill('solid', fgColor='FFF2CC')


def sheet(name, cols, rows, widths, person_cols, validations=()):
    ws = wb.create_sheet(name)
    ws.append(cols)
    for c in ws[1]:
        c.font, c.fill = HEAD, FILL
        c.alignment = Alignment(wrap_text=True, vertical='top')
    for r in rows:
        ws.append([r.get(c, '') for c in cols])
    for i, c in enumerate(cols):
        ws.column_dimensions[ws.cell(1, i + 1).column_letter].width = widths.get(c, 14)
        if c in person_cols:
            for row in ws.iter_rows(min_row=2, min_col=i + 1, max_col=i + 1):
                for cell in row:
                    cell.fill = YOU
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'C2'
    for col, options in validations:
        dv = DataValidation(type='list', formula1='"' + ','.join(options) + '"', allow_blank=True)
        letter = ws.cell(1, cols.index(col) + 1).column_letter
        dv.add(f'{letter}2:{letter}{len(rows) + 1}')
        ws.add_data_validation(dv)
    ws.auto_filter.ref = ws.dimensions
    return ws


def reasons(rec):
    f, t = fin.get(rec, {}), third.get(rec)
    parts = [f"1st: {f.get('first_decision', '')} {f.get('first_code', '')}: {f.get('first_reason', '')}"]
    if f.get('second_decision'):
        parts.append(f"2nd: {f['second_decision']} {f['second_code']}: {f['second_reason']}")
    if t:
        parts.append(f"3rd: {t['decision']} {t['reason_code']}: {t['reason']}")
    return '\n'.join(parts)


SCR_COLS = ['rank', 'rec', 'year', 'title', 'abstract', 'venue', 'doi_link', 'ai_decision', 'ai_code', 'ai_reasons',
            'person_decision', 'person_code', 'checker', 'note']
SCR_W = {'rank': 6, 'rec': 9, 'year': 6, 'title': 40, 'abstract': 70, 'venue': 22, 'doi_link': 22, 'ai_decision': 10,
         'ai_code': 14, 'ai_reasons': 60, 'person_decision': 12, 'person_code': 14, 'checker': 8, 'note': 30}
VAL = [('person_decision', ['include', 'exclude', 'unsure']), ('person_code', INC + EXC)]


def scr_rows(recs, seed):
    out = []
    for i, r in enumerate(sorted(recs, key=lambda r: rank(seed, r['rec'])), 1):
        m = meta[r['rec']]
        out.append({'rank': i, 'rec': r['rec'], 'year': r['year'], 'title': m['title'], 'abstract': m['abstract'] or '[no abstract]',
                    'venue': m['venue'], 'doi_link': doi(m), 'ai_decision': r['decision'], 'ai_code': r['code'],
                    'ai_reasons': reasons(r['rec'])})
    return out


uns = [r for r in dec if r['decision'] == 'unsure']
inc = sorted([r for r in dec if r['decision'] == 'include'], key=lambda r: rank(20261118, r['rec']))[:300]
exc = sorted([r for r in dec if r['decision'] == 'exclude'], key=lambda r: rank(20261119, r['rec']))[:300]
s1 = scr_rows(uns, 20261121)
s2 = scr_rows(inc, 20261118)
s3 = scr_rows(exc, 20261119)

COV_AI = ['fulltext_ok', 'eligible', 'exclusion', 'label', 'generator', 'S', 'A', 'N', 'P', 'F', 'L', 'class', 'modality',
          'n_datasets', 'vs_smote', 'vs_none', 'vs_cost', 'measures', 'protocol', 'inside_folds', 'tuning', 'stat_test', 'code',
          'evidence', 'note', 'confidence']
cov_log = {r['rec']: r for r in csv.DictReader(open(S / 'coverage/fetch_log.csv', encoding='utf-8'))}
cov_rows = []
for r in csv.DictReader(open(S / 'coverage/coded.csv', encoding='utf-8')):
    m = meta[r['rec']]
    row = {'rec': r['rec'], 'year': m['year'], 'title': m['title'], 'doi_link': doi(m), 'open_copy': cov_log.get(r['rec'], {}).get('url', '')}
    row.update({'ai_' + k: r[k] for k in COV_AI})
    cov_rows.append(row)
COV_COLS = ['rec', 'year', 'title', 'doi_link', 'open_copy'] + ['ai_' + k for k in COV_AI] + ['person_agrees', 'person_corrections', 'checker', 'note']

USE_AI = ['source', 'is_application', 'domain', 'task', 'stakes', 'modality', 'resampler', 'learner', 'inside_folds', 'vs_none',
          'vs_weights', 'measures', 'calibration', 'validation', 'test_balanced', 'evidence', 'note', 'confidence']
use_log = {r['rec']: r for r in csv.DictReader(open(S / 'useaudit/fetch_log.csv', encoding='utf-8'))}
use_all = list(csv.DictReader(open(S / 'useaudit/coded.csv', encoding='utf-8')))
ft = [r for r in use_all if r['source'] == 'fulltext']
ab = sorted([r for r in use_all if r['source'] != 'fulltext'], key=lambda r: rank(20261120, r['rec']))[:30]
use_rows = []
for r in ft + ab:
    m = meta[r['rec']]
    row = {'rec': r['rec'], 'year': m['year'], 'title': m['title'], 'abstract': m['abstract'], 'doi_link': doi(m),
           'open_copy': use_log.get(r['rec'], {}).get('url', '') if r['source'] == 'fulltext' else ''}
    row.update({'ai_' + k: r[k] for k in USE_AI})
    use_rows.append(row)
USE_COLS = ['rec', 'year', 'title', 'abstract', 'doi_link', 'open_copy'] + ['ai_' + k for k in USE_AI] + ['person_agrees', 'person_corrections', 'checker', 'note']

pdf_rows = list(csv.DictReader(open(S / 'samples/pdf_requests.csv', encoding='utf-8')))
PDF_COLS = list(pdf_rows[0].keys()) if pdf_rows else ['sample']

readme = wb.active
readme.title = 'README'
EN = [
    'SMOTE25: the team\'s check of the AI work of the systematic search (WP4) and the use audit (WP5). Draft v0.7, 11 November 2026.',
    'Team use only: the abstracts are licensed (Scopus). Do not share outside the team or deposit.',
    '',
    'WHY. Every decision and code in these sheets was made by AI sessions. The paper may say only what was done and by whom, so the',
    'authors\' check is reported in Section 3.4 (agreement with the AI) and your corrections replace the AI decisions. Send the',
    'filled workbook back; a session copies the corrections into person_overrides.csv and regenerates every count, figure and table.',
    '',
    'ORDER OF WORK (rough time per item, for planning only)',
    '1. Sheet 6_pdf_downloads (217 papers, 1 to 2 min each): download through the KKU library, save as R#####.pdf (the name in',
    '   save_as) in ~/Downloads/SMOTE25/papers/sample_pdfs/, mark yes / no / not available. Work down by rank. This unblocks Sections 4.4 and 8.3.',
    '2. Sheet 1_unsure (1,222 records, about 1 min each): the screen could not settle these. Decide include or exclude.',
    '3. Sheets 2_includes and 3_exclusions (300 each, under 1 min each): confirm or correct a random sample of the AI decisions.',
    '   These two give the agreement the paper reports, so finish them even if sheet 1 is not done.',
    '4. Sheets 4_coverage_codes and 5_useaudit_codes (5 to 15 min each): confirm or correct the AI codes against the paper.',
    'Split the rows between you; write your initials in the checker column. Work in rank order: any first part is itself a random sample.',
    '',
    'HOW TO DECIDE A RECORD (sheets 1 to 3). Read the title and abstract; open doi_link if they do not settle it.',
    'INCLUDE when the paper proposes a resampling method of its own that creates synthetic minority examples, or changes how SMOTE is',
    '  applied, for classification, and evaluates it on data, in English. New combinations of known parts that the paper presents and',
    '  evaluates as its method count: SMOTE with a cleaning or selection step, SMOTE inside boosting, bagging or a cost-sensitive learner,',
    '  a multiclass scheme for oversampling, a GAN, VAE, diffusion or language-model generator of minority examples.',
    'EXCLUDE with a code: E1 an existing, named method (SMOTE, ADASYN, SMOTE-ENN ...) used as it is as a preprocessing step, the',
    '  contribution being a domain model, features or a classifier (calling the pipeline a framework does not make it new); E2 regression,',
    '  clustering or anomaly detection only; E-NOGEN no synthetic examples (undersampling, cost-sensitive learning, ensembles without',
    '  oversampling, feature selection, loss functions); E-REVIEW a review, survey, editorial or book front matter; E-COMPARE a comparison',
    '  of existing methods only; E-LANG not in English; E-OTHER anything else (say what in note), for example a generator built only for',
    '  privacy or data sharing and never used for imbalanced classification.',
    'UNSURE only when the full text is needed and you cannot open it. Write the code too when you know it (column person_code).',
    'In sheets 2 and 3 leave person_decision empty if you agree with the AI; write the other decision (and code) if you do not.',
    '',
    'HOW TO CHECK THE CODES (sheets 4 and 5). Open the paper (open_copy, or the library through doi_link). Write "yes" in person_agrees',
    'if every ai_ code is right; otherwise "no" and the corrections as field=value; field=value (for example inside_folds=before-split).',
    'Sheet 4 (coverage): eligible as above; label Core (interpolation between two instances, as in SMOTE, is the main generator),',
    '  Partial (one of several generators), Not counted (generates in another way: GAN, VAE, diffusion, a fitted distribution, noise or a',
    '  sphere around one point); the six decisions it changes against SMOTE: S seed selection, A how many points per seed, N choice of the',
    '  partner, P where the point is placed, F filtering after generation, L generator run inside a learning procedure; class B (only',
    '  two-class experiments), M (only three or more classes kept), B+M (both); then the evaluation items (competitors, measures,',
    '  protocol, whether resampling was fitted inside the training folds, how settings were chosen, statistical test, code).',
    'Sheet 5 (use audit): domain, the decision the model supports, stakes (a decision about a person or not), resampler, learner. For the',
    '  rows with open_copy (full text) look above all for WHEN the resampling was done: before the train/test split or the',
    '  cross-validation (before-split, a leak), or on the training part only (stated); whether the test results were computed on',
    '  resampled data (test_balanced); whether the same model without resampling, class weights or a tuned threshold is compared;',
    '  whether calibration is assessed; and whether the model is validated on data from another source, prospectively or in use.',
    '',
    'Questions the codebooks answer in detail: data/search/screening_full_2026-11-11/SCREENING_CODEBOOK.md, coverage/COVERAGE_CODEBOOK.md,',
    'useaudit/USE_AUDIT_CODEBOOK.md (in the draft package). This workbook replaces SMOTE25_screening_check_2026-11-11.xlsx of v0.6.',
]
TH = [
    '',
    'สรุปภาษาไทย',
    'ทุกการตัดสินในไฟล์นี้ทำโดย AI ทีมผู้เขียนต้องตรวจ เพราะบทความต้องบอกว่าใครทำอะไร และผลการตรวจจะแทนที่การตัดสินของ AI',
    'ลำดับงาน: (1) ชีต 6 ดาวน์โหลด PDF ผ่านห้องสมุด มข. บันทึกชื่อไฟล์ตามคอลัมน์ save_as ไว้ที่ ~/Downloads/SMOTE25/papers/sample_pdfs/',
    '(2) ชีต 1 ตัดสิน include หรือ exclude ให้ 1,222 รายการที่ AI ตัดสินไม่ได้ (3) ชีต 2 และ 3 ตรวจตัวอย่างสุ่มอย่างละ 300 รายการ',
    'ถ้าเห็นด้วยกับ AI ให้เว้นว่าง ถ้าไม่เห็นด้วยให้ใส่การตัดสินที่ถูกพร้อมรหัส (4) ชีต 4 และ 5 ตรวจรหัสที่ AI ให้กับบทความ',
    'ใส่ yes ถ้าถูกทั้งหมด หรือ no พร้อมค่าที่ถูก เช่น inside_folds=before-split',
    'เกณฑ์ include: บทความเสนอวิธี resampling ของตนเองที่สร้างตัวอย่างสังเคราะห์ของคลาสส่วนน้อย หรือเปลี่ยนวิธีใช้ SMOTE สำหรับ classification',
    'และทดลองกับข้อมูล รวมถึงการนำส่วนที่มีอยู่แล้วมาประกอบกันแล้วนำเสนอเป็นวิธีของตน เกณฑ์ exclude: E1 ใช้วิธีเดิมเป็นขั้นเตรียมข้อมูลในงานประยุกต์',
    'E2 ไม่ใช่ classification, E-NOGEN ไม่สร้างตัวอย่างสังเคราะห์, E-REVIEW บทความปริทัศน์, E-COMPARE เปรียบเทียบวิธีเดิมเท่านั้น, E-LANG ไม่ใช่ภาษาอังกฤษ',
    'ในชีต 5 ให้ดูเป็นพิเศษว่าทำ resampling ก่อนแบ่ง train/test (รั่ว) หรือทำเฉพาะชุด train และผลทดสอบคำนวณบนข้อมูลที่ถูก resample หรือไม่',
    'แบ่งแถวกันตรวจ ใส่ชื่อย่อในคอลัมน์ checker และทำตามลำดับ rank ส่งไฟล์ที่กรอกแล้วกลับมา',
]
for line in EN + TH:
    readme.append([line])
readme.column_dimensions['A'].width = 140
readme['A1'].font = Font(bold=True)

sheet('1_unsure', SCR_COLS, s1, SCR_W, {'person_decision', 'person_code', 'checker', 'note'}, VAL)
sheet('2_includes', SCR_COLS, s2, SCR_W, {'person_decision', 'person_code', 'checker', 'note'}, VAL)
sheet('3_exclusions', SCR_COLS, s3, SCR_W, {'person_decision', 'person_code', 'checker', 'note'}, VAL)
sheet('4_coverage_codes', COV_COLS, cov_rows, {'title': 40, 'doi_link': 22, 'open_copy': 30, 'ai_evidence': 40, 'ai_note': 40,
      'ai_measures': 24, 'person_corrections': 40, 'note': 30}, {'person_agrees', 'person_corrections', 'checker', 'note'},
      [('person_agrees', ['yes', 'no'])])
sheet('5_useaudit_codes', USE_COLS, use_rows, {'title': 40, 'abstract': 60, 'doi_link': 22, 'open_copy': 30, 'ai_task': 30,
      'ai_evidence': 40, 'ai_note': 40, 'ai_measures': 24, 'person_corrections': 40, 'note': 30}, {'person_agrees', 'person_corrections', 'checker', 'note'},
      [('person_agrees', ['yes', 'no'])])
sheet('6_pdf_downloads', PDF_COLS, pdf_rows, {'sample': 16, 'title': 60, 'venue': 30, 'url': 30, 'save_as': 12,
      'downloaded (yes/no/not available)': 18}, {'downloaded (yes/no/not available)'}, [('downloaded (yes/no/not available)', ['yes', 'no', 'not available'])])
leg = wb.create_sheet('codes')
for line in (['code', 'meaning'],
             ['I1-new-variant', 'a new SMOTE variant (seed, allocation, neighbor, placement or filter changed)'],
             ['I1-hybrid', 'SMOTE combined with another procedure (cleaning, boosting, cost-sensitive learning) as the paper\'s method'],
             ['I1-generative', 'a learned generator of minority examples (GAN, VAE, diffusion, language model)'],
             ['I1-multiclass', 'a multiclass scheme for oversampling'], ['I1-other', 'another generator of synthetic minority examples'],
             ['E1', 'applies an existing, named resampling method as a preprocessing step'], ['E2', 'regression, clustering or anomaly detection only'],
             ['E-NOGEN', 'no synthetic examples'], ['E-REVIEW', 'review, survey, editorial, front matter'],
             ['E-COMPARE', 'comparison of existing methods only'], ['E-LANG', 'not in English'], ['E-OTHER', 'other reason (say it in note)'],
             ['U-...', 'AI codes for unsure: new or applied? / no abstract / other']):
    leg.append(line)
leg.column_dimensions['A'].width, leg.column_dimensions['B'].width = 16, 100
out = S / 'check'
out.mkdir(exist_ok=True)
wb.save(out / 'SMOTE25_team_check_2026-11-11.xlsx')
print({'1_unsure': len(s1), '2_includes': len(s2), '3_exclusions': len(s3), '4_coverage_codes': len(cov_rows),
       '5_useaudit_codes': len(use_rows), '6_pdf_downloads': len(pdf_rows)})
