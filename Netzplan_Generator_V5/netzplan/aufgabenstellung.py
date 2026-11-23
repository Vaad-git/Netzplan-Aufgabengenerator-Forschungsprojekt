"""Erzeugt eine strukturierte Aufgabenstellung aus einem vorhandenen Netzplan."""


def _vorgang_anzeigen(name, vorgaenge, bezeichnungen):
    """Verbindet die technische ID mit dem lesbaren KI-Namen."""

    bezeichnung = bezeichnungen.get(name)
    if bezeichnung:
        return f"{bezeichnung} [{name}] ({vorgaenge[name]['dauer']} Zeiteinheiten)"
    return f"{name} ({vorgaenge[name]['dauer']} Zeiteinheiten)"


def _vorgaenge_auflisten(namen, vorgaenge, bezeichnungen):
    """Formatiert beliebig viele Vorgänger mit Namen und Dauer."""

    beschreibungen = [
        _vorgang_anzeigen(name, vorgaenge, bezeichnungen)
        for name in namen
    ]

    if len(beschreibungen) == 1:
        return beschreibungen[0]

    if len(beschreibungen) == 2:
        return f"{beschreibungen[0]} und {beschreibungen[1]}"

    return ", ".join(beschreibungen[:-1]) + " und " + beschreibungen[-1]


def aufgabenstellung_generieren(netzplan, bezeichnungen=None):
    """Erzeugt eine schriftliche Aufgabenstellung aus Vorgängen und Kanten.

    Die KI-Bezeichnungen sind optional. Ohne sie werden wie bisher die IDs
    A, B, C usw. verwendet. Die Funktion verändert den Netzplan nicht.
    """

    vorgaenge = netzplan["vorgaenge"]
    kanten = netzplan["kanten"]
    bezeichnungen = bezeichnungen or {}

    # Für jeden Vorgang eine zunächst leere Liste direkter Vorgänger anlegen.
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
        "",
    ]

    # Jeden Vorgang einmal mit technischer ID und lesbarer Bezeichnung beschreiben.
    for name, daten in vorgaenge.items():
        vorgangstext = _vorgang_anzeigen(name, vorgaenge, bezeichnungen)
        vorgaenger = sorted(vorgaenger_pro_vorgang[name])

        if not vorgaenger:
            zeilen.append(
                f"- Vorgang {vorgangstext} kann direkt zu Projektbeginn begonnen werden."
            )
        else:
            vorgaenger_text = _vorgaenge_auflisten(
                vorgaenger, vorgaenge, bezeichnungen
            )
            zeilen.append(
                f"- Vorgang {vorgangstext} kann erst nach Abschluss von "
                f"{vorgaenger_text} beginnen."
            )

    zeilen.extend([
        "",
        "Aufgabe:",
        "Übertragen Sie die Angaben in eine Vorgängertabelle. "
        "Erstellen Sie daraus den Netzplan und berechnen Sie anschließend "
        "FAZ, FEZ, SAZ, SEZ und den Gesamtpuffer für alle Vorgänge.",
    ])

    return "\n".join(zeilen)
