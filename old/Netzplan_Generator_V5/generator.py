"""Einfacher Netzplangenerator mit Collection-Zusammenführung."""

import math
import random


# ============================================================
# 1. SCHWIERIGKEITSPROFILE
# ============================================================

SCHWIERIGKEITSPROFILE = {
    "Einfach": {
        "vorgangszahl": (6, 8),
        "dauer": (1, 5),
        "startvorgaenge": (1, 2),
        "endvorgaenge": (1, 2),
        "verzweigungen": (1, 2),
        "zusammenfuehrungen": (1, 2),
        "max_vorgaenger": 3,
        "max_nachfolger": 3,
    }
}


# ============================================================
# 2. HILFSFUNKTIONEN
# ============================================================


def grade_berechnen(knoten, kanten):
    """Zählt für jeden Vorgang die direkten Vorgänger und Nachfolger."""

    vorgaenger = {knotenname: 0 for knotenname in knoten}
    nachfolger = {knotenname: 0 for knotenname in knoten}

    for von, nach in kanten:
        nachfolger[von] += 1
        vorgaenger[nach] += 1

    return vorgaenger, nachfolger


def struktur_zaehlen(knoten, kanten):
    """Zählt Verzweigungs- und Zusammenführungsvorgänge."""

    vorgaenger, nachfolger = grade_berechnen(knoten, kanten)

    verzweigungen = sum(1 for wert in nachfolger.values() if wert >= 2)
    zusammenfuehrungen = sum(1 for wert in vorgaenger.values() if wert >= 2)

    return verzweigungen, zusammenfuehrungen, vorgaenger, nachfolger


def parameter_sind_moeglich(startzahl, endzahl, verzweigungen, zusammenfuehrungen,
                            max_vorgaenger, max_nachfolger):
    """Prüft einfache mathematische Bedingungen für die Profilwerte."""

    if startzahl > 1 and max_vorgaenger < 2:
        return False
    if endzahl > 1 and max_nachfolger < 2:
        return False
    if verzweigungen > 0 and max_nachfolger < 2:
        return False
    if zusammenfuehrungen > 0 and max_vorgaenger < 2:
        return False

    # Mehrere Enden benötigen genügend Verzweigungen.
    minimum_verzweigungen = math.ceil((endzahl - 1) / (max_nachfolger - 1)) if endzahl > 1 else 0
    # Mehrere Starts benötigen genügend Zusammenführungen.
    minimum_zusammenfuehrungen = math.ceil((startzahl - 1) / (max_vorgaenger - 1)) if startzahl > 1 else 0

    if verzweigungen < minimum_verzweigungen:
        return False
    if zusammenfuehrungen < minimum_zusammenfuehrungen:
        return False

    # Notwendige Grad-Bedingung für einen zusammenhängenden gerichteten Graphen.
    kleinster_unterschied = verzweigungen - zusammenfuehrungen * (max_vorgaenger - 1)
    groesster_unterschied = verzweigungen * (max_nachfolger - 1) - zusammenfuehrungen
    benoetigter_unterschied = endzahl - startzahl

    return kleinster_unterschied <= benoetigter_unterschied <= groesster_unterschied


# ============================================================
# 3. COLLECTIONS ZUSAMMENFÜHREN
# ============================================================


