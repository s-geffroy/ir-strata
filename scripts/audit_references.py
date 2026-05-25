#!/usr/bin/env python3
"""Audit de provenance des références (anti-hallucination).

Pour chaque référence de src/data/canonical/references.json, interroge des bases
bibliographiques publiques (Crossref, puis OpenLibrary en repli) et tente de
retrouver un ouvrage réel correspondant au triplet (titre, auteur, année).

Sorties :
  - references/audit_report.json  : détail machine par référence
  - references/AUDIT_REFERENCES.md : rapport lisible + références à re-sourcer

Statuts d'audit : "verified" / "probable" (match trouvé), "unverifiable" (les API
ont répondu mais aucun match probant -> à re-sourcer), et "api_unavailable" (une
API était injoignable, ex. OpenLibrary HTTP 403 : l'audit n'a pas pu conclure).
Seul "unverifiable" est bloquant sous --check ; "api_unavailable" ne l'est pas,
car une panne d'API tierce ne prouve pas qu'une référence est douteuse.

Avec --write, met à jour maturity_status -> "contested" pour les références
classées "unverifiable" dans references.json (le reste est inchangé).

N'utilise que la stdlib (urllib) : aucune dépendance pip.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS_PATH = ROOT / "src/data/canonical/references.json"
OUT_DIR = ROOT / "references"          # rapport machine (JSON)
DOCS_PATH = ROOT / "docs/AUDIT_REFERENCES.md"  # rapport lisible publié sur le site
USER_AGENT = "ir-strata-reference-audit/0.1 (mailto:sylvain.geffroy@gmail.com)"
REQUEST_PAUSE = 0.4  # politesse envers les API publiques

# Seuils de classification
STRONG_TITLE = 0.85
MEDIUM_TITLE = 0.60
YEAR_TOLERANCE = 2


def norm(text: str) -> str:
    """Minuscule, sans diacritiques, alphanumérique espacé."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def title_similarity(ref_title: str, cand_title: str) -> float:
    """Max entre ratio de séquence et containment par tokens (gère les sous-titres)."""
    a, b = norm(ref_title), norm(cand_title)
    if not a or not b:
        return 0.0
    ratio = SequenceMatcher(None, a, b).ratio()
    ta, tb = set(a.split()), set(b.split())
    shorter, longer = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    containment = len(shorter & longer) / len(shorter) if shorter else 0.0
    return max(ratio, containment)


def surname(author: str) -> str:
    """Nom de famille du premier auteur."""
    first = re.split(r"\s+and\s+|;|&|,", author or "", maxsplit=1)[0].strip()
    tokens = norm(first).split()
    return tokens[-1] if tokens else ""


