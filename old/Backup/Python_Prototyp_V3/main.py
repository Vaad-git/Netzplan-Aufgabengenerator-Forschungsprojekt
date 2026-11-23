import random
import math
from typing import TypedDict



# ============================================================
# 1. DATENTYPEN
# ============================================================

class Schwierigkeitsprofil(TypedDict):
    vorgangszahl: tuple[int, int]
    dauer: tuple[int, int]
    zusaetzliche_kanten: tuple[int, int]
    verzweigungen: tuple[int, int]
    zusammenfuehrungen: tuple[int, int]
    stufenanzahl: tuple[int, int]
    max_vorgaenger: tuple[int, int]
    max_nachfolger: tuple[int, int]


class Vorgang(TypedDict):
    bezeichnung: str
    dauer: int


class Netzplan(TypedDict):
    schwierigkeitsgrad: str
    vorgangszahl: int
    stufenzahl: int
    max_vorgaenger: int
    max_nachfolger: int
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
        "zusaetzliche_kanten": (1, 2),
        "verzweigungen": (1, 2),
        "zusammenfuehrungen": (1, 2),
        "stufenanzahl": (4, 5),
        "max_vorgaenger": (2, 2),
        "max_nachfolger": (2, 2)
    }
}



# ============================================================
# 3. NETZPLAN GENERIEREN
# ============================================================

def netzplan_generieren(schwierigkeitsgrad: str = "Einfach") -> Netzplan:

    if schwierigkeitsgrad not in schwierigkeitsprofile:
        raise ValueError(f"Unbekannter Schwierigkeitsgrad: {schwierigkeitsgrad}")

    profil = schwierigkeitsprofile[schwierigkeitsgrad]

    buchstaben = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Zufällige Parameter bestimmen
    vorgangszahl = random.randint(*profil["vorgangszahl"])
    stufenzahl = random.randint(*profil["stufenanzahl"])

    # Feste Grenzwerte verwenden
    max_vorgaenger = profil["max_vorgaenger"][0]
    max_nachfolger = profil["max_nachfolger"][0]

    max_vorgaenge_pro_stufe = min(max_vorgaenger, max_nachfolger)

    if max_vorgaenge_pro_stufe < 1:
        raise ValueError("Vorgänger- und Nachfolgerlimits müssen mindestens 1 sein.")

    if vorgangszahl > len(buchstaben):
        raise ValueError("Nicht genügend Vorgangskennungen vorhanden.")

    # Benötigte Mindestanzahl an Stufen berechnen
    benoetigte_mittlere_stufen = math.ceil(
        (vorgangszahl - 2) / max_vorgaenge_pro_stufe
    )

    minimale_stufenzahl = benoetigte_mittlere_stufen + 2

    if minimale_stufenzahl > profil["stufenanzahl"][1]:
        raise ValueError("Vorgangszahl und Stufenlimits sind nicht miteinander vereinbar.")

    stufenzahl = max(stufenzahl, minimale_stufenzahl)

    # --------------------------------------------------------
    # Vorgänge erzeugen
    # --------------------------------------------------------

    vorgaenge: dict[str, Vorgang] = {}

    for i in range(vorgangszahl):

        kennung = buchstaben[i]

        vorgaenge[kennung] = {
            "bezeichnung": kennung,
            "dauer": random.randint(*profil["dauer"])
        }

    vorgang_kennungen = list(vorgaenge.keys())

    # --------------------------------------------------------
    # Stufen erstellen
    # --------------------------------------------------------

    stufen: list[list[str]] = []

    for i in range(stufenzahl):
        stufen.append([])

    # Start- und Endvorgang zuordnen
    stufen[0].append(vorgang_kennungen[0])
    stufen[-1].append(vorgang_kennungen[-1])

    mittlere_vorgaenge = vorgang_kennungen[1:-1]
    anzahl_mittlere_stufen = stufenzahl - 2

    # Jede mittlere Stufe erhält zunächst einen Vorgang
    for i in range(anzahl_mittlere_stufen):
        stufen[i + 1].append(mittlere_vorgaenge[i])

    # Übrige Vorgänge zufällig auf freie Stufen verteilen
    for vorgang in mittlere_vorgaenge[anzahl_mittlere_stufen:]:

        freie_stufen = []

        for i in range(1, stufenzahl - 1):
            if len(stufen[i]) < max_vorgaenge_pro_stufe:
                freie_stufen.append(i)


        if not freie_stufen:
            raise ValueError("Keine freie Stufe für einen weiteren Vorgang vorhanden.")

        zufaellige_stufe = random.choice(freie_stufen)
        stufen[zufaellige_stufe].append(vorgang)

    # --------------------------------------------------------
    # Kanten generieren
    # --------------------------------------------------------

    kanten: list[tuple[str, str]] = []

    for i in range(stufenzahl - 1):

        aktuelle_stufe = stufen[i]
        naechste_stufe = stufen[i + 1]

        # Fall 1: Ein Vorgänger, mehrere Nachfolger
        if len(aktuelle_stufe) == 1:

            vorgaenger = aktuelle_stufe[0]

            if len(naechste_stufe) > max_nachfolger:
                raise ValueError("Maximale Nachfolgerzahl überschritten.")

            for nachfolger in naechste_stufe:
                kanten.append((vorgaenger, nachfolger))

        # Fall 2: Mehrere Vorgänger, ein Nachfolger
        elif len(naechste_stufe) == 1:

            nachfolger = naechste_stufe[0]

            if len(aktuelle_stufe) > max_vorgaenger:
                raise ValueError("Maximale Vorgängerzahl überschritten.")

            for vorgaenger in aktuelle_stufe:
                kanten.append((vorgaenger, nachfolger))

        # Fall 3: Zwei Vorgänger, zwei Nachfolger
        elif len(aktuelle_stufe) == 2 and len(naechste_stufe) == 2:

            zufaellige_nachfolger = naechste_stufe.copy()
            random.shuffle(zufaellige_nachfolger)

            for vorgaenger, nachfolger in zip(
                aktuelle_stufe, zufaellige_nachfolger
            ):
                kanten.append((vorgaenger, nachfolger))

        else:
            raise ValueError("Nicht unterstützte Stufenkombination.")

    # --------------------------------------------------------
    # Ergebnisse zurückgeben
    # --------------------------------------------------------

    return {
        "schwierigkeitsgrad": schwierigkeitsgrad,
        "vorgangszahl": vorgangszahl,
        "stufenzahl": stufenzahl,
        "max_vorgaenger": max_vorgaenger,
        "max_nachfolger": max_nachfolger,
        "vorgaenge": vorgaenge,
        "kanten": kanten,
        "stufen": stufen
    }