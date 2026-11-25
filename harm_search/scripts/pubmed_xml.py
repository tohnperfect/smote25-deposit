"""Parse the raw PubMed esearch/efetch XML of query O1 into one JSON file of records,
and write plain-text screening batches (title and full abstract) for manual reading.

Usage: python3 -I parse_records.py RAW_DIR OUT_JSON BATCH_DIR BATCH_SIZE

Checks: every PMID in the esearch IdList appears in the efetch pages, and vice versa.
No screening decision is made here.
"""
import glob
import json
import os
import re
import sys
import textwrap
import xml.etree.ElementTree as ET


def text_of(el):
    if el is None:
        return ""
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def year_of(article_el, pubmed_data_el):
    pd = article_el.find("Journal/JournalIssue/PubDate")
    if pd is not None:
        y = pd.findtext("Year")
        if y:
            return y.strip()
        md = pd.findtext("MedlineDate")
        if md:
            m = re.search(r"\d{4}", md)
            if m:
                return m.group(0)
    ad = article_el.find("ArticleDate")
    if ad is not None and ad.findtext("Year"):
        return ad.findtext("Year").strip()
    if pubmed_data_el is not None:
        for d in pubmed_data_el.findall("History/PubMedPubDate"):
            if d.get("PubStatus") == "pubmed" and d.findtext("Year"):
                return d.findtext("Year").strip()
    return ""


def history_date(pubmed_data_el, status):
    if pubmed_data_el is None:
        return ""
    for d in pubmed_data_el.findall("History/PubMedPubDate"):
        if d.get("PubStatus") == status:
            y, m, dd = d.findtext("Year"), d.findtext("Month"), d.findtext("Day")
            if y:
                return "%s-%02d-%02d" % (y, int(m or 0), int(dd or 0))
    return ""


def abstract_sections(abs_parent):
    out = []
    if abs_parent is None:
        return out
    for at in abs_parent.findall("AbstractText"):
        label = at.get("Label") or ""
        out.append({"label": label, "text": text_of(at)})
    return out


