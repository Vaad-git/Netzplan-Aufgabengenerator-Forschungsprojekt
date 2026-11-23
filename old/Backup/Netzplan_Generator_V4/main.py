import random
from collections import Counter, deque
from functools import lru_cache
from typing import TypedDict


# ============================================================
# 1. DATENTYPEN
# ============================================================


class Schwierigkeitsprofil(TypedDict):
    vorgangszahl: tuple[int, int]
    dauer: tuple[int, int]
    verzweigungen: tuple[int, int]
    zusammenfuehrungen: tuple[int, int]
    max_vorgaenge_pro_stufe: int
    optionale_zusatzkanten: tuple[int, int]


class Vorgang(TypedDict):
    bezeichnung: str
    dauer: int


class Netzplan(TypedDict):
    schwierigkeitsgrad: str
    vorgangszahl: int
    stufenzahl: int
    max_vorgaenge_pro_stufe: int
    anzahl_kanten: int
    anzahl_verzweigungen: int
    anzahl_zusammenfuehrungen: int
    anzahl_optionale_zusatzkanten: int
    anzahl_kanten_ueber_minimum: int
    soll_verzweigungen: int
    soll_zusammenfuehrungen: int
    max_tatsaechliche_vorgaenger: int
    max_tatsaechliche_nachfolger: int
    startvorgang: str
    endvorgang: str
    vorgaenge: dict[str, Vorgang]
    kanten: list[tuple[str, str]]
    stufen: list[list[str]]


# ============================================================
# 2. SCHWIERIGKEITSPROFILE
# ============================================================


schwierigkeitsprofile: dict[str, Schwierigkeitsprofil] = {
    "Einfach": {
        "vorgangszahl": (6, 8),
        "dauer": (1, 5),
        "verzweigungen": (1, 2),
        "zusammenfuehrungen": (1, 2),
        "max_vorgaenge_pro_stufe": 3,
        "optionale_zusatzkanten": (0, 2)
    }
}


# ============================================================
# 3. HILFSFUNKTIONEN FÜR DIE STRUKTURGENERIERUNG
# ============================================================


@lru_cache(maxsize=None)
def _gueltige_uebergangsmuster(anzahl_vorgaenger: int, anzahl_nachfolger: int):
    """Liefert mögliche Kantenmuster zwischen zwei kleinen Sammlungen.

    Jedes Element der linken Sammlung muss mindestens einen Nachfolger
    und jedes Element der rechten Sammlung mindestens einen Vorgänger haben.
    """

    # Alle möglichen Teilmengen der höchstens 3 x 3 Verbindungsmöglichkeiten.
    muster = []
    anzahl_moeglicher_kanten = anzahl_vorgaenger * anzahl_nachfolger

    for maske in range(1, 1 << anzahl_moeglicher_kanten):
        ausgewaehlte_kanten = [
            (i, j)
            for i in range(anzahl_vorgaenger)
            for j in range(anzahl_nachfolger)
            if maske & (1 << (i * anzahl_nachfolger + j))
        ]

        ausgangsgrade = [0] * anzahl_vorgaenger
        eingangsgrade = [0] * anzahl_nachfolger

        for i, j in ausgewaehlte_kanten:
            ausgangsgrade[i] += 1
            eingangsgrade[j] += 1

        if all(ausgangsgrade) and all(eingangsgrade):
            muster.append(tuple(ausgewaehlte_kanten))

    return tuple(muster)


