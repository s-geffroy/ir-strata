#!/usr/bin/env python3
"""Harnais de fiabilité inter-codeurs (chantier 2).

Compare le codage de référence (auteur, scores_raw.json) à un ou plusieurs codages
indépendants déposés dans `src/data/coders/coder_<id>.json`, sur le sous-ensemble
protocole (périodes pilotes × 7 familles × 3 couches). Calcule, par bloc (période, couche)
et globalement :

- l'écart absolu moyen (MAE) de chaque codeur vs la référence ;
- l'ICC(3,1) (corrélation intra-classe, modèle mixte à deux facteurs, juge unique) ;
- l'alpha de Krippendorff (niveau intervalle).

Gate : si un bloc dépasse MAE_THRESHOLD, sortie non-zéro (le codebook ou les bornes de
période doivent être revus). Tant qu'aucun codage indépendant n'est déposé, le script est
en mode informatif et ne bloque pas le build.

Sorties : references/intercoder_report.json + docs/methodology/INTERCODER.md.
Dépendances : numpy, krippendorff (requirements.txt).
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

from compute_scores import derive_raw_from_criteria

ROOT = Path(__file__).resolve().parents[1]
CODERS_DIR = ROOT / "src/data/coders"
REPORT_JSON = ROOT / "references/intercoder_report.json"
DOCS_PATH = ROOT / "docs/methodology/INTERCODER.md"

# Sous-ensemble protocole : périodes pilotes du papier (modifiable). Avec 7 familles × 3
# couches × 3 périodes ⇒ jusqu'à 63 scores (moins ceux rejetés pour anachronisme).
PROTOCOL_PERIODS = ("1815_1848", "1945_1962", "1991_2001")
PROTOCOL_LAYERS = ("strategic_reality", "political_doctrine", "academic_influence")
# Seuil d'accord : au-delà, le bloc est jugé non fiable (cf. protocole du papier).
MAE_THRESHOLD = 10.0


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def raw_of(score: dict, criteria_weights: dict):
    """raw_score d'un enregistrement : valeur explicite, sinon dérivée des critères."""
    if score.get("raw_score") is not None:
        return float(score["raw_score"])
    return derive_raw_from_criteria(score.get("criteria_scores"), criteria_weights)


def reference_coding(criteria_weights: dict) -> dict:
    """{score_id: raw_score} de la référence, restreint au sous-ensemble protocole."""
    scores = load(ROOT / "src/data/canonical/scores_raw.json")["scores"]
    out = {}
    for s in scores:
        if (s["entity_id"] == "global_system"
                and s["period_id"] in PROTOCOL_PERIODS
                and s["layer"] in PROTOCOL_LAYERS
                and s.get("maturity_status") != "deprecated"):
            out[s["score_id"]] = raw_of(s, criteria_weights)
    return out


def coder_codings(criteria_weights: dict) -> dict:
    """{coder_id: {score_id: raw_score}} pour chaque fichier coder_*.json déposé."""
    codings = {}
    if not CODERS_DIR.exists():
        return codings
    for path in sorted(CODERS_DIR.glob("coder_*.json")):
        data = load(path)
        coder_id = data.get("coder_id", path.stem)
        codings[coder_id] = {
            s["score_id"]: raw_of(s, criteria_weights) for s in data.get("scores", [])
        }
    return codings


def icc_3_1(matrix):
    """ICC(3,1) — modèle mixte à deux facteurs, juge unique, cohérence.

    matrix : numpy array (n unités × k juges). Formule ANOVA classique (Shrout & Fleiss
    1979) : ICC(3,1) = (MSR - MSE) / (MSR + (k-1)·MSE).
    """
    import numpy as np
    n, k = matrix.shape
    grand_mean = matrix.mean()
    row_means = matrix.mean(axis=1)
    col_means = matrix.mean(axis=0)
    ss_rows = k * ((row_means - grand_mean) ** 2).sum()
    ss_cols = n * ((col_means - grand_mean) ** 2).sum()
    ss_total = ((matrix - grand_mean) ** 2).sum()
    ss_error = ss_total - ss_rows - ss_cols
    df_rows = n - 1
    df_error = (n - 1) * (k - 1)
    if df_rows <= 0 or df_error <= 0:
        return None
    msr = ss_rows / df_rows
    mse = ss_error / df_error
    denom = msr + (k - 1) * mse
    if denom == 0:
        return None
    return float((msr - mse) / denom)


