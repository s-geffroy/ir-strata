#!/usr/bin/env python3
"""Traçabilité des révisions de scores (chantier 4b).

Compare l'état courant des scores canoniques à un instantané précédent
(`references/scores_snapshot.json`) et journalise tout changement de `raw_score` dans
`src/data/canonical/revision_log.json`. Le `raw_score` étant dérivé des critères, un
changement journalisé signale soit une modification des critères, soit un réalignement.

Modes :
  --write   : journalise les changements et met à jour l'instantané (mutateur).
  --check   : signale les changements non journalisés (lecture seule). Exit 1 si dérive
              entre l'instantané et l'état courant n'est pas reflétée dans le journal.

À la première exécution, l'instantané est initialisé sans journaliser (baseline).
stdlib uniquement.
"""
from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "references/scores_snapshot.json"
LOG_PATH = ROOT / "src/data/canonical/revision_log.json"
SCORE_FILES = ("src/data/canonical/scores_raw.json", "src/data/canonical/scores_entities_raw.json")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def current_state() -> dict:
    """{score_id: raw_score} pour tous les scores (actifs et rejetés)."""
    state = {}
    for rel in SCORE_FILES:
        for s in load(ROOT / rel)["scores"]:
            state[s["score_id"]] = s["raw_score"]
    return state


def score_meta() -> dict:
    meta = {}
    for rel in SCORE_FILES:
        for s in load(ROOT / rel)["scores"]:
            meta[s["score_id"]] = {
                "period_id": s.get("period_id"),
                "theory_family_id": s.get("theory_family_id"),
                "layer": s.get("layer"),
            }
    return meta


def diff(previous: dict, current: dict):
    """Liste des (score_id, old, new) dont le raw_score a changé."""
    changes = []
    for score_id, new_value in current.items():
        old_value = previous.get(score_id)
        if old_value is not None and old_value != new_value:
            changes.append((score_id, old_value, new_value))
    return changes


def main(write: bool) -> int:
    current = current_state()

    if not SNAPSHOT_PATH.exists():
        if write:
            SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
            SNAPSHOT_PATH.write_text(
                json.dumps({"captured_at": date.today().isoformat(), "raw_scores": current},
                           ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Instantané initialisé ({len(current)} scores). Aucune révision journalisée.")
        else:
            print("Aucun instantané : exécutez --write pour initialiser la baseline.")
        return 0

    previous = load(SNAPSHOT_PATH)["raw_scores"]
    changes = diff(previous, current)

    if not write:
        if changes:
            print(f"DÉRIVE non journalisée : {len(changes)} raw_score ont changé depuis "
                  "l'instantané. Lancez `track_revisions.py --write` pour journaliser.")
            for sid, old, new in changes[:20]:
                print(f"  - {sid}: {old} → {new}")
            return 1
        print("Aucune dérive : scores cohérents avec l'instantané.")
        return 0

    if not changes:
        print("Aucun changement à journaliser.")
        return 0

    meta = score_meta()
    log = load(LOG_PATH)
    today = date.today().isoformat()
    for sid, old, new in changes:
        m = meta.get(sid, {})
        log["revisions"].append({
            "revised_at": today,
            "score_id": sid,
            "period_id": m.get("period_id"),
            "theory_family_id": m.get("theory_family_id"),
            "layer": m.get("layer"),
            "field": "raw_score",
            "old_value": old,
            "new_value": new,
            "reason": "Critères modifiés ou raw_score réaligné sur les critères "
                      "(migrate_raw_from_criteria).",
        })
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SNAPSHOT_PATH.write_text(
        json.dumps({"captured_at": today, "raw_scores": current}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"{len(changes)} révision(s) journalisée(s) dans revision_log.json ; instantané mis à jour.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--write" in sys.argv))
