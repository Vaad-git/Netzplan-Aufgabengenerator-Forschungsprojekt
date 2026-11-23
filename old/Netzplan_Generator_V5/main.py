
"""Lokaler Testlauf: Netzplan, Aufgabenstellung und Lösungsvergleich."""

import random

from generator import netzplan_generieren
from netzplan_ausgabe import netzplan_ausgeben
from aufgabenstellung import aufgabenstellung_generieren
from musterloesung import (
    WERTE,
    musterloesung_berechnen,
    loesung_vergleichen,
)


def vorgaenger_ermitteln(netzplan):
    """Erstellt für jeden Vorgang eine Liste seiner direkten Vorgänger."""

    vorgaenger = {name: [] for name in netzplan["vorgaenge"]}

    for kante in netzplan["kanten"]:
        vorgaenger[kante["nachfolger"]].append(kante["vorgaenger"])

    return vorgaenger


def schuelerloesung_manuell_eingeben(netzplan):
    """Liest die fünf Werte für jeden Vorgang über die Konsole ein."""

    vorgaenger = vorgaenger_ermitteln(netzplan)
    schuelerloesung = {"vorgaenge": {}}

    print("\nEINGABE DER SCHÜLERLÖSUNG")
    print("Gib pro Vorgang die fünf Werte in dieser Reihenfolge ein:")
    print("FAZ, FEZ, SAZ, SEZ, GP")
    print("Beispiel: 0, 6, 0, 6, 0")
    print("Negative Zahlen sind als Eingabe erlaubt und werden normal bewertet.\n")

    for name, daten in netzplan["vorgaenge"].items():
        direkte_vorgaenger = sorted(vorgaenger[name])

        if direkte_vorgaenger:
            vorgaenger_text = ", ".join(direkte_vorgaenger)
        else:
            vorgaenger_text = "keine (Startvorgang)"

        print(
            f"Vorgang {name} | Dauer: {daten['dauer']} | "
            f"Vorgänger: {vorgaenger_text}"
        )

        while True:
            eingabe = input("  FAZ, FEZ, SAZ, SEZ, GP: ")
            teile = [teil.strip() for teil in eingabe.split(",")]

            if len(teile) != len(WERTE):
                print("  Bitte genau fünf Zahlen eingeben, getrennt durch Kommas.")
                continue

            try:
                zahlen = [int(teil) for teil in teile]
            except ValueError:
                print("  Bitte nur ganze Zahlen eingeben, zum Beispiel: 0, 6, 0, 6, 0")
                continue

            schuelerloesung["vorgaenge"][name] = dict(zip(WERTE, zahlen))
            break

        print()

    return schuelerloesung


def schuelerloesung_aus_musterloesung_erstellen(musterloesung):
    """Übernimmt die Musterwerte als Schülerlösung für einen automatischen Test."""

    schuelerloesung = {"vorgaenge": {}}

    for name, werte in musterloesung["vorgaenge"].items():
        schuelerloesung["vorgaenge"][name] = {
            wert: werte[wert] for wert in WERTE
        }

    return schuelerloesung


def schuelerloesung_mit_einem_fehler_erstellen(musterloesung):
    """Erstellt eine Musterlösung, bei der genau ein Wert um 1 erhöht ist."""

    schuelerloesung = schuelerloesung_aus_musterloesung_erstellen(musterloesung)

    moegliche_fehler = [
        (name, wert)
        for name in schuelerloesung["vorgaenge"]
        for wert in WERTE
    ]

    name, wert = random.choice(moegliche_fehler)
    ursprungswert = schuelerloesung["vorgaenge"][name][wert]
    schuelerloesung["vorgaenge"][name][wert] = ursprungswert + 1

    fehlerinfo = {
        "vorgang": name,
        "wert": wert,
        "musterwert": ursprungswert,
        "schuelerwert": ursprungswert + 1,
    }

    return schuelerloesung, fehlerinfo


