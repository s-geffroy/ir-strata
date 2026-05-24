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
    sourced = [s for s in active if s.get("calibration_status") == "sourced"]

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
        "Les audits précédents garantissent l'existence des références et l'absence "
        "d'anachronisme, **pas** la justesse des valeurs de score. Le re-sourçage remplace "
        "progressivement les justifications seed par des justifications réelles, adossées aux "
        "preuves et références vérifiées. Ce tableau en mesure l'avancement.",
        "",
        f"**{len(sourced)} / {len(active)} scores actifs re-sourcés ({pct:.1f} %).**",
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
        "## Méthode de re-sourçage",
        "",
        "Pour chaque score : justification analytique réelle, `evidence_basis` pointant des "
        "preuves existantes, `direct_references` vers des références **vérifiées**, confiance "
        "recalibrée, `known_limits` explicites, puis `calibration_status: \"sourced\"`. Voir "
        "la tranche déjà traitée comme gabarit (1945-1962, couche `strategic_reality`).",
    ]
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Calibration : {len(sourced)}/{len(active)} scores actifs sourcés ({pct:.1f} %)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
