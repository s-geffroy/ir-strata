#!/usr/bin/env python3
"""Construit un signal bibliométrique externe par famille théorique et par période.

Chantier 3 (ancrage externe falsifiable). Interroge l'API OpenAlex (gratuite, sans clé)
pour compter les publications associées à chaque famille théorique sur l'intervalle d'années
de chaque période, puis normalise ces comptes à 100 % par période. Ce signal — indépendant
de nos scores — sert de point de comparaison pour la couche `academic_influence`
(cf. audit_external_alignment.py).

C'est un PROXY assumé : les mots-clés ne capturent pas parfaitement chaque tradition, et
OpenAlex sous-représente l'avant-XXe siècle. À traiter comme un repère, pas une vérité.

Réseau, hors build déterministe (rangé dans `data:refresh`). Dégradation gracieuse : si
l'API est indisponible, le fichier existant est conservé et le statut passe à
`api_unavailable`. stdlib uniquement.

Sortie : src/data/canonical/external_signal.json
"""
from __future__ import annotations
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src/data/canonical/external_signal.json"
OPENALEX = "https://api.openalex.org/works"
# OpenAlex recommande un mailto pour le "polite pool".
MAILTO = "ir-strata@example.org"

# Mots-clés de recherche plein texte par famille (proxy, documenté comme tel).
FAMILY_QUERIES = {
    "realism": "realism international relations theory",
    "liberalism": "liberalism international relations theory",
    "marxism_dependency_structuralism": "dependency theory marxism international relations",
    "constructivism": "constructivism international relations theory",
    "english_school": "english school international society",
    "critical_postcolonial_feminist": "postcolonial feminist critical international relations",
    "geopolitics_imperialism_reason_of_state": "geopolitics imperialism international relations",
}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def openalex_count(query: str, start_year: int, end_year: int) -> int | None:
    """Nombre de publications OpenAlex pour la requête sur l'intervalle d'années."""
    params = urllib.parse.urlencode({
        "search": query,
        "filter": f"publication_year:{start_year}-{end_year}",
        "per_page": 1,
        "mailto": MAILTO,
    })
    url = f"{OPENALEX}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": f"ir-strata ({MAILTO})"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return int(data.get("meta", {}).get("count", 0))
    except Exception as exc:  # réseau indisponible, rate limit, etc.
        print(f"  ! OpenAlex indisponible pour '{query}' {start_year}-{end_year}: {exc}")
        return None


def main() -> int:
    periods = load("src/data/canonical/periods.json")["periods"]
    emergence = {e["theory_family_id"]: e
                 for e in load("src/data/canonical/theory_emergence.json")["emergence"]}

    by_period = {}
    api_failures = 0
    for p in periods:
        pid, start, end = p["period_id"], p["start_year"], p["end_year"]
        counts = {}
        for family, query in FAMILY_QUERIES.items():
            # Ne sonder que les familles déjà émergées académiquement sur la période.
            acad_from = emergence.get(family, {}).get("academic_influence_from")
            if acad_from is not None and end < acad_from:
                continue
            count = openalex_count(query, start, end)
            if count is None:
                api_failures += 1
            else:
                counts[family] = count
            time.sleep(0.2)  # courtoisie envers l'API
        total = sum(counts.values())
        normalized = {f: round(100 * c / total, 4) for f, c in counts.items()} if total else {}
        by_period[pid] = {"raw_counts": counts, "normalized_signal": normalized}

    status = "ok" if api_failures == 0 else ("partial" if any(
        v["raw_counts"] for v in by_period.values()) else "api_unavailable")

    if status == "api_unavailable" and OUTPUT.exists():
        print("OpenAlex totalement indisponible : fichier existant conservé.")
        return 0

    payload = {
        "schema_version": "1.0.0",
        "source": "OpenAlex (https://openalex.org)",
        "built_at": date.today().isoformat(),
        "status": status,
        "is_proxy": True,
        "note": "Signal proxy : comptes de publications par mots-clés, normalisés à 100 % "
                "par période. Indépendant des scores du modèle, à des fins de comparaison.",
        "family_queries": FAMILY_QUERIES,
        "by_period": by_period,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Signal externe construit (statut={status}, {api_failures} échec(s) API).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
