# Image unique pour ir-strata : Node 20 (Docusaurus) + Python 3 (pipeline de données).
# Le cœur du pipeline est stdlib ; requirements.txt n'apporte que le harnais inter-codeurs.
FROM node:20-bookworm-slim

# Python 3 + pip pour le pipeline (validate_model / compute_scores / generate_* / audits
# et intercoder_reliability_test) ; ca-certificates pour les requêtes HTTPS des audits
# (Crossref / OpenLibrary / OpenAlex).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python (numpy + krippendorff pour la fiabilité inter-codeurs).
# --break-system-packages : Debian bookworm marque l'environnement comme externally-managed
# (PEP 668) ; acceptable ici car l'image est dédiée à ce projet.
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

WORKDIR /app

# Le code est monté par volume (docker-compose) ; pas de COPY en mode dev.
EXPOSE 3000 3001
