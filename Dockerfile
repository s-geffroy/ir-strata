# Image unique pour ir-strata : Node 20 (Docusaurus) + Python 3 (pipeline de données).
# Les scripts Python n'utilisent que la stdlib → aucun pip / requirements.txt.
FROM node:20-bookworm-slim

# Python 3 pour validate_model / compute_scores / generate_exports / generate_mdx ;
# ca-certificates pour les requêtes HTTPS de l'audit de références (Crossref / OpenLibrary).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Le code est monté par volume (docker-compose) ; pas de COPY en mode dev.
EXPOSE 3000 3001