def _sammlungen_erzeugen(
    vorgang_kennungen: list[str], max_vorgaenge_pro_stufe: int
) -> list[list[str]]:
    """Teilt die mittleren Vorgänge zufällig in Sammlungen von 1 bis max. 3 auf.

    Start- und Endvorgang bilden jeweils eine eigene Sammlung.
    Die Ebenenanzahl wird damit nicht separat festgelegt, sondern ergibt sich
    aus der Anzahl und Größe der Sammlungen.
    """

    startvorgang = vorgang_kennungen[0]
    endvorgang = vorgang_kennungen[-1]
    mittlere_vorgaenge = vorgang_kennungen[1:-1].copy()
    random.shuffle(mittlere_vorgaenge)

    sammlungen = [[startvorgang]]

    position = 0
    while position < len(mittlere_vorgaenge):
        rest = len(mittlere_vorgaenge) - position
        groesse = random.randint(1, min(max_vorgaenge_pro_stufe, rest))
        sammlungen.append(mittlere_vorgaenge[position:position + groesse])
        position += groesse

    sammlungen.append([endvorgang])
    return sammlungen


def _grundkanten_erzeugen(sammlungen: list[list[str]]) -> list[tuple[str, str]]:
    """Verbindet aufeinanderfolgende Sammlungen vollständig genug, damit
    jeder Vorgang einen Vorgänger und einen Nachfolger besitzt.
    """

    kanten = []

    for linke_sammlung, rechte_sammlung in zip(sammlungen, sammlungen[1:]):
        muster = _gueltige_uebergangsmuster(
            len(linke_sammlung), len(rechte_sammlung)
        )

        if not muster:
            raise ValueError("Für zwei Sammlungen konnte kein Verbindungsmuster gefunden werden.")

        ausgewaehltes_muster = random.choice(muster)

        for linker_index, rechter_index in ausgewaehltes_muster:
            kanten.append((
                linke_sammlung[linker_index],
                rechte_sammlung[rechter_index]
            ))

    return kanten


def _grade_ermitteln(vorgaenge: dict[str, Vorgang], kanten: list[tuple[str, str]]):
    """Zählt für jeden Vorgang seine Vorgänger und Nachfolger."""

    anzahl_vorgaenger = {kennung: 0 for kennung in vorgaenge}
    anzahl_nachfolger = {kennung: 0 for kennung in vorgaenge}

    for vorgaenger, nachfolger in kanten:
        anzahl_nachfolger[vorgaenger] += 1
        anzahl_vorgaenger[nachfolger] += 1

    return anzahl_vorgaenger, anzahl_nachfolger


def _strukturwerte_ermitteln(
    vorgaenge: dict[str, Vorgang], kanten: list[tuple[str, str]]
) -> tuple[int, int, dict[str, int], dict[str, int]]:
    """Ermittelt die Anzahl der Verzweigungs- und Zusammenführungsknoten."""

    anzahl_vorgaenger, anzahl_nachfolger = _grade_ermitteln(vorgaenge, kanten)

    verzweigungen = sum(
        1 for anzahl in anzahl_nachfolger.values() if anzahl >= 2
    )
    zusammenfuehrungen = sum(
        1 for anzahl in anzahl_vorgaenger.values() if anzahl >= 2
    )

    return verzweigungen, zusammenfuehrungen, anzahl_vorgaenger, anzahl_nachfolger