def write_outputs(report: dict, lines: list):
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    criteria_weights = load(ROOT / "src/data/canonical/model_metadata.json")["default_criteria_weights"]
    reference = reference_coding(criteria_weights)
    coders = coder_codings(criteria_weights)

    header = [
        "---",
        "id: INTERCODER",
        "title: Fiabilité inter-codeurs",
        "sidebar_label: Fiabilité inter-codeurs",
        "---",
        "",
        "# Fiabilité inter-codeurs",
        "",
        f"_État au {date.today().isoformat()}. Sous-ensemble protocole : "
        f"{', '.join(PROTOCOL_PERIODS)} × {len(PROTOCOL_LAYERS)} couches × 7 familles._",
        "",
    ]

    # Mode informatif : aucun codage indépendant déposé.
    if not coders:
        report = {
            "audited_at": date.today().isoformat(),
            "status": "single_coder",
            "n_protocol_scores": len(reference),
            "coders": [],
            "message": "Un seul codeur (référence) : la fiabilité inter-codeurs n'est pas "
                       "testable. Déposez un codage indépendant via la console de codage.",
        }
        lines = header + [
            "> **Statut : un seul codeur.** La fiabilité inter-codeurs n'est pas encore "
            "testable : le codage publié est un codage d'auteur unique. Pour l'évaluer, un "
            "spécialiste doit re-coder le sous-ensemble protocole à l'aveugle (voir la "
            "**console de codage**) puis déposer son fichier dans `src/data/coders/`.",
            "",
            f"- Scores du protocole prêts à être recodés : **{len(reference)}**",
            f"- Seuil d'accord visé (MAE par bloc) : **≤ {MAE_THRESHOLD:.0f}**",
        ]
        write_outputs(report, lines)
        print(f"Inter-codeurs : 1 codeur (référence), {len(reference)} scores protocole. "
              "Fiabilité non testable (mode informatif).")
        return 0

    import numpy as np
    import krippendorff

    # Unités communes à TOUS les raters (référence + codeurs).
    rater_ids = ["reference"] + list(coders.keys())
    all_codings = {"reference": reference, **coders}
    common_ids = sorted(set(reference).intersection(*[set(c) for c in coders.values()]))
    if not common_ids:
        print("Inter-codeurs : aucun score commun entre la référence et les codeurs.")
        return 1

    # Matrice unités × raters.
    matrix = np.array([[all_codings[r][sid] for r in rater_ids] for sid in common_ids], dtype=float)

    # MAE de chaque codeur vs référence.
    ref_col = matrix[:, 0]
    mae_by_coder = {}
    for j, rid in enumerate(rater_ids[1:], start=1):
        mae_by_coder[rid] = float(np.abs(matrix[:, j] - ref_col).mean())

    # ICC(3,1) et alpha de Krippendorff (intervalle) sur l'ensemble des raters.
    icc = icc_3_1(matrix) if matrix.shape[1] >= 2 else None
    alpha = float(krippendorff.alpha(reliability_data=matrix.T, level_of_measurement="interval"))

    # MAE par bloc (période, couche) : écart moyen des codeurs vs référence.
    blocks = {}
    for idx, sid in enumerate(common_ids):
        # score_id = score_<period>_global_system_<layer>_<family> : on retrouve période et couche.
        period = next((p for p in PROTOCOL_PERIODS if sid.startswith(f"score_{p}_")), "?")
        layer = next((l for l in PROTOCOL_LAYERS if f"_{l}_" in sid), "?")
        deviations = [abs(matrix[idx, j] - matrix[idx, 0]) for j in range(1, len(rater_ids))]
        blocks.setdefault((period, layer), []).extend(deviations)
    block_mae = {f"{p}/{l}": float(np.mean(v)) for (p, l), v in blocks.items()}
    failing = {k: v for k, v in block_mae.items() if v > MAE_THRESHOLD}

    report = {
        "audited_at": date.today().isoformat(),
        "status": "ok" if not failing else "blocks_above_threshold",
        "n_protocol_scores": len(common_ids),
        "coders": list(coders.keys()),
        "mae_threshold": MAE_THRESHOLD,
        "mae_by_coder": mae_by_coder,
        "icc_3_1": icc,
        "krippendorff_alpha_interval": alpha,
        "block_mae": block_mae,
        "failing_blocks": failing,
    }

    lines = header + [
        f"- Codeurs comparés à la référence : **{', '.join(coders.keys())}**",
        f"- Scores communs analysés : **{len(common_ids)}**",
        f"- ICC(3,1) : **{icc:.3f}**" if icc is not None else "- ICC(3,1) : n/a",
        f"- Alpha de Krippendorff (intervalle) : **{alpha:.3f}**",
        "",
        "## MAE par codeur (vs référence)",
        "",
        "| Codeur | MAE |",
        "| --- | ---: |",
    ]
    lines += [f"| {c} | {m:.2f} |" for c, m in mae_by_coder.items()]
    lines += [
        "",
        f"## MAE par bloc (seuil ≤ {MAE_THRESHOLD:.0f})",
        "",
        "| Période / couche | MAE | Statut |",
        "| --- | ---: | --- |",
    ]
    for block, mae in sorted(block_mae.items()):
        status = "⚠️ à revoir" if mae > MAE_THRESHOLD else "ok"
        lines.append(f"| {block} | {mae:.2f} | {status} |")

    write_outputs(report, lines)
    print(f"Inter-codeurs : {len(coders)} codeur(s), {len(common_ids)} scores, "
          f"ICC(3,1)={icc:.3f} alpha={alpha:.3f}, "
          f"{len(failing)} bloc(s) au-dessus du seuil.")
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