def collections_zusammenfuehren(knoten, rang, startzahl, endzahl,
                                 soll_verzweigungen, soll_zusammenfuehrungen,
                                 max_vorgaenger, max_nachfolger):
    """Verbindet alle einzelnen Collections zu einer gemeinsamen Collection.

    Jeder Vorgang startet in einer eigenen Collection. Pro Schritt werden
    zwei Collections durch genau eine gerichtete Kante verbunden und vereinigt.
    """

    anzahl_schritte = len(knoten) - 1

    # So oft muss die Zahl der Start- und Endvorgänge durch eine Verbindung
    # jeweils um eins sinken.
    start_aufloesungen = len(knoten) - startzahl
    ende_aufloesungen = len(knoten) - endzahl

    # Eine Verbindung kann gleichzeitig einen Start und ein Ende auflösen.
    minimum_beide = max(0, start_aufloesungen + ende_aufloesungen - anzahl_schritte)
    maximum_beide = min(start_aufloesungen, ende_aufloesungen)

    moegliche_aufteilungen = list(range(minimum_beide, maximum_beide + 1))
    random.shuffle(moegliche_aufteilungen)

    for anzahl_beide in moegliche_aufteilungen:
        nur_start = start_aufloesungen - anzahl_beide
        nur_ende = ende_aufloesungen - anzahl_beide
        weder_noch = anzahl_schritte - anzahl_beide - nur_start - nur_ende

        restliche_schrittarten = (
            ["NUR_START"] * nur_start
            + ["NUR_ENDE"] * nur_ende
            + ["KEINES"] * weder_noch
        )
        random.shuffle(restliche_schrittarten)
        schrittarten = ["BEIDE"] * anzahl_beide + restliche_schrittarten

        # Die Zusammenführungen werden bei Bedarf zurückverfolgt. Dadurch
        # kann eine ungünstige zufällige Auswahl verworfen werden.
        bereits_versuchte_stellungen = set()

        def weiterbauen(collections, kanten, schritt):
            if schritt == anzahl_schritte:
                return kanten if len(collections) == 1 else None

            # Gleiche Zwischenstände müssen nicht mehrfach geprüft werden.
            stellung = (
                schritt,
                tuple(sorted(tuple(sorted(c)) for c in collections)),
                tuple(sorted(kanten)),
            )
            if stellung in bereits_versuchte_stellungen:
                return None
            bereits_versuchte_stellungen.add(stellung)

            vorgaenger, nachfolger = grade_berechnen(knoten, kanten)
            verzweigungen, zusammenfuehrungen, _, _ = struktur_zaehlen(knoten, kanten)
            art = schrittarten[schritt]
            kandidaten = []

            for links in collections:
                for rechts in collections:
                    if links is rechts:
                        continue

                    for von in links:
                        for nach in rechts:
                            # Kanten dürfen nur in topologischer Richtung verlaufen.
                            if rang[von] >= rang[nach]:
                                continue
                            if nachfolger[von] >= max_nachfolger:
                                continue
                            if vorgaenger[nach] >= max_vorgaenger:
                                continue

                            # Diese Schrittart steuert die Anzahl der Starts/Enden.
                            if art in ("BEIDE", "NUR_START") and vorgaenger[nach] != 0:
                                continue
                            if art in ("NUR_ENDE", "KEINES") and vorgaenger[nach] == 0:
                                continue
                            if art in ("BEIDE", "NUR_ENDE") and nachfolger[von] != 0:
                                continue
                            if art in ("NUR_START", "KEINES") and nachfolger[von] == 0:
                                continue

                            # Die Grundstruktur darf die gewünschten Zahlen
                            # an Verzweigungen und Zusammenführungen nicht überschreiten.
                            neue_verzweigung = int(nachfolger[von] == 1)
                            neue_zusammenfuehrung = int(vorgaenger[nach] == 1)

                            if verzweigungen + neue_verzweigung > soll_verzweigungen:
                                continue
                            if zusammenfuehrungen + neue_zusammenfuehrung > soll_zusammenfuehrungen:
                                continue

                            kandidaten.append((von, nach, links, rechts))

            random.shuffle(kandidaten)

            for von, nach, links, rechts in kandidaten:
                neue_collection = links | rechts
                neue_collections = [c for c in collections if c is not links and c is not rechts]
                neue_collections.append(neue_collection)

                ergebnis = weiterbauen(neue_collections, kanten + [(von, nach)], schritt + 1)
                if ergebnis is not None:
                    return ergebnis

            return None

        ergebnis = weiterbauen([{name} for name in knoten], [], 0)
        if ergebnis is not None:
            return ergebnis

    return None


# ============================================================
# 4. FEHLENDE VERZWEIGUNGEN / ZUSAMMENFÜHRUNGEN ERGÄNZEN
# ============================================================


