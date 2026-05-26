#!/usr/bin/env python3
"""Recalcule `raw_score` depuis `criteria_scores` dans les fichiers canoniques de scores.

Chantier 1 (phase 2) : les `criteria_scores` deviennent la source de vérité unique ;
`raw_score` n'est plus un jugement saisi indépendamment mais le résultat déterministe de
la formule documentée (cf. compute_scores.derive_raw_from_criteria et
model_metadata.json:default_criteria_weights). Ce script réaligne les `raw_score`
canoniques sur leurs critères ; validate_model.py garantit ensuite qu'ils ne divergent
plus (gate de cohérence).

Outil reproductible : à relancer après toute modification de `criteria_scores`.
Idempotent. stdlib uniquement.

Usage :
  python3 scripts/migrate_raw_from_criteria.py          # applique et écrit
  python3 scripts/migrate_raw_from_criteria.py --check   # signale sans écrire (exit 1 si dérive)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from compute_scores import derive_raw_from_criteria

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("src/data/canonical/scores_raw.json", "src/data/canonical/scores_entities_raw.json")
# Précision de stockage du raw_score recalculé (lisible, suffisante pour la synthèse).
STORE_DECIMALS = 2


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main(check_only: bool) -> int:
    criteria_weights = load("src/data/canonical/model_metadata.json")["default_criteria_weights"]
    total_changed = 0
    drift = []
    for rel_path in TARGETS:
        data = load(rel_path)
        changed = 0
        for score in data["scores"]:
            derived = derive_raw_from_criteria(score.get("criteria_scores"), criteria_weights)
            if derived is None:
                continue  # pas de critères dérivables (cas limite) : on laisse en l'état
            new_raw = round(derived, STORE_DECIMALS)
            if score.get("raw_score") != new_raw:
                drift.append((score["score_id"], score.get("raw_score"), new_raw))
                score["raw_score"] = new_raw
                changed += 1
        if changed and not check_only:
            (ROOT / rel_path).write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        total_changed += changed
        print(f"{rel_path}: {changed} raw_score recalculés")

    if check_only:
        if drift:
            print(f"DÉRIVE : {len(drift)} raw_score divergent de leurs critères :")
            for sid, old, new in drift[:20]:
                print(f"  - {sid}: {old} → {new}")
            if len(drift) > 20:
                print(f"  … et {len(drift) - 20} autres")
            return 1
        print("Aucune dérive : raw_score cohérents avec les critères.")
        return 0

    print(f"Total : {total_changed} raw_score recalculés depuis les critères.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--check" in sys.argv))
