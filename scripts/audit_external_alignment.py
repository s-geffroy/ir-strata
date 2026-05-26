#!/usr/bin/env python3
"""Confronte la couche `academic_influence` au signal bibliométrique externe.

Chantier 3. Pour chaque période, calcule la corrélation de rang de Spearman entre les
scores `academic_influence` normalisés (générés par le modèle) et le signal externe
(build_external_signal.py). C'est un CRITÈRE DE FALSIFIABILITÉ : une corrélation faible ou
négative signale que le classement académique du modèle s'écarte du signal indépendant et
mérite réexamen (signalement, non blocage : le signal n'est qu'un proxy).

Lecture seule, stdlib uniquement.
Sorties : references/external_alignment_report.json + docs/EXTERNAL_ALIGNMENT.md
"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNAL_PATH = ROOT / "src/data/canonical/external_signal.json"
REPORT_JSON = ROOT / "references/external_alignment_report.json"
DOCS_PATH = ROOT / "docs/EXTERNAL_ALIGNMENT.md"

# Seuil en deçà duquel l'alignement est jugé faible (à réexaminer).
WEAK_CORRELATION = 0.3


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ranks(values):
    """Rangs moyens (gestion des ex æquo) pour la corrélation de Spearman."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            result[order[k]] = avg_rank
        i = j + 1
    return result


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def spearman(xs, ys):
    if len(xs) < 3:
        return None
    return pearson(ranks(xs), ranks(ys))


def main() -> int:
    if not SIGNAL_PATH.exists():
        DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
        DOCS_PATH.write_text(
            "---\nid: EXTERNAL_ALIGNMENT\ntitle: Alignement au signal externe\n"
            "sidebar_label: Alignement externe\n---\n\n# Alignement au signal externe\n\n"
            "> Signal externe non encore construit. Lancez `python3 "
            "scripts/build_external_signal.py` (réseau, via `npm run data:refresh`).\n",
            encoding="utf-8")
        print("Signal externe absent : rapport en attente.")
        return 0

    signal = load(SIGNAL_PATH)["by_period"]
    scores = load(ROOT / "src/data/generated/scores_normalized.json")["scores"]

    # academic_influence normalisé, global_system, par période et famille.
    model = {}
    for s in scores:
        if s["entity_id"] == "global_system" and s["layer"] == "academic_influence":
            model.setdefault(s["period_id"], {})[s["theory_family_id"]] = s["normalized_score"]

    per_period = {}
    for pid, model_fams in model.items():
        ext_fams = signal.get(pid, {}).get("normalized_signal", {})
        common = sorted(set(model_fams) & set(ext_fams))
        if len(common) < 3:
            continue
        rho = spearman([model_fams[f] for f in common], [ext_fams[f] for f in common])
        per_period[pid] = {"n_families": len(common), "spearman": rho}

    weak = {pid: v for pid, v in per_period.items()
            if v["spearman"] is not None and v["spearman"] < WEAK_CORRELATION}

    report = {
        "audited_at": date.today().isoformat(),
        "weak_threshold": WEAK_CORRELATION,
        "per_period": per_period,
        "weak_periods": weak,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "---",
        "id: EXTERNAL_ALIGNMENT",
        "title: Alignement au signal externe",
        "sidebar_label: Alignement externe",
        "---",
        "",
        "# Alignement de l'influence académique au signal bibliométrique externe",
        "",
        f"_État au {report['audited_at']}._",
        "",
        "Corrélation de rang (Spearman) entre les scores `academic_influence` normalisés du "
        "modèle et un **signal externe indépendant** (comptes de publications OpenAlex par "
        "famille, cf. `build_external_signal.py`). Le signal est un **proxy** : une "
        "corrélation faible invite au réexamen, elle ne prouve pas une erreur.",
        "",
        f"Seuil d'alerte : Spearman < {WEAK_CORRELATION}.",
        "",
        "| Période | Familles | Spearman | Statut |",
        "| --- | ---: | ---: | --- |",
    ]
    for pid in sorted(per_period):
        v = per_period[pid]
        rho = v["spearman"]
        rho_str = f"{rho:.3f}" if rho is not None else "n/a"
        status = "⚠️ à réexaminer" if (rho is not None and rho < WEAK_CORRELATION) else "ok"
        lines.append(f"| {pid} | {v['n_families']} | {rho_str} | {status} |")
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Alignement externe : {len(per_period)} période(s) évaluée(s), "
          f"{len(weak)} sous le seuil.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