def struktur_ergaenzen(knoten, kanten, rang, startvorgaenge, endvorgaenge,
                       soll_verzweigungen, soll_zusammenfuehrungen,
                       max_vorgaenger, max_nachfolger):
    """Ergänzt nur die Kanten, die für die Zielzahlen noch benötigt werden."""

    startmenge = set(startvorgaenge)
    endmenge = set(endvorgaenge)
    bereits_versuchte_stellungen = set()

    def suchen(aktuelle_kanten):
        verzweigungen, zusammenfuehrungen, vorgaenger, nachfolger = struktur_zaehlen(
            knoten, aktuelle_kanten
        )

        if (verzweigungen == soll_verzweigungen
                and zusammenfuehrungen == soll_zusammenfuehrungen):
            return aktuelle_kanten

        stellung = tuple(sorted(aktuelle_kanten))
        if stellung in bereits_versuchte_stellungen:
            return None
        bereits_versuchte_stellungen.add(stellung)

        kandidaten = []
        vorhandene_kanten = set(aktuelle_kanten)

        for von in knoten:
            if von in endmenge or nachfolger[von] >= max_nachfolger:
                continue

            for nach in knoten:
                if nach in startmenge or rang[von] >= rang[nach]:
                    continue
                if (von, nach) in vorhandene_kanten:
                    continue
                if vorgaenger[nach] >= max_vorgaenger:
                    continue

                neue_verzweigung = int(nachfolger[von] == 1)
                neue_zusammenfuehrung = int(vorgaenger[nach] == 1)

                if verzweigungen + neue_verzweigung > soll_verzweigungen:
                    continue
                if zusammenfuehrungen + neue_zusammenfuehrung > soll_zusammenfuehrungen:
                    continue
                if not (neue_verzweigung or neue_zusammenfuehrung):
                    continue

                kandidaten.append((von, nach))

        random.shuffle(kandidaten)

        for kante in kandidaten:
            ergebnis = suchen(aktuelle_kanten + [kante])
            if ergebnis is not None:
                return ergebnis

        return None

    return suchen(kanten.copy())


# ============================================================
# 5. EBENEN UND VALIDIERUNG
# ============================================================


def ebenen_ableiten(knoten, kanten, rang):
    """Berechnet die Ebenen ganz am Ende anhand des längsten Weges."""

    nachfolger = {name: [] for name in knoten}
    for von, nach in kanten:
        nachfolger[von].append(nach)

    sortierte_knoten = sorted(knoten, key=lambda name: rang[name])
    abstand = {name: 0 for name in knoten}

    for name in sortierte_knoten:
        for nach in nachfolger[name]:
            abstand[nach] = max(abstand[nach], abstand[name] + 1)

    stufen = [[] for _ in range(max(abstand.values()) + 1)]
    for name in knoten:
        stufen[abstand[name]].append(name)

    for stufe in stufen:
        stufe.sort()

    return stufen


