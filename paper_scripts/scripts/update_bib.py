#!/usr/bin/env python3
"""WP8: write refs.bib v0.2 from v0.1 plus the reviewed results of verify_refs.py.

Every change below was read against its source on 10 Nov 2026 (Crossref record,
arXiv abstract page or JMLR page); see refcheck/report.csv and the v0.2 handoff.
Usage: python3 scripts/update_bib.py ../v01/refs.bib refcheck/report.csv refs.bib
"""
import csv
import re
import sys
from pathlib import Path

D = '2026-11-10'
FIX = {  # key -> fields to set (None removes the field)
    'chawla2003smoteboost': {'doi': '10.1007/978-3-540-39804-2_12'},
    'batista2004study': {'doi': '10.1145/1007730.1007735'},
    'he2008adasyn': {'doi': '10.1109/IJCNN.2008.4633969'},
    'chen2010ramoboost': {'doi': '10.1109/TNN.2010.2066988'},
    'cao2013inos': {'doi': '10.1109/TKDE.2013.37'},
    'agrawal2015scut': {'doi': '10.5220/0005595502260234'},
    'nekooeimehr2016asuwo': {'doi': '10.1016/j.eswa.2015.10.031'},
    'zhang2016cgmos': {'doi': '10.1145/2983323.2983789'},
    'mullick2019gamo': {'doi': '10.1109/ICCV.2019.00178'},
    'almajzoub2020absmote': {'doi': '10.18178/ijmlc.2020.10.1.894'},
    'chen2021hde': {'doi': '10.1016/j.ins.2020.12.023'},
    'chen2021rsmote': {'doi': '10.1016/j.ins.2020.10.013'},
    'maldonado2022fwsmote': {'doi': '10.1016/j.patcog.2021.108511'},
    'tao2022svddw': {'author': 'Tao, Xinmin and Zheng, Yujia and Chen, Wei and Zhang, Xiaohan and Qi, Lin and Fan, Zhiting and Huang, Shan',
                     'doi': '10.1016/j.ins.2021.12.066'},
    'liu2023nromm': {'doi': '10.1016/j.patcog.2022.109008'},
    'yadav2025ciso': {'author': 'Yadav, Pankaj and Vijay, Vivek',
                      'note': 'Version 1 posted 27 January 2025, version 2 on 6 August 2026; no journal version found on 10 November 2026'},
    'hu2026loyalty': {'author': 'Hu, Shengquan and Li, Junfei and Li, Zefeng and Zhang, Zihao and Feng, Yan and Law, K. L. Eddie',
                      'volume': '199', 'pages': '108677', 'doi': '10.1016/j.neunet.2026.108677', 'note': None},
    'upman2026qcsmote': {'_type': 'article', 'author': 'Upman, Parth and Gowda, Shreyank N.', 'journal': 'Neurocomputing',
                         'volume': '711', 'pages': '135492', 'year': '2027', 'doi': '10.1016/j.neucom.2026.135492',
                         'howpublished': None,
                         'note': 'Issue of January 2027; the corpus coded the arXiv version (arXiv:2606.24625, June 2026)'},
    'pradipta2021smote': {'author': 'Pradipta, Gede Angga and Wardoyo, Retantyo and Musdholifah, Aina and Sanjaya, I Nyoman Hariyasa and Ismail, Muhammad',
                          'pages': '1--8', 'doi': '10.1109/ICIC54025.2021.9632912', 'note': None},
    'hassanat2022stop': {'author': 'Hassanat, Ahmad B. and Tarawneh, Ahmad S. and Altarawneh, Ghada A. and Almuhaimeed, Abdullah',
                         'note': 'The corpus copy. A journal version appeared as Tarawneh et al. (2022), IEEE Access 10:47643--47660'},
    'wang2012multiclass': {'doi': '10.1109/TSMCB.2012.2187280'},
    'buda2018systematic': {'doi': '10.1016/j.neunet.2018.07.011'},
    'lopez2012analysis': {'doi': '10.1016/j.eswa.2011.12.043'},
    'lopez2014importance': {'doi': '10.1016/j.ins.2013.09.038'},
    'demsar2006statistical': {'url': 'https://www.jmlr.org/papers/v7/demsar06a.html'},
    'cawley2010overfitting': {'url': 'https://www.jmlr.org/papers/v11/cawley10a.html'},
    'lemaitre2017imbalanced': {'url': 'https://www.jmlr.org/papers/v18/16-365.html'},
    'he2009learning': {'doi': '10.1109/TKDE.2008.239'},
    'branco2016survey': {'doi': '10.1145/2907070'},
    'krawczyk2016learning': {'doi': '10.1007/s13748-016-0094-0'},
    'haixiang2017learning': {'doi': '10.1016/j.eswa.2016.12.035'},
    'kovacs2019empirical': {'doi': '10.1016/j.asoc.2019.105662'},
    'kovacs2019smotevariants': {'doi': '10.1016/j.neucom.2019.06.100'},
    'elor2022smote': {'note': 'arXiv:2201.08528, version 3 of May 2022; no journal version found on 10 November 2026'},
    'sakho2026rebalancing': {'volume': None, 'note': 'arXiv:2402.03819 (version 6, March 2026); PMLR volume number to be added'},
    'tantithamthavorn2020impact': {'doi': '10.1109/TSE.2018.2876537'},
    'elreedy2019comprehensive': {'doi': '10.1016/j.ins.2019.07.070'},
    'elreedy2024theoretical': {'doi': '10.1007/s10994-022-06296-4'},
    'ahmad2025concentration': {'author': 'Ahmad, Touqeer and Mousavi Kalan, Mohammadreza and Portier, Fran{\\c{c}}ois and Stupfler, Gilles',
                               'volume': '38', 'pages': '174853--174894', 'doi': '10.52202/085713-5262'},
    'xia2026imbalance': {'howpublished': 'arXiv preprint arXiv:2601.10630', 'note': None},
    'vandengoorbergh2022harm': {'doi': '10.1093/jamia/ocac093'},
    'carriero2025harms': {'number': '3--4', 'pages': 'e10320', 'doi': '10.1002/sim.10320'},
    'piccininni2024understanding': {'doi': '10.1016/j.jbi.2024.104666'},
    'yang2024impact': {'doi': '10.1186/s40537-023-00857-7'},
    'andersen2026tipping': {'author': 'Andersen, Amalie Koch and Mehdizavareh, Hadi and Khan, Arijit and Becher, Tobias and Britsch, Simone and Britsch, Markward and B{\\o}ttcher, Morten and Winther, Simon and Rohde, Palle Duun and Jensen, Morten Hasselstr{\\o}m and Cichosz, Simon Lebech',
                            'volume': '33', 'number': '10', 'pages': '1943--1956', 'doi': '10.1093/jamia/ocag127', 'note': None},
    'roesler2026class': {'author': "Roesler, Mathias William and Wells, Cameron and Schamberg, Gabriel and Gao, Junyi and Harrison, Ewen and O'Grady, Gregory and Varghese, Chris",
                         'doi': '10.64898/2026.03.04.26347634'},
    'sirikul2026class': {'author': 'Sirikul, Wachiranun and Isaradech, Natthanaphop and Kiratipaisarl, Wuttipat and Wongyikul, Pakpoom and Jirattikanwong, Noraworn and Phinyo, Phichayut',
                         'howpublished': 'arXiv preprint arXiv:2606.08966'},
    'santos2018cross': {'doi': '10.1109/MCI.2018.2866730'},
    'vandewiele2021overly': {'author': 'Vandewiele, Gilles and Dehaene, Isabelle and Kov{\\\'a}cs, Gy{\\"o}rgy and Sterckx, Lucas and Janssens, Olivier and Ongenae, Femke and De Backere, Femke and De Turck, Filip and Roelens, Kristien and Decruyenaere, Johan and Van Hoecke, Sofie and Demeester, Thomas',
                             'doi': '10.1016/j.artmed.2020.101987'},
    'ganev2026smote': {},
    'collins2024tripodai': {'doi': '10.1136/bmj-2023-078378'},
    'chakraborty2021bias': {'doi': '10.1145/3468264.3468537'},
    'dablain2023deepsmote': {'doi': '10.1109/TNNLS.2021.3136503'},
    'zhang2018mixup': {'note': 'arXiv:1710.09412, ICLR camera-ready version'},
}
SOURCE = {  # how each memory or incomplete entry was verified
    'demsar2006statistical': 'JMLR page', 'cawley2010overfitting': 'JMLR page', 'lemaitre2017imbalanced': 'JMLR page',
    'yadav2025ciso': 'arXiv page', 'elor2022smote': 'arXiv page', 'sakho2026rebalancing': 'arXiv page (journal-ref AISTATS 2026)',
    'xia2026imbalance': 'arXiv API', 'sirikul2026class': 'arXiv page', 'zhang2016cgmos': 'Crossref (manual query)', 'santos2018cross': 'Crossref (manual query)', 'ganev2026smote': 'arXiv page (ICLR 2026)',
    'zhang2018mixup': 'arXiv page',
}
NEW = ("@article{tarawneh2022stop, author={Tarawneh, Ahmad S. and Hassanat, Ahmad B. and Altarawneh, Ghada Awad and "
       "Almuhaimeed, Abdullah}, title={Stop Oversampling for Class Imbalance Learning: A Review}, journal={IEEE Access}, "
       "volume={10}, pages={47643--47660}, year={2022}, doi={10.1109/ACCESS.2022.3169512}, "
       "status={verified: Crossref " + D + "; journal version of hassanat2022stop}}")


