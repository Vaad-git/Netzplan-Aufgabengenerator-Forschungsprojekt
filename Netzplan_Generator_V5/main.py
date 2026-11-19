"""Lokaler Testlauf: Netzplan erzeugen und als SVG speichern."""

from generator import netzplan_generieren
from netzplan_ausgabe import netzplan_ausgeben


if __name__ == "__main__":
    plan = netzplan_generieren()
    datei = netzplan_ausgeben(plan)

    print("Netzplan wurde erzeugt.")
    print("Vorgänge:", plan["vorgangszahl"])
    print("Kanten:", plan["anzahl_kanten"])
    print("Startvorgänge:", plan["startvorgaenge"])
    print("Endvorgänge:", plan["endvorgaenge"])
    print("Verzweigungen:", plan["anzahl_verzweigungen"])
    print("Zusammenführungen:", plan["anzahl_zusammenfuehrungen"])
    print("Ebenen:", plan["stufen"])
    print("Grafik:", datei.resolve())
