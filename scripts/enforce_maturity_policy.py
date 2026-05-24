#!/usr/bin/env python3
"""Politique de maturité : concentrer `reviewed` sur les périodes P1.

Principe (honnêteté du statut) : le jeu de données est un seed non vérifié. Un objet ne peut
porter `reviewed`/`validated` que s'il est rattaché à une période prioritaire P1 (effort de
revue concentré). Tout objet `reviewed`/`validated` rattaché à une période non-P1 est
rétrogradé en `draft`. Les objets `deprecated` (ex. anachronismes) ne sont pas touchés.

Exemption : `references.json` — ces objets sont validés par l'audit de provenance
(audit_references.py, 56/56 vérifiées), leur statut `reviewed` reste défendable.

stdlib uniquement. Avec --write, applique les rétrogradations. Sans, simple rapport.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = {"reviewed", "validated"}

# (fichier, clé liste, champ période, "single" | "list")
TARGETS = [
    ("src/data/canonical/scores_raw.json", "scores", "period_id", "single"),
    ("src/data/canonical/scores_entities_raw.json", "scores", "period_id", "single"),
    ("src/data/canonical/evidence.json", "evidence", "period_id", "single"),
    ("src/data/canonical/events.json", "events", "period_id", "single"),
    ("src/data/canonical/controversies.json", "controversies", "period_ids", "list"),
    ("src/data/canonical/periods.json", "periods", "period_id", "self"),
]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def p1_set() -> set:
    return {p["period_id"] for p in load("src/data/canonical/periods.json")["periods"]
            if p.get("priority") == "P1"}


def is_non_p1(obj: dict, field: str, kind: str, p1: set) -> bool:
    """True si l'objet n'est rattaché à AUCUNE période P1."""
    if kind == "self":
        return obj.get("priority") != "P1"
    if kind == "single":
        return obj.get(field) not in p1
    periods = obj.get(field) or []
    return not any(p in p1 for p in periods)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="applique les rétrogradations")
    parser.add_argument("--check", action="store_true",
                        help="sortie non-nulle si des objets reviewed/validated sont hors P1 (read-only)")
    args = parser.parse_args()

    p1 = p1_set()
    total_demoted = 0
    summary = []

    for path, key, field, kind in TARGETS:
        doc = load(path)
        demoted = 0
        for obj in doc[key]:
            if obj.get("maturity_status") in REVIEWED and is_non_p1(obj, field, kind, p1):
                demoted += 1
                if args.write:
                    obj["maturity_status"] = "draft"
        if demoted and args.write:
            (ROOT / path).write_text(
                json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        total_demoted += demoted
        summary.append((key, demoted))

    print("Rétrogradations reviewed/validated -> draft (hors P1) :")
    for key, n in summary:
        print(f"  {key:14} {n}")
    print(f"Total : {total_demoted}{' (appliqué)' if args.write else ' (rapport seul)'}")
    print("Exempté : references.json (validé par l'audit de provenance)")

    if args.check and not args.write and total_demoted:
        print(f"CHECK FAILED : {total_demoted} objet(s) reviewed/validated hors P1 (lancer --write)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
