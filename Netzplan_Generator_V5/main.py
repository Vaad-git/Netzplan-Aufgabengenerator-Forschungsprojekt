"""Lokaler Testlauf: Netzplan, Aufgabenstellung und Lösungsvergleich."""

import random

from netzplan.generator import netzplan_generieren
from netzplan.netzplan_ausgabe import netzplan_ausgeben
from netzplan.aufgabenstellung import aufgabenstellung_generieren
from netzplan.ki_aufgabenstellung import bezeichnungen_mit_ki_generieren
from netzplan.musterloesung import (
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


def schuelerloesung_manuell_eingeben(netzplan, bezeichnungen=None):
    """Liest die fünf Werte für jeden Vorgang über die Konsole ein."""

    vorgaenger = vorgaenger_ermitteln(netzplan)
    bezeichnungen = bezeichnungen or {}
    schuelerloesung = {"vorgaenge": {}}

    print("\nEINGABE DER SCHÜLERLÖSUNG")
    print("Eingabeformat je Vorgang: fünf Werte in folgender Reihenfolge:")
    print("FAZ, FEZ, SAZ, SEZ, GP")
    print("Beispiel: 0, 6, 0, 6, 0")
    print("Negative Zahlen sind als Eingabe erlaubt und werden normal bewertet.\n")

    for name, daten in netzplan["vorgaenge"].items():
        direkte_vorgaenger = sorted(vorgaenger[name])

        if direkte_vorgaenger:
            vorgaenger_anzeigen = []
            for vorgaenger_name in direkte_vorgaenger:
                vorgaenger_bezeichnung = bezeichnungen.get(vorgaenger_name)
                if vorgaenger_bezeichnung:
                    vorgaenger_anzeigen.append(
                        f"{vorgaenger_bezeichnung} [{vorgaenger_name}]"
                    )
                else:
                    vorgaenger_anzeigen.append(vorgaenger_name)
            vorgaenger_text = ", ".join(vorgaenger_anzeigen)
        else:
            vorgaenger_text = "keine (Startvorgang)"

        bezeichnung = bezeichnungen.get(name)
        name_text = f"{bezeichnung} [{name}]" if bezeichnung else name
        print(
            f"Vorgang {name_text} | Dauer: {daten['dauer']} | "
            f"Vorgänger: {vorgaenger_text}"
        )

        while True:
            eingabe = input("  FAZ, FEZ, SAZ, SEZ, GP: ")
            teile = [teil.strip() for teil in eingabe.split(",")]

            if len(teile) != len(WERTE):
                print("  Fehler: Genau fünf Zahlen, getrennt durch Kommas, sind erforderlich.")
                continue

            try:
                zahlen = [int(teil) for teil in teile]
            except ValueError:
                print("  Fehler: Es sind ganze Zahlen erforderlich, z. B. 0, 6, 0, 6, 0.")
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


def schuelerloesung_auswaehlen(netzplan, musterloesung, bezeichnungen=None):
    """Bietet manuelle Eingabe und zwei automatische Testmöglichkeiten an."""

    print("LÖSUNG EINGEBEN / TESTMODUS")
    print("1 - Eigene Lösung manuell eingeben")
    print("2 - Musterlösung direkt als Schülerlösung abschicken (Test)")
    print("3 - Musterlösung mit genau einem Fehler abschicken (Test)\n")

    while True:
        auswahl = input("Auswahl [1/2/3]: ").strip()

        if auswahl == "1":
            return schuelerloesung_manuell_eingeben(netzplan, bezeichnungen), None

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

        print("Ungültige Auswahl. Erlaubte Eingaben: 1, 2 oder 3.\n")


def vergleichsergebnis_ausgeben(vergleich, bezeichnungen=None):
    """Gibt die Ergebnisse des Einzelvergleichs übersichtlich aus."""

    bezeichnungen = bezeichnungen or {}
    print("\nERGEBNIS DER ÜBERPRÜFUNG")

    for name, vorgangsergebnis in vergleich["vorgaenge"].items():
        vorgangsbezeichnung = bezeichnungen.get(name)
        vorgangsname = (
            f"{vorgangsbezeichnung} [{name}]"
            if vorgangsbezeichnung else name
        )
        print(
            f"\nVorgang {vorgangsname}: "
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

    # 2. Vorgangsbezeichnungen über die Gemini API erzeugen.
    print("KI erstellt passende Vorgangsbezeichnungen ...")
    try:
        bezeichnungen = bezeichnungen_mit_ki_generieren(plan)
        print("KI-Bezeichnungen wurden erfolgreich erstellt.")
    except RuntimeError as fehler:
        # Der restliche Prototyp bleibt auch ohne laufende KI testbar.
        bezeichnungen = {}
        print("\nHINWEIS: KI-Namensgebung war nicht verfügbar.")
        print(fehler)
        print("Die Aufgabenstellung verwendet stattdessen die IDs A, B, C usw.\n")

    # 3. Grafik, Aufgabenstellung und Musterlösung aus demselben Netzplan erstellen.
    datei = netzplan_ausgeben(plan, bezeichnungen=bezeichnungen)
    aufgabenstellung = aufgabenstellung_generieren(plan, bezeichnungen)
    musterloesung = musterloesung_berechnen(plan)

    print("\nNETZPLAN WURDE ERZEUGT")
    print("Vorgänge:", plan["vorgangszahl"])
    print("Kanten:", plan["anzahl_kanten"])
    print("Grafik:", datei.resolve())

    print("\n" + aufgabenstellung)
    print("\nSVG-Grafik vor der Eingabe öffnen. Danach die Vorgangswerte erfassen.")

    # 4. Schülerlösung manuell oder über einen Testmodus erstellen.
    schuelerloesung, _ = schuelerloesung_auswaehlen(
        plan, musterloesung, bezeichnungen
    )

    # 5. Schülerlösung mit der Musterlösung vergleichen.
    vergleich = loesung_vergleichen(musterloesung, schuelerloesung)

    # 6. Einzel- und Gesamtergebnis anzeigen.
    vergleichsergebnis_ausgeben(vergleich, bezeichnungen)


if __name__ == "__main__":
    main()
