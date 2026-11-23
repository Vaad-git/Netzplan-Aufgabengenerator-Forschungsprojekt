
"""Berechnet die Musterlösung und vergleicht sie mit einer Schülerlösung."""

# Die fünf Werte, die für jeden Vorgang berechnet und verglichen werden.
WERTE = ("FAZ", "FEZ", "SAZ", "SEZ", "GP")


# ============================================================
# 1. MUSTERLÖSUNG BERECHNEN
# ============================================================

def musterloesung_berechnen(netzplan):
    """Berechnet FAZ, FEZ, SAZ, SEZ und Gesamtpuffer für alle Vorgänge."""

    vorgaenge = netzplan["vorgaenge"]
    kanten = netzplan["kanten"]

    if not vorgaenge:
        raise ValueError("Der Netzplan enthält keine Vorgänge.")

    # Für jeden Vorgang seine direkten Vorgänger und Nachfolger sammeln.
    vorgaenger = {name: [] for name in vorgaenge}
    nachfolger = {name: [] for name in vorgaenge}
    vorhandene_kanten = set()

    for kante in kanten:
        von = kante["vorgaenger"]
        nach = kante["nachfolger"]

        if von not in vorgaenge or nach not in vorgaenge or von == nach:
            raise ValueError("Der Netzplan enthält eine ungültige Kante.")

        if (von, nach) in vorhandene_kanten:
            raise ValueError("Der Netzplan enthält eine doppelte Kante.")

        vorhandene_kanten.add((von, nach))
        nachfolger[von].append(nach)
        vorgaenger[nach].append(von)

    # Prüfen, ob alle Vorgangsdauern gültige Zahlen sind.
    for name, daten in vorgaenge.items():
        dauer = daten["dauer"]

        if not isinstance(dauer, int) or dauer < 0:
            raise ValueError(
                f"Die Dauer von Vorgang {name} muss eine nichtnegative ganze Zahl sein."
            )

    # Eine topologische Reihenfolge der Vorgänge erstellen.
    # Dazu werden zuerst alle Vorgänge ohne Vorgänger aufgenommen.
    rest_vorgaenger = {
        name: len(vorgaenger[name]) for name in vorgaenge
    }

    warteschlange = [
        name for name in vorgaenge
        if rest_vorgaenger[name] == 0
    ]

    reihenfolge = []

    while warteschlange:
        aktuell = warteschlange.pop(0)
        reihenfolge.append(aktuell)

        for nach in nachfolger[aktuell]:
            rest_vorgaenger[nach] -= 1

            if rest_vorgaenger[nach] == 0:
                warteschlange.append(nach)

    # Wenn nicht alle Vorgänge aufgenommen wurden, liegt ein Kreislauf vor.
    if len(reihenfolge) != len(vorgaenge):
        raise ValueError("Der Netzplan enthält einen gerichteten Kreislauf.")

    # --------------------------------------------------------
    # VORWÄRTSRECHNUNG: FAZ und FEZ
    # --------------------------------------------------------

    ergebnisse = {}

    for name in reihenfolge:

        # Der FAZ entspricht dem größten FEZ aller direkten Vorgänger.
        # Startvorgänge haben den FAZ 0.
        faz = max(
            (ergebnisse[von]["FEZ"] for von in vorgaenger[name]),
            default=0
        )

        # Der FEZ ergibt sich aus FAZ plus Vorgangsdauer.
        fez = faz + vorgaenge[name]["dauer"]

        ergebnisse[name] = {
            "FAZ": faz,
            "FEZ": fez
        }

    # Die Projektdauer entspricht dem größten FEZ aller Endvorgänge.
    endvorgaenge = [
        name for name in vorgaenge
        if not nachfolger[name]
    ]

    projektdauer = max(
        ergebnisse[name]["FEZ"] for name in endvorgaenge
    )

    # --------------------------------------------------------
    # RÜCKWÄRTSRECHNUNG: SAZ und SEZ
    # --------------------------------------------------------

    for name in reversed(reihenfolge):

        # Bei Vorgängen mit Nachfolgern ist der SEZ
        # der kleinste SAZ-Wert aller direkten Nachfolger.
        if nachfolger[name]:
            sez = min(
                ergebnisse[nach]["SAZ"]
                for nach in nachfolger[name]
            )

        # Endvorgänge erhalten den gemeinsamen Projektendzeitpunkt.
        else:
            sez = projektdauer

        # Der SAZ ergibt sich aus SEZ minus Vorgangsdauer.
        saz = sez - vorgaenge[name]["dauer"]

        # Der Gesamtpuffer ist die Differenz aus SAZ und FAZ.
        gp = saz - ergebnisse[name]["FAZ"]

        ergebnisse[name].update({
            "SAZ": saz,
            "SEZ": sez,
            "GP": gp
        })

    return {
        "projektdauer": projektdauer,
        "vorgaenge": ergebnisse
    }


# ============================================================
# 2. SCHÜLERLÖSUNG VERGLEICHEN
# ============================================================

def _eingabewert_normalisieren(wert):
    """Wandelt eine Zahl als Text in eine ganze Zahl um."""

    if isinstance(wert, str):
        try:
            return int(wert.strip())
        except ValueError:
            return None

    return wert


def loesung_vergleichen(musterloesung, schuelerloesung):
    """Vergleicht jeden Schülerwert einzeln mit der Musterlösung."""

    muster_vorgaenge = musterloesung["vorgaenge"]
    schueler_vorgaenge = schuelerloesung.get("vorgaenge", {})

    ergebnisse = {}
    anzahl_richtig = 0
    anzahl_werte = len(muster_vorgaenge) * len(WERTE)

    # Alle Vorgänge der Musterlösung durchgehen.
    for name, musterwerte in muster_vorgaenge.items():

        # Falls ein Vorgang fehlt, ist seine Schülerlösung zunächst leer.
        schuelerwerte = schueler_vorgaenge.get(name, {})

        wert_ergebnisse = {}
        vorgang_richtig = 0

        # Jeden der fünf Werte einzeln vergleichen.
        for wert in WERTE:

            musterwert = musterwerte[wert]
            schuelerwert = _eingabewert_normalisieren(
                schuelerwerte.get(wert)
            )

            richtig = schuelerwert == musterwert

            wert_ergebnisse[wert] = {
                "muster": musterwert,
                "schueler": schuelerwert,
                "richtig": richtig
            }

            if richtig:
                anzahl_richtig += 1
                vorgang_richtig += 1

        ergebnisse[name] = {
            "werte": wert_ergebnisse,
            "anzahl_richtig": vorgang_richtig,
            "anzahl_werte": len(WERTE)
        }

    # Prüfen, ob der Schüler zusätzliche, unbekannte Vorgänge eingetragen hat.
    zusaetzliche_vorgaenge = sorted(
        set(schueler_vorgaenge) - set(muster_vorgaenge)
    )

    # Anteil der richtigen Werte berechnen.
    prozent = (
        round(anzahl_richtig / anzahl_werte * 100, 2)
        if anzahl_werte else 0.0
    )

    return {
        "vorgaenge": ergebnisse,
        "anzahl_richtig": anzahl_richtig,
        "anzahl_werte": anzahl_werte,
        "prozent_richtig": prozent,
        "zusaetzliche_vorgaenge": zusaetzliche_vorgaenge,
        "alles_korrekt": (
            anzahl_richtig == anzahl_werte
            and not zusaetzliche_vorgaenge
        )
    }
