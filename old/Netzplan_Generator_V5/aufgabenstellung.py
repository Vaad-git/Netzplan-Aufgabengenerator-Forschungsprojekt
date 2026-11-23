"""Erzeugt eine textuelle Aufgabenstellung aus einem vorhandenen Netzplan."""


def _vorgaenge_auflisten(namen, vorgaenge):
    """Formatiert beliebig viele Vorgänge mit ihrer Dauer als Textliste."""

    beschreibungen = []

    for name in namen:
        dauer = vorgaenge[name]["dauer"]
        beschreibungen.append(f"{name} ({dauer} Zeiteinheiten)")

    if len(beschreibungen) == 1:
        return beschreibungen[0]

    if len(beschreibungen) == 2:
        return f"{beschreibungen[0]} und {beschreibungen[1]}"

    return ", ".join(beschreibungen[:-1]) + " und " + beschreibungen[-1]


def aufgabenstellung_generieren(netzplan):
    """Erzeugt eine schriftliche Aufgabenstellung aus Vorgängen und Kanten."""

    vorgaenge = netzplan["vorgaenge"]
    kanten = netzplan["kanten"]

    # Für jeden Vorgang eine zunächst leere Liste seiner direkten Vorgänger anlegen.
    vorgaenger_pro_vorgang = {name: [] for name in vorgaenge}

    # Die Vorgängerinformationen aus den vorhandenen Kanten übernehmen.
    for kante in kanten:
        von = kante["vorgaenger"]
        nach = kante["nachfolger"]
        vorgaenger_pro_vorgang[nach].append(von)

    zeilen = [
        "AUFGABENSTELLUNG",
        "",
        "Für das Projekt gelten folgende Vorgänge und Abhängigkeiten:",
        ""
    ]

    # Jeden Vorgang einmal beschreiben.
    for name, daten in vorgaenge.items():
        dauer = daten["dauer"]
        vorgaenger = sorted(vorgaenger_pro_vorgang[name])

        if not vorgaenger:
            zeilen.append(
                f"- Vorgang {name} ({dauer} Zeiteinheiten) "
                "kann direkt zu Projektbeginn begonnen werden."
            )
        else:
            vorgaenger_text = _vorgaenge_auflisten(vorgaenger, vorgaenge)

            zeilen.append(
                f"- Vorgang {name} ({dauer} Zeiteinheiten) "
                f"kann erst nach Abschluss von {vorgaenger_text} beginnen."
            )

    zeilen.extend([
        "",
        "Aufgabe:",
        "Übertragen Sie die Angaben in eine Vorgängertabelle. "
        "Erstellen Sie daraus den Netzplan und berechnen Sie anschließend "
        "FAZ, FEZ, SAZ, SEZ und den Gesamtpuffer für alle Vorgänge."
    ])

    return "\n".join(zeilen)


if __name__ == "__main__":
    # Beispieldatensatz mit einer Zusammenführung aus drei Vorgängern.
    beispiel_plan = {
        "vorgaenge": {
            "A": {"dauer": 6},
            "B": {"dauer": 3},
            "C": {"dauer": 5},
            "D": {"dauer": 4},
            "E": {"dauer": 2},
            "F": {"dauer": 4},
            "G": {"dauer": 2},
        },
        "kanten": [
            {"vorgaenger": "A", "nachfolger": "C"},
            {"vorgaenger": "A", "nachfolger": "D"},
            {"vorgaenger": "B", "nachfolger": "E"},
            {"vorgaenger": "C", "nachfolger": "F"},
            {"vorgaenger": "D", "nachfolger": "F"},
            {"vorgaenger": "E", "nachfolger": "F"},
            {"vorgaenger": "F", "nachfolger": "G"},
        ],
    }

    print(aufgabenstellung_generieren(beispiel_plan))