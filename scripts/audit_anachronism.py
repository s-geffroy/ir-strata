#!/usr/bin/env python3
"""Audit anti-anachronisme.

Règle (docs/methodology/ANTI_ANACHRONISM.md) : une théorie peut servir à analyser
rétrospectivement la réalité stratégique (couche strategic_reality, toujours autorisée),
mais ne peut pas compter comme doctrine politique (political_doctrine) ou influence
académique (academic_influence) AVANT son émergence historique.

Ce script confronte chaque score des couches political_doctrine / academic_influence à
la table d'émergence (src/data/canonical/theory_emergence.json) et signale tout score
dont la période commence avant l'émergence de la théorie pour cette couche.

Sorties :
  - references/anachronism_report.json  : détail machine
  - docs/AUDIT_ANACHRONISM.md           : rapport lisible publié sur le site

Avec --write, applique le rejet prévu par la règle : maturity_status -> "deprecated"
et ajout d'un bloc anachronism sur les scores fautifs (ils sont alors exclus des
graphiques et conclusions via compute_scores.py). Un score peut être épargné en portant
"anachronism_override": true (usage anachronique explicitement justifié).

stdlib uniquement.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORE_FILES = ["src/data/canonical/scores_raw.json",
               "src/data/canonical/scores_entities_raw.json"]
EMERGENCE_PATH = ROOT / "src/data/canonical/theory_emergence.json"
REPORT_JSON = ROOT / "references/anachronism_report.json"
DOCS_PATH = ROOT / "docs/AUDIT_ANACHRONISM.md"
CONSTRAINED_LAYERS = ("political_doctrine", "academic_influence")


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def emergence_map() -> dict:
    data = json.loads(EMERGENCE_PATH.read_text(encoding="utf-8"))
    return {e["theory_family_id"]: e for e in data["emergence"]}


def detect(emergence: dict, periods: dict) -> list[dict]:
    findings = []
    for fname in SCORE_FILES:
        for s in load(fname)["scores"]:
            layer = s.get("layer")
            if layer not in CONSTRAINED_LAYERS:
                continue
            fam = s.get("theory_family_id")
            emap = emergence.get(fam)
            period = periods.get(s.get("period_id"))
            if not emap or not period:
                continue
            emerged = emap[f"{layer}_from"]
            start = period["start_year"]
            if start < emerged:
                findings.append({
                    "file": fname,
                    "score_id": s["score_id"],
                    "period_id": s["period_id"],
                    "period_start": start,
                    "theory_family_id": fam,
                    "layer": layer,
                    "emerged_from": emerged,
                    "years_before_emergence": emerged - start,
                    "already_deprecated": s.get("maturity_status") == "deprecated",
                    "has_override": bool(s.get("anachronism_override")),
                })
    return findings


def write_back(findings: list[dict]) -> int:
    by_file: dict[str, set] = {}
    for f in findings:
        if f["has_override"]:
            continue
        by_file.setdefault(f["file"], set()).add(f["score_id"])
    changed = 0
    detail = {f["score_id"]: f for f in findings}
    for fname, ids in by_file.items():
        doc = load(fname)
        for s in doc["scores"]:
            if s["score_id"] in ids:
                d = detail[s["score_id"]]
                s["maturity_status"] = "deprecated"
                s["anachronism"] = {
                    "status": "rejected_anachronistic",
                    "layer": d["layer"],
                    "emerged_from": d["emerged_from"],
                    "period_start": d["period_start"],
                    "rule": "theory not available for this layer before emergence",
                }
                changed += 1
        (ROOT / fname).write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def write_markdown(report: dict) -> None:
    by_family: dict[str, int] = {}
    by_layer: dict[str, int] = {}
    for f in report["findings"]:
        by_family[f["theory_family_id"]] = by_family.get(f["theory_family_id"], 0) + 1
        by_layer[f["layer"]] = by_layer.get(f["layer"], 0) + 1
    lines = [
        "---",
        "id: AUDIT_ANACHRONISM",
        "title: Audit anti-anachronisme",
        "sidebar_label: Audit anti-anachronisme",
        "---",
        "",
        "# Audit anti-anachronisme",
        "",
        f"_Audité le {report['audited_at']}._",
        "",
        "Confronte les scores des couches `political_doctrine` et `academic_influence` aux "
        "années d'émergence (`theory_emergence.json`). La couche `strategic_reality` n'est "
        "jamais contrainte (usage rétrospectif autorisé). Les scores fautifs non justifiés "
        "sont rejetés (`maturity_status: deprecated`) et exclus des graphiques.",
        "",
        "## Synthèse",
        "",
        f"- Scores anachroniques détectés : **{report['total']}**",
        f"- Dont déjà rejetés / justifiés : {report['already_handled']}",
        f"- Rejetés par cet audit (`--write`) : {report.get('written', 0)}",
        "",
        "### Par couche",
        "",
        "| Couche | Nombre |",
        "| --- | --- |",
    ]
    for layer, n in sorted(by_layer.items()):
        lines.append(f"| `{layer}` | {n} |")
    lines += ["", "### Par famille théorique", "", "| Famille | Nombre |", "| --- | --- |"]
    for fam, n in sorted(by_family.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{fam}` | {n} |")
    lines += ["", "## Exemples (jusqu'à 25)", "",
              "| score_id | famille | couche | période début | émergence | années avant |",
              "| --- | --- | --- | --- | --- | --- |"]
    for f in report["findings"][:25]:
        lines.append(f"| `{f['score_id']}` | {f['theory_family_id']} | {f['layer']} | "
                     f"{f['period_start']} | {f['emerged_from']} | {f['years_before_emergence']} |")
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="rejette (deprecated) les scores anachroniques non justifiés")
    parser.add_argument("--check", action="store_true",
                        help="sortie non-nulle s'il reste des anachronismes non traités (read-only)")
    args = parser.parse_args()

    periods = {p["period_id"]: p for p in load("src/data/canonical/periods.json")["periods"]}
    emergence = emergence_map()
    findings = detect(emergence, periods)

    already_handled = sum(1 for f in findings if f["already_deprecated"] or f["has_override"])
    report = {
        "audited_at": date.today().isoformat(),
        "total": len(findings),
        "already_handled": already_handled,
        "findings": findings,
    }

    written = 0
    if args.write:
        written = write_back(findings)
    report["written"] = written

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)

    print(f"Anachronismes détectés : {len(findings)} | déjà gérés : {already_handled} | "
          f"rejetés (--write) : {written}")

    unhandled = [f for f in findings if not f["already_deprecated"] and not f["has_override"]]
    if args.check and unhandled:
        print(f"CHECK FAILED : {len(unhandled)} anachronisme(s) non traité(s) "
              f"(lancer --write ou poser anachronism_override)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
