from generator import netzplan_generieren
from netzplan_ausgabe import netzplan_ausgeben
from aufgabenstellung import aufgabenstellung_generieren


if __name__ == "__main__":
    # Netzplan einmal erzeugen
    plan = netzplan_generieren()

    # Grafik aus genau diesem Netzplan erstellen
    datei = netzplan_ausgeben(plan)

    print("Netzplan wurde erzeugt.")
    print("Vorgänge:", plan["vorgangszahl"])
    print("Kanten:", plan["anzahl_kanten"])
    print("Grafik:", datei.resolve())

    # Aufgabenstellung aus demselben Netzplan erstellen
    print()
    print(aufgabenstellung_generieren(plan))