def _strukturkanten_ergaenzen(
    sammlungen: list[list[str]],
    kanten: list[tuple[str, str]],
    vorgaenge: dict[str, Vorgang],
    soll_verzweigungen: int,
    soll_zusammenfuehrungen: int,
    max_vorgaenge_pro_stufe: int
) -> list[tuple[str, str]] | None:
    """Ergänzt notwendige Kanten, bis die gewünschten Strukturknoten entstehen.

    Die Kanten dürfen Sammlungen überspringen. Dadurch entstehen nicht nur
    Verbindungen zwischen direkt aufeinanderfolgenden Ebenen.
    """

    kanten = kanten.copy()
    position = {
        kennung: stufenindex
        for stufenindex, sammlung in enumerate(sammlungen)
        for kennung in sammlung
    }

    max_schritte = soll_verzweigungen + soll_zusammenfuehrungen + 2

    for _ in range(max_schritte):
        verzweigungen, zusammenfuehrungen, anzahl_vorgaenger, anzahl_nachfolger = (
            _strukturwerte_ermitteln(vorgaenge, kanten)
        )

        if (verzweigungen == soll_verzweigungen
                and zusammenfuehrungen == soll_zusammenfuehrungen):
            return kanten

        moegliche_erweiterungen = []

        for vorgaenger in vorgaenge:
            for nachfolger in vorgaenge:
                # Nur nach vorne und mindestens eine Ebene überspringen.
                if position[nachfolger] <= position[vorgaenger] + 1:
                    continue

                if (vorgaenger, nachfolger) in kanten:
                    continue

                if anzahl_nachfolger[vorgaenger] >= max_vorgaenge_pro_stufe:
                    continue

                if anzahl_vorgaenger[nachfolger] >= max_vorgaenge_pro_stufe:
                    continue

                # Wird durch diese Kante ein neuer Verzweigungs- bzw.
                # Zusammenführungsknoten erzeugt?
                neue_verzweigung = int(anzahl_nachfolger[vorgaenger] == 1)
                neue_zusammenfuehrung = int(anzahl_vorgaenger[nachfolger] == 1)

                if verzweigungen + neue_verzweigung > soll_verzweigungen:
                    continue

                if zusammenfuehrungen + neue_zusammenfuehrung > soll_zusammenfuehrungen:
                    continue

                if neue_verzweigung or neue_zusammenfuehrung:
                    moegliche_erweiterungen.append((vorgaenger, nachfolger))

        if not moegliche_erweiterungen:
            return None

        kanten.append(random.choice(moegliche_erweiterungen))

    verzweigungen, zusammenfuehrungen, _, _ = _strukturwerte_ermitteln(
        vorgaenge, kanten
    )

    if (verzweigungen == soll_verzweigungen
            and zusammenfuehrungen == soll_zusammenfuehrungen):
        return kanten

    return None


def _optionale_kanten_ergaenzen(
    sammlungen: list[list[str]],
    kanten: list[tuple[str, str]],
    vorgaenge: dict[str, Vorgang],
    gewuenschte_anzahl: int,
    max_vorgaenge_pro_stufe: int
) -> tuple[list[tuple[str, str]], int]:
    """Fügt optionale Kanten hinzu, ohne neue Verzweigungs- oder
    Zusammenführungsknoten zu erzeugen.

    Dafür werden nur bereits verzweigende Vorgänge mit bereits
    zusammenführenden Vorgängen verbunden. Beide Grade dürfen höchstens
    bis zur festgelegten Maximalgröße erweitert werden.
    """

    kanten = kanten.copy()
    position = {
        kennung: stufenindex
        for stufenindex, sammlung in enumerate(sammlungen)
        for kennung in sammlung
    }

    hinzugefuegt = 0

    for _ in range(gewuenschte_anzahl):
        verzweigungen, zusammenfuehrungen, anzahl_vorgaenger, anzahl_nachfolger = (
            _strukturwerte_ermitteln(vorgaenge, kanten)
        )

        moegliche_kanten = []

        for vorgaenger in vorgaenge:
            if anzahl_nachfolger[vorgaenger] < 2:
                continue
            if anzahl_nachfolger[vorgaenger] >= max_vorgaenge_pro_stufe:
                continue

            for nachfolger in vorgaenge:
                if anzahl_vorgaenger[nachfolger] < 2:
                    continue
                if anzahl_vorgaenger[nachfolger] >= max_vorgaenge_pro_stufe:
                    continue
                if position[nachfolger] <= position[vorgaenger]:
                    continue
                if (vorgaenger, nachfolger) in kanten:
                    continue

                moegliche_kanten.append((vorgaenger, nachfolger))

        if not moegliche_kanten:
            break

        kanten.append(random.choice(moegliche_kanten))
        hinzugefuegt += 1

    return kanten, hinzugefuegt


