#!/usr/bin/env python3
"""Génère docs/PAPER.md (MDX) à partir de paper/main.tex (source de vérité LaTeX).
On saute le préambule et les directives bibliographiques, on convertit le balisage en
Markdown et on met les formules en code (les accolades LaTeX casseraient MDX sinon).
stdlib uniquement."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "paper/main.tex"
OUT = ROOT / "docs/PAPER.md"
PDF_REL = "/paper/strates_ri.pdf"


def cite(m: str) -> str:
    keys = [k.strip() for k in m.split(",")]
    out = []
    for k in keys:
        mt = re.match(r"([a-zA-Z]+)(\d{4})", k)
        if mt:
            out.append(f"{mt.group(1).capitalize()} {mt.group(2)}")
        else:
            out.append(k)
    return "(" + " ; ".join(out) + ")"


def inline(s: str) -> str:
    s = re.sub(r"\\citep\{([^}]*)\}", lambda m: cite(m.group(1)), s)
    s = re.sub(r"\\citet\{([^}]*)\}", lambda m: cite(m.group(1)), s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", r"`\1`", s)
    s = s.replace(r"\%", "%").replace(r"\&", "&").replace(r"\_", "_")
    s = s.replace("--", "–")
    return s


def parse_tabular(rows: list[str]) -> list[str]:
    cells = []
    for r in rows:
        r = r.strip()
        if not r or r.startswith(r"\hline"):
            continue
        r = r.rstrip("\\").rstrip()
        if r.endswith(r"\\"):
            r = r[:-2]
        parts = [inline(c.strip()) for c in r.split("&")]
        cells.append(parts)
    if not cells:
        return []
    n = len(cells[0])
    md = ["| " + " | ".join(cells[0]) + " |", "| " + " | ".join(["---"] * n) + " |"]
    for row in cells[1:]:
        while len(row) < n:
            row.append("")
        md.append("| " + " | ".join(row) + " |")
    return md


def main() -> int:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    i = 0
    in_enum = False
    document_commence = False
    while i < len(lines):
        ln = lines[i]
        st = ln.strip()

        # Saut du préambule LaTeX : rien n'est émis tant que \begin{document}
        # n'a pas été rencontré (écarte \documentclass, \usepackage, \hypersetup…).
        if not document_commence:
            if st == r"\begin{document}":
                document_commence = True
            i += 1
            continue

        if st.startswith(r"\title{"):
            out += ["# " + inline(re.search(r"\\title\{(.*)\}", st).group(1)), ""]
        elif st.startswith(r"\author{"):
            out += [inline(re.search(r"\\author\{(.*)\}", st).group(1)), ""]
        elif st.startswith(r"\date{"):
            out += [inline(re.search(r"\\date\{(.*)\}", st).group(1)), ""]
        elif st == r"\begin{abstract}":
            out += ["## Résumé", ""]
        elif st in (r"\end{abstract}", r"\appendix", r"\maketitle", r"\end{document}"):
            pass
        elif st.startswith(r"\bibliographystyle{") or st.startswith(r"\bibliography{"):
            pass
        elif st.startswith(r"\section{"):
            out += ["", "## " + inline(re.search(r"\\section\{(.*)\}", st).group(1)), ""]
        elif st.startswith(r"\subsection{"):
            out += ["", "### " + inline(re.search(r"\\subsection\{(.*)\}", st).group(1)), ""]
        elif st == r"\begin{enumerate}":
            in_enum = True
        elif st == r"\end{enumerate}":
            in_enum = False; out.append("")
        elif st.startswith(r"\item"):
            out.append("1. " + inline(st[len(r"\item"):].strip()))
        elif st == r"\begin{center}":
            pass
        elif st == r"\end{center}":
            pass
        elif st.startswith(r"\begin{tabular}"):
            rows = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(r"\end{tabular}"):
                rows.append(lines[i]); i += 1
            out += [""] + parse_tabular(rows) + [""]
        elif st == r"\[":
            math = []
            i += 1
            while i < len(lines) and lines[i].strip() != r"\]":
                math.append(lines[i].strip()); i += 1
            out += ["", "```text", *math, "```", ""]
        elif st == "":
            out.append("")
        else:
            out.append(inline(ln))
        i += 1

    # frontmatter + bandeau + lien PDF
    header = [
        "---",
        "id: PAPER",
        "title: Papier méthodologique",
        "sidebar_label: Papier (méthodologie)",
        "---",
        "",
        "import useBaseUrl from '@docusaurus/useBaseUrl';",
        "",
        ":::info Version publiable",
        "Working paper méthodologique, **aligné sur l'application**. "
        f"<a href={{useBaseUrl('{PDF_REL}')}} target=\"_blank\" rel=\"noopener\">Télécharger le PDF</a>"
        " · source LaTeX : `paper/main.tex`.",
        ":::",
        "",
    ]
    body = "\n".join(out)
    body = re.sub(r"\n{3,}", "\n\n", body)
    OUT.write_text("\n".join(header) + body + "\n", encoding="utf-8")
    print(f"Généré : {OUT.relative_to(ROOT)} ({len(body)} caractères)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
