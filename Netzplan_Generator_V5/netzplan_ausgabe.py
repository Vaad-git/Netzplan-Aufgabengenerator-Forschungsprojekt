"""Erstellt eine SVG-Grafik mit dem Graphviz-Programm 'dot'."""

from pathlib import Path
import subprocess


def netzplan_ausgeben(netzplan, dateiname="ausgaben/netzplan.svg"):
    """Schreibt den Netzplan als DOT-Text und lässt Graphviz die SVG-Datei erzeugen."""

    zeilen = [
        "digraph Netzplan {",
        '  graph [rankdir="LR", bgcolor="white", nodesep="0.5", ranksep="0.8"];',
        '  node [shape="box", style="rounded,filled", fontname="Arial"];',
        '  edge [arrowsize="0.8"];',
    ]

    starts = set(netzplan["startvorgaenge"])
    enden = set(netzplan["endvorgaenge"])

    # Gleiche Ebenen werden in der Grafik nebeneinander angeordnet.
    for stufe in netzplan["stufen"]:
        zeilen.append("  { rank=same; " + "; ".join(f'"{name}"' for name in stufe) + "; }")

    for name, daten in netzplan["vorgaenge"].items():
        if name in starts:
            farbe = "#d9f2df"
        elif name in enden:
            farbe = "#ffe8cc"
        else:
            farbe = "#e5e7eb"
        label = f'{name}\\nDauer: {daten["dauer"]}'
        zeilen.append(f'  "{name}" [label="{label}", fillcolor="{farbe}"];')

    for kante in netzplan["kanten"]:
        farbe = "#2563eb" if kante["art"] == "Strukturergaenzung" else "#475569"
        zeilen.append(
            f'  "{kante["vorgaenger"]}" -> "{kante["nachfolger"]}" [color="{farbe}"];'
        )

    zeilen.append("}")
    dot_text = "\n".join(zeilen)

    ziel = Path(dateiname)
    ziel.parent.mkdir(parents=True, exist_ok=True)

    # Graphviz ist ein Systemprogramm und wird direkt aufgerufen.
    subprocess.run(
        ["dot", "-Tsvg", "-o", str(ziel)],
        input=dot_text,
        text=True,
        check=True,
        capture_output=True,
    )

    return ziel
