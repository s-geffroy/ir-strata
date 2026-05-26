#!/usr/bin/env python3
"""Test de sensibilité au choix « rejeter vs scorer bas » l'anachronisme.

Chantier 3. Le modèle REJETTE (deprecated) tout score doctrine/académique antérieur à
l'émergence d'une famille — un choix de modélisation fort. Ce script recalcule la synthèse
sous l'hypothèse alternative : au lieu de rejeter, on attribue un score BAS (LOW_SCORE) à
ces couches émergentes. On compare ensuite la conclusion (famille dominante et classement)
de chaque période entre les deux régimes.

Lecture : si les conclusions tiennent, le choix de rejet est robuste ; si elles basculent,
l'hypothèse est trop forte et doit être documentée.

Lecture seule, stdlib uniquement.
Sortie : docs/ANACHRONISM_SENSITIVITY.md
"""
from __future__ import annotations
import copy
import json
from datetime import date
from pathlib import Path

from compute_scores import normalize, synthesize, derive_raw_from_criteria

ROOT = Path(__file__).resolve().parents[1]
DOCS_PATH = ROOT / "docs/ANACHRONISM_SENSITIVITY.md"

# Score bas attribué aux couches émergentes dans le régime alternatif.
LOW_SCORE = 5
CONSTRAINED_LAYERS = ("political_doctrine", "academic_influence")


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def dominant_ranking(synth_normalized, period_id):
    """Classement des familles (desc) par synthèse normalisée pour une période."""
    items = [(s["theory_family_id"], s["normalized_score"]) for s in synth_normalized
             if s["entity_id"] == "global_system" and s["period_id"] == period_id]
    return [fam for fam, _ in sorted(items, key=lambda kv: kv[1], reverse=True)]


def main() -> int:
    metadata = load("src/data/canonical/model_metadata.json")
    weights = metadata["default_synthesis_weights"]
    periods = {p["period_id"]: p for p in load("src/data/canonical/periods.json")["periods"]}
    emergence = {e["theory_family_id"]: e
                 for e in load("src/data/canonical/theory_emergence.json")["emergence"]}
    raw = (load("src/data/canonical/scores_raw.json")["scores"]
           + load("src/data/canonical/scores_entities_raw.json")["scores"])

    # Régime publié : la synthèse ne se forme que pour les familles présentes sur 3 couches.
    baseline = normalize(synthesize(raw, weights))

    # Régime alternatif : les scores rejetés pour anachronisme sont réactivés à LOW_SCORE.
    alt_raw = copy.deepcopy(raw)
    reactivated_periods = set()
    for s in alt_raw:
        period = periods.get(s["period_id"])
        emap = emergence.get(s["theory_family_id"])
        if (s.get("maturity_status") == "deprecated" and s["layer"] in CONSTRAINED_LAYERS
                and emap and period and period["start_year"] < emap[f"{s['layer']}_from"]):
            s["maturity_status"] = "reviewed"
            s["raw_score"] = LOW_SCORE
            reactivated_periods.add(s["period_id"])
    alternative = normalize(synthesize(alt_raw, weights))

    rows = []
    for pid in sorted(periods):
        base_rank = dominant_ranking(baseline, pid)
        alt_rank = dominant_ranking(alternative, pid)
        base_top = base_rank[0] if base_rank else "—"
        alt_top = alt_rank[0] if alt_rank else "—"
        if not base_rank and not alt_rank:
            continue  # période sans synthèse dans les deux régimes
        if not base_rank and alt_rank:
            verdict = "synthèse créée (n'existait pas en régime publié)"
        elif base_top != alt_top:
            verdict = "⚠️ dominante change"
        elif base_rank != alt_rank:
            verdict = "classement modifié (dominante stable)"
        else:
            verdict = "stable"
        rows.append((pid, base_top, alt_top, verdict))

    lines = [
        "---",
        "id: ANACHRONISM_SENSITIVITY",
        "title: Sensibilité à l'anachronisme",
        "sidebar_label: Sensibilité anachronisme",
        "---",
        "",
        "# Sensibilité au choix « rejeter vs scorer bas » l'anachronisme",
        "",
        f"_État au {date.today().isoformat()}._",
        "",
        "Le modèle **rejette** les scores doctrine/académique antérieurs à l'émergence d'une "
        f"famille. Régime alternatif testé ici : leur attribuer un score bas ({LOW_SCORE}) "
        "au lieu de les rejeter. On compare la famille dominante et le classement de chaque "
        "période entre les deux régimes.",
        "",
        f"Périodes affectées (au moins un score réactivé) : "
        f"{', '.join(sorted(reactivated_periods)) or 'aucune'}.",
        "",
        "| Période | Dominante (publié) | Dominante (alternatif) | Verdict |",
        "| --- | --- | --- | --- |",
    ]
    for pid, base_top, alt_top, verdict in rows:
        lines.append(f"| {pid} | {base_top} | {alt_top} | {verdict} |")
    lines += [
        "",
        "## Lecture",
        "",
        "- **Stable / dominante stable** : la conclusion ne dépend pas du choix de rejet → "
        "choix robuste.",
        "- **Synthèse créée** : le rejet supprime une synthèse que l'alternative ferait "
        "exister (ex. périodes pré-académiques). C'est l'effet voulu du rejet, à assumer.",
        "- **⚠️ Dominante change** : la conclusion dépend du choix de modélisation → "
        "hypothèse forte à documenter explicitement.",
    ]
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    changed = sum(1 for _, _, _, v in rows if v.startswith("⚠️"))
    print(f"Sensibilité anachronisme : {len(rows)} période(s) avec synthèse, "
          f"{changed} à dominante changeante. Rapport écrit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