def parse_article(pa):
    mc = pa.find("MedlineCitation")
    art = mc.find("Article")
    pdata = pa.find("PubmedData")
    pmid = mc.findtext("PMID").strip()
    secs = abstract_sections(art.find("Abstract"))
    other = []
    for oa in mc.findall("OtherAbstract"):
        other.extend(abstract_sections(oa))
    doi = ""
    if pdata is not None:
        for aid in pdata.findall("ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = (aid.text or "").strip()
    return {
        "pmid": pmid,
        "year": year_of(art, pdata),
        "journal": text_of(art.find("Journal/Title")),
        "title": text_of(art.find("ArticleTitle")),
        "abstract_sections": secs,
        "other_abstract_sections": other,
        "publication_types": [text_of(p) for p in art.findall("PublicationTypeList/PublicationType")],
        "language": [text_of(l) for l in art.findall("Language")],
        "entrez_date": history_date(pdata, "entrez"),
        "pubmed_date": history_date(pdata, "pubmed"),
        "doi": doi,
        "record_type": "PubmedArticle",
    }


def parse_book(pb):
    bd = pb.find("BookDocument")
    pmid = bd.findtext("PMID").strip()
    title = text_of(bd.find("ArticleTitle")) or text_of(bd.find("Book/BookTitle"))
    return {
        "pmid": pmid,
        "year": (bd.findtext("Book/PubDate/Year") or "").strip(),
        "journal": text_of(bd.find("Book/BookTitle")),
        "title": title,
        "abstract_sections": abstract_sections(bd.find("Abstract")),
        "other_abstract_sections": [],
        "publication_types": [text_of(p) for p in bd.findall("PublicationType")],
        "language": [text_of(l) for l in bd.findall("Language")],
        "entrez_date": "",
        "pubmed_date": "",
        "doi": "",
        "record_type": "PubmedBookArticle",
    }


def full_abstract(rec):
    parts = []
    for s in rec["abstract_sections"]:
        parts.append((s["label"] + ": " if s["label"] else "") + s["text"])
    return " ".join(parts)


def main():
    raw_dir, out_json, batch_dir, batch_size = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    es = ET.parse(os.path.join(raw_dir, "esearch.xml")).getroot()
    count = int(es.findtext("Count"))
    id_list = [i.text.strip() for i in es.findall("IdList/Id")]

    records = []
    for path in sorted(glob.glob(os.path.join(raw_dir, "efetch_retstart_*.xml"))):
        root = ET.parse(path).getroot()
        for pa in root.findall("PubmedArticle"):
            records.append(parse_article(pa))
        for pb in root.findall("PubmedBookArticle"):
            records.append(parse_book(pb))

    fetched = [r["pmid"] for r in records]
    print("esearch Count:", count, "| IdList length:", len(id_list))
    print("efetch records:", len(records), "| unique:", len(set(fetched)))
    print("in IdList but not fetched:", sorted(set(id_list) - set(fetched)))
    print("fetched but not in IdList:", sorted(set(fetched) - set(id_list)))

    # keep the esearch order
    order = {p: i for i, p in enumerate(id_list)}
    records.sort(key=lambda r: order.get(r["pmid"], 10 ** 9))
    for i, r in enumerate(records, 1):
        r["seq"] = i
        r["abstract"] = full_abstract(r)

    no_abs = [r["pmid"] for r in records if not r["abstract"]]
    print("records without abstract:", len(no_abs), no_abs)
    print("records with OtherAbstract only:", [r["pmid"] for r in records if not r["abstract"] and r["other_abstract_sections"]])
    print("book records:", [r["pmid"] for r in records if r["record_type"] != "PubmedArticle"])
    print("non-English:", [(r["pmid"], r["language"]) for r in records if r["language"] != ["eng"]])
    flagged_types = [(r["pmid"], t) for r in records for t in r["publication_types"]
                     if t in ("Review", "Systematic Review", "Meta-Analysis", "Retracted Publication",
                              "Retraction of Publication", "Comment", "Editorial", "Erratum", "Published Erratum")]
    print("flagged publication types:", flagged_types)
    by_entrez = {}
    for r in records:
        by_entrez.setdefault(r["entrez_date"][:7], 0)
        by_entrez[r["entrez_date"][:7]] += 1
    recent = sorted([(r["entrez_date"], r["pmid"]) for r in records], reverse=True)[:8]
    print("most recent entrez dates:", recent)
    years = {}
    for r in records:
        years[r["year"]] = years.get(r["year"], 0) + 1
    print("records per year:", dict(sorted(years.items())))

    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump({"esearch_count": count, "id_list": id_list, "records": records}, fh, ensure_ascii=False, indent=1)

    os.makedirs(batch_dir, exist_ok=True)
    wrap = textwrap.TextWrapper(width=240, break_long_words=False, break_on_hyphens=False)
    nb = 0
    for b in range(0, len(records), batch_size):
        nb += 1
        lines = []
        for r in records[b:b + batch_size]:
            lines.append("=" * 20)
            lines.append("#%d PMID %s | %s | %s | %s" % (r["seq"], r["pmid"], r["year"], r["journal"],
                                                    "; ".join(r["publication_types"])))
            lines.append("TI: " + r["title"])
            if not r["abstract_sections"]:
                lines.append("AB: [no abstract in record]")
                if r["other_abstract_sections"]:
                    lines.append("OTHER ABSTRACT:")
                    for s in r["other_abstract_sections"]:
                        lines.extend(wrap.wrap((s["label"] + ": " if s["label"] else "") + s["text"]))
            for s in r["abstract_sections"]:
                lines.extend(wrap.wrap((s["label"] + ": " if s["label"] else "") + s["text"]))
        with open(os.path.join(batch_dir, "batch_%02d.txt" % nb), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    print("wrote", nb, "batches to", batch_dir)


if __name__ == "__main__":
    main()
