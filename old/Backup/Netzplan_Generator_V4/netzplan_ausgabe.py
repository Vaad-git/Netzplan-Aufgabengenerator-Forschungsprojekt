from pathlib import Path

from graphviz import Digraph


def netzplan_ausgeben(stufen, kanten, vorgaenge):
    """Erstellt den Netzplan als SVG und öffnet die Datei.

    Die Datei ausgaben/netzplan.svg wird bei jedem Aufruf überschrieben,
    sodass nicht für jede Generierung eine neue SVG-Datei entsteht.
    """

    graph = Digraph("Netzplan", format="svg", engine="dot")

    graph.attr(
        rankdir="LR",
        splines="polyline",
        nodesep="0.55",
        ranksep="1.0",
        pad="0.25"
    )
    graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fillcolor="lightblue",
        color="#47728f",
        fontname="Arial",
        fontsize="11",
        margin="0.14,0.08"
    )
    graph.attr("edge", color="#536878", arrowsize="0.75")

    # Die Vorgänge werden entsprechend der vom Generator ermittelten
    # Ebenen auf derselben Graphviz-Rangstufe angeordnet.
    for index, stufe in enumerate(stufen):
        with graph.subgraph(name=f"cluster_ebene_{index}") as ebene:
            ebene.attr(
                label=f"Ebene {index + 1}",
                rank="same",
                style="rounded",
                color="lightgrey",
                fontname="Arial"
            )

            for kennung in stufe:
                dauer = vorgaenge[kennung]["dauer"]
                ebene.node(kennung, label=f"{kennung}\nDauer: {dauer}")

    for vorgaenger, nachfolger in kanten:
        graph.edge(vorgaenger, nachfolger)

    ausgabe_ordner = Path(__file__).resolve().parent / "ausgaben"
    ausgabe_ordner.mkdir(exist_ok=True)

    graph.render(
        filename="netzplan",
        directory=str(ausgabe_ordner),
        cleanup=True,
        view=True
    )