def schuelerloesung_auswaehlen(netzplan, musterloesung):
    """Bietet manuelle Eingabe und zwei automatische Testmöglichkeiten an."""

    print("LÖSUNG EINGEBEN / TESTMODUS")
    print("1 - Eigene Lösung manuell eingeben")
    print("2 - Musterlösung direkt als Schülerlösung abschicken (Test)")
    print("3 - Musterlösung mit genau einem Fehler abschicken (Test)\n")

    while True:
        auswahl = input("Bitte Option 1, 2 oder 3 auswählen: ").strip()

        if auswahl == "1":
            return schuelerloesung_manuell_eingeben(netzplan), None

        if auswahl == "2":
            print("\nTestmodus: Die unveränderte Musterlösung wird abgeschickt.\n")
            return schuelerloesung_aus_musterloesung_erstellen(musterloesung), None

        if auswahl == "3":
            schuelerloesung, fehlerinfo = schuelerloesung_mit_einem_fehler_erstellen(
                musterloesung
            )
            print("\nTestmodus: Genau ein zufällig ausgewählter Wert wurde um 1 erhöht.")
            print(
                f"Künstlicher Fehler: Vorgang {fehlerinfo['vorgang']}, "
                f"{fehlerinfo['wert']}: Musterwert {fehlerinfo['musterwert']}, "
                f"Testwert {fehlerinfo['schuelerwert']}.\n"
            )
            return schuelerloesung, fehlerinfo

        print("Ungültige Auswahl. Bitte 1, 2 oder 3 eingeben.\n")


def vergleichsergebnis_ausgeben(vergleich):
    """Gibt die Ergebnisse des Einzelvergleichs übersichtlich aus."""

    print("\nERGEBNIS DER ÜBERPRÜFUNG")

    for name, vorgangsergebnis in vergleich["vorgaenge"].items():
        print(
            f"\nVorgang {name}: "
            f"{vorgangsergebnis['anzahl_richtig']}/"
            f"{vorgangsergebnis['anzahl_werte']} Werte richtig"
        )

        for wert in WERTE:
            detail = vorgangsergebnis["werte"][wert]
            status = "RICHTIG" if detail["richtig"] else "FALSCH"
            print(
                f"  {wert}: Schüler = {detail['schueler']} | "
                f"Muster = {detail['muster']} -> {status}"
            )

    if vergleich["zusaetzliche_vorgaenge"]:
        print(
            "\nUnbekannte zusätzliche Vorgänge: "
            + ", ".join(vergleich["zusaetzliche_vorgaenge"])
        )

    print("\nGESAMTERGEBNIS")
    print(
        f"Richtige Werte: {vergleich['anzahl_richtig']} von "
        f"{vergleich['anzahl_werte']}"
    )
    print(f"Ergebnis: {vergleich['prozent_richtig']} %")

    if vergleich["alles_korrekt"]:
        print("Gesamtbewertung: Die Lösung ist vollständig korrekt.")
    else:
        print("Gesamtbewertung: Die Lösung enthält Fehler.")


def main():
    """Führt einen vollständigen lokalen Testlauf durch."""

    # 1. Netzplan einmal erzeugen.
    plan = netzplan_generieren()

    # 2. Grafik, Aufgabenstellung und Musterlösung aus demselben Netzplan erstellen.
    datei = netzplan_ausgeben(plan)
    aufgabenstellung = aufgabenstellung_generieren(plan)
    musterloesung = musterloesung_berechnen(plan)

    print("NETZPLAN WURDE ERZEUGT")
    print("Vorgänge:", plan["vorgangszahl"])
    print("Kanten:", plan["anzahl_kanten"])
    print("Grafik:", datei.resolve())

    print("\n" + aufgabenstellung)
    print("\nBitte öffne die SVG-Grafik, bevor du die Werte eingibst.")

    # 3. Schülerlösung manuell oder über einen Testmodus erstellen.
    schuelerloesung, _ = schuelerloesung_auswaehlen(plan, musterloesung)

    # 4. Schülerlösung mit der Musterlösung vergleichen.
    vergleich = loesung_vergleichen(musterloesung, schuelerloesung)

    # 5. Einzel- und Gesamtergebnis anzeigen.
    vergleichsergebnis_ausgeben(vergleich)


if __name__ == "__main__":
    main()