def _stufen_aus_kanten_ableiten(
    vorgaenge: dict[str, Vorgang],
    kanten: list[tuple[str, str]],
    startvorgang: str
) -> list[list[str]]:
    """Leitet die Ebenen aus dem fertigen gerichteten Graphen ab.

    Die Ebene eines Vorgangs entspricht der Länge des längsten Pfades
    vom Startvorgang zu diesem Vorgang.
    """

    nachfolger_liste = {kennung: [] for kennung in vorgaenge}
    eingangsgrade = {kennung: 0 for kennung in vorgaenge}

    for vorgaenger, nachfolger in kanten:
        nachfolger_liste[vorgaenger].append(nachfolger)
        eingangsgrade[nachfolger] += 1

    warteschlange = deque(
        kennung for kennung in vorgaenge if eingangsgrade[kennung] == 0
    )

    abstand = {kennung: 0 for kennung in vorgaenge}
    sortierte_vorgaenge = []

    while warteschlange:
        aktueller_vorgang = warteschlange.popleft()
        sortierte_vorgaenge.append(aktueller_vorgang)

        for nachfolger in nachfolger_liste[aktueller_vorgang]:
            abstand[nachfolger] = max(
                abstand[nachfolger], abstand[aktueller_vorgang] + 1
            )
            eingangsgrade[nachfolger] -= 1

            if eingangsgrade[nachfolger] == 0:
                warteschlange.append(nachfolger)

    if len(sortierte_vorgaenge) != len(vorgaenge):
        raise ValueError("Die erzeugten Kanten enthalten einen Kreislauf.")

    if any(
        kennung != startvorgang and abstand[kennung] == 0
        for kennung in vorgaenge
    ):
        raise ValueError("Mindestens ein Vorgang ist vom Startvorgang nicht erreichbar.")

    stufenzahl = max(abstand.values()) + 1
    stufen = [[] for _ in range(stufenzahl)]

    for kennung in vorgaenge:
        stufen[abstand[kennung]].append(kennung)

    return stufen


def _alle_vorgaenge_erreichbar(
    vorgaenge: dict[str, Vorgang],
    kanten: list[tuple[str, str]],
    startvorgang: str,
    endvorgang: str
) -> bool:
    """Prüft, ob jeder Vorgang vom Start erreichbar ist und zum Ende führt."""

    nachfolger_liste = {kennung: [] for kennung in vorgaenge}
    vorgaenger_liste = {kennung: [] for kennung in vorgaenge}

    for vorgaenger, nachfolger in kanten:
        nachfolger_liste[vorgaenger].append(nachfolger)
        vorgaenger_liste[nachfolger].append(vorgaenger)

    def erreichbar(start: str, adjacency: dict[str, list[str]]) -> set[str]:
        besucht = set()
        warteschlange = [start]

        while warteschlange:
            aktuell = warteschlange.pop()
            if aktuell in besucht:
                continue
            besucht.add(aktuell)
            warteschlange.extend(adjacency[aktuell])

        return besucht

    vom_start = erreichbar(startvorgang, nachfolger_liste)
    zum_ende = erreichbar(endvorgang, vorgaenger_liste)

    return len(vom_start) == len(vorgaenge) and len(zum_ende) == len(vorgaenge)


# ============================================================
# 4. NETZPLAN VALIDIEREN
# ============================================================


