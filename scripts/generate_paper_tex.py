#!/usr/bin/env python3
"""Génère paper/main.tex : wrapper LaTeX compilable autour du corps .txt
(préambule + \\maketitle + bibliographie natbib). Le .txt reste la source unique."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BODY = ROOT / "paper/papier_strates_ri_chemin_a.txt"
OUT = ROOT / "paper/main.tex"

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[french]{babel}
\usepackage[margin=2.5cm]{geometry}
\usepackage{array}
\usepackage{natbib}
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=black,citecolor=blue,urlcolor=blue}
\setcitestyle{authoryear,round}

\begin{document}
"""

BIB = (r"\bibliographystyle{plainnat}"
       "\n" r"\bibliography{references_strates_ri_chemin_a}" "\n")

lines = BODY.read_text(encoding="utf-8").splitlines()
out = [PREAMBLE]
in_math = False
for ln in lines:
    st = ln.strip()
    if st == r"\[":
        in_math = True
    elif st == r"\]":
        in_math = False
    elif not in_math:
        # échapper les underscores des identifiants snake_case en prose (hors math)
        ln = ln.replace("_", r"\_")

    if st == r"\begin{abstract}":
        out.append(r"\maketitle")
        out.append(ln)
    elif st == r"\appendix":
        out.append(BIB)
        out.append(ln)
    else:
        out.append(ln)
out.append(r"\end{document}")
OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"Généré : {OUT.relative_to(ROOT)}")
