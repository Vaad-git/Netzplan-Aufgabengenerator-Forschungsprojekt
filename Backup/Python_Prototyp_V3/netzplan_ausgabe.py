
from graphviz import Digraph
from pathlib import Path


def netzplan_ausgeben(stufen, kanten, vorgaenge):

    graph = Digraph("Netzplan", format="svg", engine="dot")

    # Allgemeine Darstellung
    graph.attr(rankdir="LR", splines="polyline", nodesep="0.5", ranksep="1")
    graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fillcolor="lightblue",
        fontname="Arial"
    )

    # Vorgänge nach Ebenen anordnen
    for i, stufe in enumerate(stufen):

        with graph.subgraph(name=f"cluster_ebene_{i}") as ebene:

            ebene.attr(
                label=f"Ebene {i + 1}",
                rank="same",
                style="rounded",
                color="lightgrey"
            )

            for kennung in stufe:
                dauer = vorgaenge[kennung]["dauer"]
                ebene.node(kennung, label=f"{kennung}\nDauer: {dauer}")

    # Abhängigkeiten einzeichnen
    for vorgaenger, nachfolger in kanten:
        graph.edge(vorgaenger, nachfolger)

    # Ausgabeordner erstellen
    ausgabe_ordner = Path(__file__).resolve().parent / "ausgaben"
    ausgabe_ordner.mkdir(exist_ok=True)

    # Netzplan erstellen und öffnen
    graph.render(
        filename="netzplan",
        directory=str(ausgabe_ordner),
        cleanup=True,
        view=True
    )