def netzplan_validieren(netzplan: Netzplan) -> None:
    """Bricht mit einer verständlichen Fehlermeldung ab, wenn der Netzplan
    eine grundlegende strukturelle Regel verletzt.
    """

    vorgaenge = netzplan["vorgaenge"]
    kanten = netzplan["kanten"]
    stufen = netzplan["stufen"]
    startvorgang = netzplan["startvorgang"]
    endvorgang = netzplan["endvorgang"]
    max_pro_stufe = netzplan["max_vorgaenge_pro_stufe"]

    if not stufen or any(not stufe for stufe in stufen):
        raise ValueError("Der Netzplan enthält eine leere Ebene.")

    if any(len(stufe) > max_pro_stufe for stufe in stufen):
        raise ValueError("Die maximale Anzahl an Vorgängen pro Ebene wurde überschritten.")

    alle_vorgaenge = [kennung for stufe in stufen for kennung in stufe]

    if len(alle_vorgaenge) != len(set(alle_vorgaenge)):
        raise ValueError("Ein Vorgang wurde mehreren Ebenen zugeordnet.")

    if set(alle_vorgaenge) != set(vorgaenge):
        raise ValueError("Nicht alle Vorgänge sind genau einer Ebene zugeordnet.")

    if len(stufen[0]) != 1 or stufen[0][0] != startvorgang:
        raise ValueError("Die erste Ebene muss ausschließlich den Startvorgang enthalten.")

    if len(stufen[-1]) != 1 or stufen[-1][0] != endvorgang:
        raise ValueError("Die letzte Ebene muss ausschließlich den Endvorgang enthalten.")

    if len(kanten) != len(set(kanten)):
        raise ValueError("Eine Kante wurde mehrfach erzeugt.")

    for vorgaenger, nachfolger in kanten:
        if vorgaenger not in vorgaenge or nachfolger not in vorgaenge:
            raise ValueError("Eine Kante verweist auf einen nicht existierenden Vorgang.")
        if vorgaenger == nachfolger:
            raise ValueError("Ein Vorgang darf nicht von sich selbst abhängen.")

    position = {
        kennung: index
        for index, stufe in enumerate(stufen)
        for kennung in stufe
    }

    for vorgaenger, nachfolger in kanten:
        if position[nachfolger] <= position[vorgaenger]:
            raise ValueError("Eine Kante verläuft nicht zu einer späteren Ebene.")

    anzahl_vorgaenger, anzahl_nachfolger = _grade_ermitteln(vorgaenge, kanten)

    if any(anzahl > max_pro_stufe for anzahl in anzahl_vorgaenger.values()):
        raise ValueError("Ein Vorgang hat mehr Vorgänger als die maximale Ebenengröße erlaubt.")

    if any(anzahl > max_pro_stufe for anzahl in anzahl_nachfolger.values()):
        raise ValueError("Ein Vorgang hat mehr Nachfolger als die maximale Ebenengröße erlaubt.")

    if any(anzahl_vorgaenger[k] == 0 for k in vorgaenge if k != startvorgang):
        raise ValueError("Ein Vorgang besitzt keinen Vorgänger.")

    if any(anzahl_nachfolger[k] == 0 for k in vorgaenge if k != endvorgang):
        raise ValueError("Ein Vorgang besitzt keinen Nachfolger.")

    if not _alle_vorgaenge_erreichbar(
        vorgaenge, kanten, startvorgang, endvorgang
    ):
        raise ValueError("Nicht alle Vorgänge liegen auf einem Weg vom Start zum Ende.")

    verzweigungen, zusammenfuehrungen, _, _ = _strukturwerte_ermitteln(
        vorgaenge, kanten
    )

    if verzweigungen != netzplan["anzahl_verzweigungen"]:
        raise ValueError("Die gespeicherte Verzweigungsanzahl stimmt nicht mit den Kanten überein.")

    if zusammenfuehrungen != netzplan["anzahl_zusammenfuehrungen"]:
        raise ValueError("Die gespeicherte Zusammenführungsanzahl stimmt nicht mit den Kanten überein.")


# ============================================================
# 5. ÖFFENTLICHE GENERATORFUNKTION
# ============================================================