def netzplan_validieren(netzplan):
    """Prüft die wichtigsten Regeln des fertigen Netzplans."""

    knoten = list(netzplan["vorgaenge"])
    kanten = [(k["vorgaenger"], k["nachfolger"]) for k in netzplan["kanten"]]

    if len(kanten) != len(set(kanten)):
        raise ValueError("Doppelte Kanten sind nicht erlaubt.")

    for von, nach in kanten:
        if von not in knoten or nach not in knoten or von == nach:
            raise ValueError("Eine Kante ist ungültig.")

    vorgaenger, nachfolger = grade_berechnen(knoten, kanten)

    starts = sorted(name for name in knoten if vorgaenger[name] == 0)
    enden = sorted(name for name in knoten if nachfolger[name] == 0)

    if not starts or not enden:
        raise ValueError("Der Netzplan benötigt mindestens einen Start und ein Ende.")

    if starts != sorted(netzplan["startvorgaenge"]):
        raise ValueError("Die Startvorgänge stimmen nicht mit den Kanten überein.")
    if enden != sorted(netzplan["endvorgaenge"]):
        raise ValueError("Die Endvorgänge stimmen nicht mit den Kanten überein.")

    if any(wert > netzplan["max_vorgaenger"] for wert in vorgaenger.values()):
        raise ValueError("Die maximale Vorgängerzahl wurde überschritten.")
    if any(wert > netzplan["max_nachfolger"] for wert in nachfolger.values()):
        raise ValueError("Die maximale Nachfolgerzahl wurde überschritten.")

    if netzplan["anzahl_verzweigungen"] != sum(wert >= 2 for wert in nachfolger.values()):
        raise ValueError("Die Verzweigungsanzahl ist nicht korrekt.")
    if netzplan["anzahl_zusammenfuehrungen"] != sum(wert >= 2 for wert in vorgaenger.values()):
        raise ValueError("Die Zusammenführungsanzahl ist nicht korrekt.")
    if netzplan["anzahl_verzweigungen"] != netzplan["soll_verzweigungen"]:
        raise ValueError("Die gewünschte Verzweigungsanzahl wurde nicht erreicht.")
    if netzplan["anzahl_zusammenfuehrungen"] != netzplan["soll_zusammenfuehrungen"]:
        raise ValueError("Die gewünschte Zusammenführungsanzahl wurde nicht erreicht.")
    if len(starts) != netzplan["soll_startvorgaenge"]:
        raise ValueError("Die gewünschte Anzahl der Startvorgänge wurde nicht erreicht.")
    if len(enden) != netzplan["soll_endvorgaenge"]:
        raise ValueError("Die gewünschte Anzahl der Endvorgänge wurde nicht erreicht.")

    # Eine topologische Sortierung prüft, dass keine gerichteten Kreisläufe vorliegen.
    rest_vorgaenger = vorgaenger.copy()
    sortiert = []
    warteschlange = list(starts)
    while warteschlange:
        aktuell = warteschlange.pop(0)
        sortiert.append(aktuell)
        for von, nach in kanten:
            if von == aktuell:
                rest_vorgaenger[nach] -= 1
                if rest_vorgaenger[nach] == 0:
                    warteschlange.append(nach)
    if len(sortiert) != len(knoten):
        raise ValueError("Der Netzplan enthält einen gerichteten Kreislauf.")

    # Prüfen, ob alle Vorgänge von einem Start erreichbar sind.
    adjazenz = {name: [] for name in knoten}
    for von, nach in kanten:
        adjazenz[von].append(nach)

    erreichbar = set()
    warteschlange = list(starts)
    while warteschlange:
        aktuell = warteschlange.pop()
        if aktuell not in erreichbar:
            erreichbar.add(aktuell)
            warteschlange.extend(adjazenz[aktuell])

    if erreichbar != set(knoten):
        raise ValueError("Nicht alle Vorgänge sind von einem Startvorgang erreichbar.")

    # Prüfen, ob alle Vorgänge mindestens ein Ende erreichen.
    rueckwaerts = {name: [] for name in knoten}
    for von, nach in kanten:
        rueckwaerts[nach].append(von)

    erreichbar = set()
    warteschlange = list(enden)
    while warteschlange:
        aktuell = warteschlange.pop()
        if aktuell not in erreichbar:
            erreichbar.add(aktuell)
            warteschlange.extend(rueckwaerts[aktuell])

    if erreichbar != set(knoten):
        raise ValueError("Nicht alle Vorgänge führen zu einem Endvorgang.")

    # Die Collections müssen am Ende zu einem gemeinsamen Netz gehören.
    ungerichtet = {name: [] for name in knoten}
    for von, nach in kanten:
        ungerichtet[von].append(nach)
        ungerichtet[nach].append(von)

    verbunden = set()
    warteschlange = [knoten[0]]
    while warteschlange:
        aktuell = warteschlange.pop()
        if aktuell not in verbunden:
            verbunden.add(aktuell)
            warteschlange.extend(ungerichtet[aktuell])

    if verbunden != set(knoten):
        raise ValueError("Der Netzplan besteht aus mehreren unverbundenen Teilen.")

    # Jeder Vorgang muss genau einer berechneten Ebene zugeordnet sein.
    stufen_vorgaenge = [name for stufe in netzplan["stufen"] for name in stufe]
    if len(stufen_vorgaenge) != len(knoten) or set(stufen_vorgaenge) != set(knoten):
        raise ValueError("Die Ebenenzuordnung ist unvollständig.")


# ============================================================
# 6. ÖFFENTLICHE GENERATORFUNKTION
# ============================================================


