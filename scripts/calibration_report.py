#!/usr/bin/env python3
"""Rapport de couverture du re-sourçage (calibration) des scores.

Distingue les scores encore au stade `seed` (justification générée, non sourcée) des scores
`sourced` (justification réelle adossée à des preuves et références vérifiées). Un score est
considéré `sourced` s'il porte `calibration_status: "sourced"`. Tout le reste est `seed`.

Sorties :
  - references/calibration_report.json
  - docs/CALIBRATION_STATUS.md (publié, priorise les périodes P1)

Le re-sourçage est le grand chantier restant : ce rapport en mesure l'avancement et désigne
les prochains lots prioritaires (P1, hors scores rejetés pour anachronisme).

stdlib uniquement, lecture seule.
"""
from __future__ import annotations
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS_PATH = ROOT / "docs/CALIBRATION_STATUS.md"
REPORT_JSON = ROOT / "references/calibration_report.json"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> int:
    periods = {p["period_id"]: p for p in load("src/data/canonical/periods.json")["periods"]}
    rows = (load("src/data/canonical/scores_raw.json")["scores"]
            + load("src/data/canonical/scores_entities_raw.json")["scores"])

    # On ne compte que les scores actifs (hors deprecated/anachroniques).
    active = [s for s in rows if s.get("maturity_status") != "deprecated"]
    deprecated_count = len(rows) - len(active)
    sourced = [s for s in active if s.get("calibration_status") == "sourced"]

    # Dette de re-sourçage : preuves dont le résumé est encore un gabarit (« À enrichir »).
    evidence_list = load("src/data/canonical/evidence.json")["evidence"]
    template_evidence = [e for e in evidence_list
                         if "à enrichir" in (e.get("summary_fr") or "").lower()]

    by_period = defaultdict(lambda: {"sourced": 0, "seed": 0})
    for s in active:
        bucket = "sourced" if s.get("calibration_status") == "sourced" else "seed"
        by_period[s["period_id"]][bucket] += 1

    report = {
        "audited_at": date.today().isoformat(),
        "active_scores": len(active),
        "sourced": len(sourced),
        "seed": len(active) - len(sourced),
        "by_period": dict(by_period),
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    pct = 100 * len(sourced) / len(active) if active else 0
    lines = [
        "---",
        "id: CALIBRATION_STATUS",
        "title: Avancement du re-sourçage",
        "sidebar_label: Re-sourçage des scores",
        "---",
        "",
        "# Avancement du re-sourçage des scores",
        "",
        f"_État au {report['audited_at']}._",
        "",
        "> **Ce que « sourcé » garantit — et ne garantit pas.** Le statut `sourced` signifie "
        "que le score est **adossé à des preuves et des références vérifiées** (existantes, "
        "non anachroniques). Il ne signifie **pas** que la valeur numérique est validée "
        "empiriquement par un spécialiste : cette validation relève de l'étude inter-codeurs "
        "(voir la console de codage et le rapport inter-codeurs).",
        "",
        "Le re-sourçage remplace progressivement les justifications seed par des "
        "justifications réelles, adossées aux preuves et références vérifiées. Ce tableau en "
        "mesure l'avancement.",
        "",
        f"**{len(sourced)} / {len(active)} scores _actifs_ re-sourcés ({pct:.1f} %).**",
        "",
        f"_Le total inclut aussi {deprecated_count} scores rejetés pour anachronisme "
        "(`deprecated`), exclus de ce décompte : « 100 % » se lit donc « 100 % des scores "
        "actifs adossés à des preuves », pas « 100 % validés »._",
        "",
        "## Par période (priorité P1 d'abord)",
        "",
        "| Période | Priorité | Sourcé | Seed |",
        "| --- | --- | ---: | ---: |",
    ]
    ordered = sorted(by_period.items(),
                     key=lambda kv: (periods.get(kv[0], {}).get("priority", "P2"), kv[0]))
    for pid, c in ordered:
        prio = periods.get(pid, {}).get("priority", "?")
        lines.append(f"| {pid} | {prio} | {c['sourced']} | {c['seed']} |")
    lines += [
        "",
        "## Dette : preuves encore au stade gabarit",
        "",
        f"**{len(template_evidence)} / {len(evidence_list)} preuves** portent encore un "
        "résumé gabarit (« À enrichir avec citations précises »). Tant que ce compteur n'est "
        "pas nul, le `probative_strength` de ces preuves reste indicatif, non documenté.",
        "",
    ]
    if template_evidence:
        lines += ["| Preuve | Période |", "| --- | --- |"]
        for e in sorted(template_evidence, key=lambda x: x.get("period_id", "")):
            lines.append(f"| {e['evidence_id']} | {e.get('period_id', '?')} |")
    lines += [
        "",
        "## Méthode de re-sourçage",
        "",
        "Pour chaque score : justification analytique réelle, `evidence_basis` pointant des "
        "preuves existantes, `direct_references` vers des références **vérifiées**, confiance "
        "recalibrée, `known_limits` explicites, puis `calibration_status: \"sourced\"`. Voir "
        "la tranche déjà traitée comme gabarit (1945-1962, couche `strategic_reality`).",
    ]
    report["template_evidence"] = len(template_evidence)
    report["deprecated_excluded"] = deprecated_count
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Calibration : {len(sourced)}/{len(active)} scores actifs sourcés ({pct:.1f} %) ; "
          f"{len(template_evidence)} preuves gabarit ; {deprecated_count} rejetés exclus")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