def netzplan_generieren(schwierigkeitsgrad: str = "Einfach") -> Netzplan:
    """Erzeugt einen zufälligen, strukturell gültigen Netzplan.

    Die Anzahl der Verzweigungs- und Zusammenführungsknoten wird separat
    aus den jeweiligen Profilbereichen ausgewählt. Die tatsächlich nötigen
    Kanten werden anschließend passend dazu erzeugt.
    """

    if schwierigkeitsgrad not in schwierigkeitsprofile:
        raise ValueError(f"Unbekannter Schwierigkeitsgrad: {schwierigkeitsgrad}")

    profil = schwierigkeitsprofile[schwierigkeitsgrad]
    buchstaben = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    max_pro_stufe = profil["max_vorgaenge_pro_stufe"]

    max_parameter_versuche = 30
    max_struktur_versuche = 500

    for _ in range(max_parameter_versuche):
        vorgangszahl = random.randint(*profil["vorgangszahl"])

        if vorgangszahl > len(buchstaben):
            raise ValueError("Nicht genügend Vorgangskennungen vorhanden.")

        soll_verzweigungen = random.randint(*profil["verzweigungen"])
        soll_zusammenfuehrungen = random.randint(*profil["zusammenfuehrungen"])

        vorgang_kennungen = list(buchstaben[:vorgangszahl])
        startvorgang = vorgang_kennungen[0]
        endvorgang = vorgang_kennungen[-1]

        vorgaenge: dict[str, Vorgang] = {
            kennung: {
                "bezeichnung": kennung,
                "dauer": random.randint(*profil["dauer"])
            }
            for kennung in vorgang_kennungen
        }

        for _ in range(max_struktur_versuche):
            sammlungen = _sammlungen_erzeugen(
                vorgang_kennungen, max_pro_stufe
            )

            kanten = _grundkanten_erzeugen(sammlungen)

            kanten = _strukturkanten_ergaenzen(
                sammlungen,
                kanten,
                vorgaenge,
                soll_verzweigungen,
                soll_zusammenfuehrungen,
                max_pro_stufe
            )

            if kanten is None:
                continue

            # Optionale Kanten sind kein Pflichtbestandteil der Struktur.
            # Sie werden nur ergänzt, wenn sie vorhandene Verzweigungs- und
            # Zusammenführungsknoten erweitern, ohne neue zu erzeugen.
            gewuenschte_optionale_kanten = random.randint(
                *profil["optionale_zusatzkanten"]
            )

            kanten, anzahl_optionale_kanten = _optionale_kanten_ergaenzen(
                sammlungen,
                kanten,
                vorgaenge,
                gewuenschte_optionale_kanten,
                max_pro_stufe
            )

            stufen = _stufen_aus_kanten_ableiten(
                vorgaenge, kanten, startvorgang
            )

            verzweigungen, zusammenfuehrungen, anzahl_vorgaenger, anzahl_nachfolger = (
                _strukturwerte_ermitteln(vorgaenge, kanten)
            )

            netzplan: Netzplan = {
                "schwierigkeitsgrad": schwierigkeitsgrad,
                "vorgangszahl": vorgangszahl,
                "stufenzahl": len(stufen),
                "max_vorgaenge_pro_stufe": max_pro_stufe,
                "anzahl_kanten": len(kanten),
                "anzahl_verzweigungen": verzweigungen,
                "anzahl_zusammenfuehrungen": zusammenfuehrungen,
                "anzahl_optionale_zusatzkanten": anzahl_optionale_kanten,
                "anzahl_kanten_ueber_minimum": len(kanten) - (vorgangszahl - 1),
                "soll_verzweigungen": soll_verzweigungen,
                "soll_zusammenfuehrungen": soll_zusammenfuehrungen,
                "max_tatsaechliche_vorgaenger": max(anzahl_vorgaenger.values()),
                "max_tatsaechliche_nachfolger": max(anzahl_nachfolger.values()),
                "startvorgang": startvorgang,
                "endvorgang": endvorgang,
                "vorgaenge": vorgaenge,
                "kanten": kanten,
                "stufen": stufen
            }

            try:
                netzplan_validieren(netzplan)
            except ValueError:
                continue

            return netzplan

    raise RuntimeError(
        "Es konnte innerhalb der erlaubten Versuche kein Netzplan erzeugt werden. "
        "Bitte die Profilgrenzen oder die maximale Ebenengröße überprüfen."
    )