def netzplan_generieren(schwierigkeitsgrad="Einfach"):
    """Erzeugt einen Netzplan anhand des gewählten Schwierigkeitsprofils."""

    if schwierigkeitsgrad not in SCHWIERIGKEITSPROFILE:
        raise ValueError("Unbekannter Schwierigkeitsgrad.")

    profil = SCHWIERIGKEITSPROFILE[schwierigkeitsgrad]

    # Mehrere zufällige Anläufe, falls eine zufällige Auswahl nicht aufgeht.
    for _ in range(200):
        anzahl = random.randint(*profil["vorgangszahl"])
        knoten = [chr(ord("A") + i) for i in range(anzahl)]

        startzahl = random.randint(*profil["startvorgaenge"])
        endzahl = random.randint(*profil["endvorgaenge"])

        # Nur Kombinationen verwenden, die zu den Profilgrenzen passen.
        moegliche_zielwerte = []
        for verzweigungen in range(profil["verzweigungen"][0], profil["verzweigungen"][1] + 1):
            for zusammenfuehrungen in range(profil["zusammenfuehrungen"][0], profil["zusammenfuehrungen"][1] + 1):
                if parameter_sind_moeglich(
                    startzahl, endzahl, verzweigungen, zusammenfuehrungen,
                    profil["max_vorgaenger"], profil["max_nachfolger"]
                ):
                    moegliche_zielwerte.append((verzweigungen, zusammenfuehrungen))

        if not moegliche_zielwerte:
            continue

        soll_verzweigungen, soll_zusammenfuehrungen = random.choice(moegliche_zielwerte)

        # Die topologische Reihenfolge wird zufällig festgelegt.
        rangfolge = knoten.copy()
        random.shuffle(rangfolge)
        rang = {name: index for index, name in enumerate(rangfolge)}

        # Zuerst die einzelnen Collections zu einer gemeinsamen Collection verbinden.
        grundkanten = collections_zusammenfuehren(
            knoten, rang, startzahl, endzahl,
            soll_verzweigungen, soll_zusammenfuehrungen,
            profil["max_vorgaenger"], profil["max_nachfolger"]
        )

        if grundkanten is None:
            continue

        vorgaenger, nachfolger = grade_berechnen(knoten, grundkanten)
        startvorgaenge = sorted(name for name in knoten if vorgaenger[name] == 0)
        endvorgaenge = sorted(name for name in knoten if nachfolger[name] == 0)

        # Falls die Grundstruktur noch nicht genug Branches/Merges enthält,
        # werden nur die dafür benötigten Kanten ergänzt.
        kanten = struktur_ergaenzen(
            knoten, grundkanten, rang, startvorgaenge, endvorgaenge,
            soll_verzweigungen, soll_zusammenfuehrungen,
            profil["max_vorgaenger"], profil["max_nachfolger"]
        )

        if kanten is None:
            continue

        vorgaenger, nachfolger = grade_berechnen(knoten, kanten)
        startvorgaenge = sorted(name for name in knoten if vorgaenger[name] == 0)
        endvorgaenge = sorted(name for name in knoten if nachfolger[name] == 0)
        stufen = ebenen_ableiten(knoten, kanten, rang)

        vorgaenge = {
            name: {
                "bezeichnung": name,
                "dauer": random.randint(*profil["dauer"]),
                "ebene": next(index + 1 for index, stufe in enumerate(stufen) if name in stufe),
            }
            for name in knoten
        }

        verzweigungen, zusammenfuehrungen, _, _ = struktur_zaehlen(knoten, kanten)

        netzplan = {
            "schwierigkeitsgrad": schwierigkeitsgrad,
            "vorgangszahl": anzahl,
            "anzahl_kanten": len(kanten),
            "vorgaenge": vorgaenge,
            "kanten": [
                {
                    "vorgaenger": von,
                    "nachfolger": nach,
                    "art": "Grundstruktur" if (von, nach) in grundkanten else "Strukturergaenzung",
                }
                for von, nach in kanten
            ],
            "startvorgaenge": startvorgaenge,
            "endvorgaenge": endvorgaenge,
            "anzahl_verzweigungen": verzweigungen,
            "anzahl_zusammenfuehrungen": zusammenfuehrungen,
            "soll_startvorgaenge": startzahl,
            "soll_endvorgaenge": endzahl,
            "soll_verzweigungen": soll_verzweigungen,
            "soll_zusammenfuehrungen": soll_zusammenfuehrungen,
            "max_vorgaenger": profil["max_vorgaenger"],
            "max_nachfolger": profil["max_nachfolger"],
            "stufen": stufen,
            "stufenzahl": len(stufen),
        }

        # Die Validierung bleibt als einfache Sicherheitsprüfung erhalten.
        netzplan_validieren(netzplan)
        return netzplan

    raise RuntimeError("Es konnte kein gültiger Netzplan erzeugt werden. Bitte erneut versuchen.")