def set_field(entry, name, value):
    pat = re.compile(r'(,\s*)' + name + r'=\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}')
    if value is None:
        return pat.sub('', entry, count=1)
    if pat.search(entry):
        return pat.sub(lambda m: f'{m.group(1)}{name}={{{value}}}', entry, count=1)
    return re.sub(r',\s*status=\{', f', {name}={{{value}}}, status={{', entry, count=1)


def main():
    lines = Path(sys.argv[1]).read_text(encoding='utf-8').splitlines()
    rep = {r['key']: r for r in csv.DictReader(open(sys.argv[2], encoding='utf-8'))}
    out = []
    for line in lines:
        m = re.match(r'@(\w+)\{([^,]+),', line)
        if not m:
            out.append(line.replace('% refs.bib for the SMOTE25 integrated draft v0.1 (10 Nov 2026).',
                                    '% refs.bib for the SMOTE25 integrated draft v0.2 (10 Nov 2026); checked against Crossref, arXiv and JMLR on 10 Nov 2026 (scripts/verify_refs.py, refcheck/report.csv).')
                       .replace('%   memory    = completed from memory; VERIFY against the DOI before submission',
                                '%   verified  = checked against the named source on 10 Nov 2026 (no entry is from memory any more)'))
            continue
        typ, key = m.group(1), m.group(2)
        e = line
        fix = dict(FIX.get(key, {}))
        if '_type' in fix:
            e = e.replace(f'@{typ}{{', '@' + fix.pop('_type') + '{', 1)
        for k, v in fix.items():
            e = set_field(e, k, v)
        r = rep.get(key, {})
        old = re.search(r'status=\{([^}]*)\}', e).group(1)
        if key in SOURCE:
            new = f'verified: {SOURCE[key]} {D}'
        elif r.get('cr_doi'):
            new = f"verified: Crossref ({'DOI' if r.get('how') == 'doi' else 'title search'}) {D}"
            if not old.startswith('memory') and not old.startswith('checked'):
                new = f'{old}; Crossref DOI checked {D}' if r.get('how') == 'doi' else f'{old}; Crossref {D}'
        else:
            new = old
        e = re.sub(r'status=\{[^}]*\}', 'status={' + new + '}', e)
        out.append(e)
        if key == 'hassanat2022stop':
            out.append(NEW)
    out = [re.sub(r'^% -{3,} (.*?) -{3,}$', r'% ==== \1 ====', l) for l in out]
    Path(sys.argv[3]).write_text('\n'.join(out) + '\n', encoding='utf-8')
    txt = '\n'.join(out)
    print('entries', txt.count('\n@') + (1 if txt.startswith('@') else 0), '| memory left', txt.count('status={memory'),
          '| with doi', len(re.findall(r'\bdoi=\{', txt)), '| "others"', txt.count(' and others}'))


if __name__ == '__main__':
    main()