def fetch_json(url: str) -> tuple[dict | None, str | None]:
    """Retourne (données, erreur). `erreur` non nul = API injoignable (403, réseau,
    timeout...) — à distinguer d'une réponse vide (référence réellement introuvable)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.load(resp), None
    except Exception as exc:  # noqa: BLE001 — on enregistre l'échec, on continue
        return None, str(exc)


def query_crossref(ref: dict) -> tuple[list[dict], str | None]:
    q = urllib.parse.urlencode({
        "query.bibliographic": f"{ref.get('title','')} {ref.get('author','')}",
        "rows": 10,
    })
    data, error = fetch_json(f"https://api.crossref.org/works?{q}")
    if error or not data:
        return [], error
    items = data.get("message", {}).get("items", [])
    out = []
    for it in items:
        titles = it.get("title") or [""]
        title = re.sub(r"<[^>]+>", "", titles[0]) if titles else ""
        authors = " ".join(
            f"{a.get('given','')} {a.get('family','')}".strip()
            for a in it.get("author", [])
        )
        year = None
        for key in ("published", "published-print", "issued", "published-online"):
            parts = (it.get(key) or {}).get("date-parts") or []
            if parts and parts[0] and parts[0][0]:
                year = parts[0][0]
                break
        out.append({"source": "crossref", "title": title, "author": authors,
                    "year": year, "id": it.get("DOI")})
    return out, None


def query_openlibrary(ref: dict) -> tuple[list[dict], str | None]:
    q = urllib.parse.urlencode({
        "q": f"{ref.get('title','')} {ref.get('author','')}",
        "limit": 5,
        "fields": "title,author_name,first_publish_year,key",
    })
    data, error = fetch_json(f"https://openlibrary.org/search.json?{q}")
    if error or not data:
        return [], error
    out = []
    for doc in data.get("docs", []):
        out.append({
            "source": "openlibrary",
            "title": doc.get("title", ""),
            "author": ", ".join(doc.get("author_name", []) or []),
            "year": doc.get("first_publish_year"),
            "id": doc.get("key"),
        })
    return out, None


def best_match(ref: dict, candidates: list[dict]) -> dict | None:
    ref_surname = surname(ref.get("author", ""))
    ref_year = ref.get("year")
    scored = []
    for c in candidates:
        t_sim = title_similarity(ref.get("title", ""), c.get("title", ""))
        author_ok = bool(ref_surname) and ref_surname in norm(c.get("author", ""))
        year_ok = (
            isinstance(ref_year, int) and isinstance(c.get("year"), int)
            and abs(c["year"] - ref_year) <= YEAR_TOLERANCE
        )
        # Score composite : le titre seul ne suffit pas (un ouvrage *à propos* d'une
        # œuvre contient son titre exact). La corroboration auteur/année départage.
        composite = t_sim + (0.30 if author_ok else 0.0) + (0.20 if year_ok else 0.0)
        scored.append({**c, "title_sim": round(t_sim, 3),
                       "author_ok": author_ok, "year_ok": year_ok,
                       "composite": round(composite, 3)})
    if not scored:
        return None
    return max(scored, key=lambda c: c["composite"])


def classify(match: dict | None) -> str:
    if not match:
        return "unverifiable"
    t, a, y = match["title_sim"], match["author_ok"], match["year_ok"]
    if t >= STRONG_TITLE and (a or y):
        return "verified"
    if t >= MEDIUM_TITLE and a and y:
        return "verified"
    if t >= MEDIUM_TITLE and (a or y):
        return "probable"
    return "unverifiable"


def audit_one(ref: dict) -> dict:
    cx_candidates, cx_error = query_crossref(ref)
    time.sleep(REQUEST_PAUSE)
    ol_candidates, ol_error = query_openlibrary(ref)
    time.sleep(REQUEST_PAUSE)
    candidates = cx_candidates + ol_candidates
    match = best_match(ref, candidates)
    status = classify(match)
    api_errors = {src: err for src, err in
                  (("crossref", cx_error), ("openlibrary", ol_error)) if err}
    # Résilience : une référence non vérifiable alors qu'une API a échoué (403,
    # réseau, timeout...) ne peut pas être déclarée douteuse — l'audit n'a pas eu
    # de chance équitable. On la classe `api_unavailable` (non bloquant), distinct
    # de `unverifiable` (les API ont répondu mais aucun match probant).
    if status == "unverifiable" and api_errors:
        status = "api_unavailable"
    return {
        "id": ref.get("id"),
        "bibtex_key": ref.get("bibtex_key"),
        "title": ref.get("title"),
        "author": ref.get("author"),
        "year": ref.get("year"),
        "audit_status": status,
        "best_match": match,
        "candidates_seen": len(candidates),
        "api_errors": api_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="passe les références 'unverifiable' en maturity_status=contested")
    parser.add_argument("--check", action="store_true",
                        help="sortie non-nulle si au moins une référence est 'unverifiable'")
    parser.add_argument("--limit", type=int, default=0,
                        help="limiter le nombre de références (debug)")
    args = parser.parse_args()

    doc = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    references = doc["references"]
    if args.limit:
        references = references[:args.limit]

    results = []
    for i, ref in enumerate(references, 1):
        res = audit_one(ref)
        results.append(res)
        print(f"[{i}/{len(references)}] {res['audit_status']:12} {res['id']}")

    counts: dict[str, int] = {}
    for r in results:
        counts[r["audit_status"]] = counts.get(r["audit_status"], 0) + 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "audited_at": date.today().isoformat(),
        "source_apis": ["crossref", "openlibrary"],
        "total": len(results),
        "counts": counts,
        "results": results,
    }
    (OUT_DIR / "audit_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)

    if args.write:
        flagged = {r["id"] for r in results if r["audit_status"] == "unverifiable"}
        for ref in doc["references"]:
            if ref.get("id") in flagged:
                ref["maturity_status"] = "contested"
        REFS_PATH.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n--write : {len(flagged)} référence(s) passée(s) en maturity_status=contested")

    print("\nRésumé :", json.dumps(counts, ensure_ascii=False))

    if counts.get("api_unavailable"):
        apis = sorted({src for r in results for src in (r.get("api_errors") or {})})
        print(f"NOTE : {counts['api_unavailable']} référence(s) non vérifiée(s) car "
              f"API indisponible(s) ({', '.join(apis) or 'inconnue'}). Statut "
              "`api_unavailable`, non bloquant — l'audit n'a pas pu conclure.")

    if args.check and counts.get("unverifiable"):
        print(f"CHECK FAILED : {counts['unverifiable']} référence(s) non vérifiable(s)")
        return 1
    return 0


def write_markdown(report: dict) -> None:
    lines = [
        "---",
        "id: AUDIT_REFERENCES",
        "title: Audit de provenance des références",
        "sidebar_label: Audit des références",
        "---",
        "",
        "# Audit de provenance des références",
        "",
        f"_Audité le {report['audited_at']} via {', '.join(report['source_apis'])}._",
        "",
        "Cet audit tente de retrouver chaque référence dans des bases bibliographiques "
        "publiques afin de détecter d'éventuelles références hallucinées. Il ne remplace "
        "pas une vérification humaine : `probable` et `unverifiable` doivent être relus.",
        "",
        "## Synthèse",
        "",
        "| Statut | Nombre |",
        "| --- | --- |",
    ]
    for status in ("verified", "probable", "unverifiable", "api_unavailable"):
        lines.append(f"| `{status}` | {report['counts'].get(status, 0)} |")
    lines += ["", "## Références à re-sourcer (`unverifiable`)", ""]
    flagged = [r for r in report["results"] if r["audit_status"] == "unverifiable"]
    if not flagged:
        lines.append("_Aucune._")
    else:
        lines.append("| id | titre | auteur | année | meilleur match (titre sim.) |")
        lines.append("| --- | --- | --- | --- | --- |")
        for r in flagged:
            m = r["best_match"]
            mt = f"{m['title']} ({m['title_sim']})" if m else "—"
            lines.append(f"| `{r['id']}` | {r['title']} | {r['author']} | "
                         f"{r['year']} | {mt} |")
    lines += ["", "## À vérifier manuellement (`probable`)", ""]
    probable = [r for r in report["results"] if r["audit_status"] == "probable"]
    if not probable:
        lines.append("_Aucune._")
    else:
        lines.append("| id | titre | meilleur match | sim. | auteur ok | année ok |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for r in probable:
            m = r["best_match"] or {}
            lines.append(f"| `{r['id']}` | {r['title']} | {m.get('title','—')} | "
                         f"{m.get('title_sim','—')} | {m.get('author_ok','—')} | "
                         f"{m.get('year_ok','—')} |")
    lines += ["", "## Non vérifiées car API indisponible (`api_unavailable`)", "",
              "Ces références n'ont pas pu être contrôlées parce qu'une base "
              "bibliographique était injoignable (ex. OpenLibrary `HTTP 403`). "
              "Ce **n'est pas** un signe de référence douteuse : l'audit n'a pas "
              "pu conclure et ne bloque pas la publication.", ""]
    unavailable = [r for r in report["results"] if r["audit_status"] == "api_unavailable"]
    if not unavailable:
        lines.append("_Aucune._")
    else:
        lines.append("| id | titre | auteur | année | API en échec |")
        lines.append("| --- | --- | --- | --- | --- |")
        for r in unavailable:
            apis = ", ".join((r.get("api_errors") or {}).keys()) or "—"
            lines.append(f"| `{r['id']}` | {r['title']} | {r['author']} | "
                         f"{r['year']} | {apis} |")
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
