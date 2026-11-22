import io
import unittest

from Backup.Netzplan_Generator_V4.main import Netzplan, netzplan_generieren
from Backup.Netzplan_Generator_V4.netzplan_ausgabe import netzplan_ausgeben


# ============================================================
# 1. KURZE STRUKTURTESTS
# ============================================================


class NetzplanTests(unittest.TestCase):
    netzplan: Netzplan

    def test_alle_vorgaenge_genau_einmal_in_stufen(self):
        alle_vorgaenge = [
            kennung
            for stufe in self.netzplan["stufen"]
            for kennung in stufe
        ]

        self.assertCountEqual(
            alle_vorgaenge,
            self.netzplan["vorgaenge"].keys()
        )
        self.assertEqual(len(alle_vorgaenge), len(set(alle_vorgaenge)))

    def test_start_und_ende(self):
        stufen = self.netzplan["stufen"]

        self.assertEqual(stufen[0], [self.netzplan["startvorgang"]])
        self.assertEqual(stufen[-1], [self.netzplan["endvorgang"]])

    def test_kanten_sind_gueltig_und_eindeutig(self):
        vorgaenge = self.netzplan["vorgaenge"]
        kanten = self.netzplan["kanten"]

        self.assertEqual(len(kanten), len(set(kanten)))

        for vorgaenger, nachfolger in kanten:
            self.assertIn(vorgaenger, vorgaenge)
            self.assertIn(nachfolger, vorgaenge)
            self.assertNotEqual(vorgaenger, nachfolger)

    def test_ebenen_und_verbindungen_halten_limits_ein(self):
        netzplan = self.netzplan
        max_pro_stufe = netzplan["max_vorgaenge_pro_stufe"]

        self.assertTrue(all(0 < len(stufe) <= max_pro_stufe for stufe in netzplan["stufen"]))

        position = {
            kennung: index
            for index, stufe in enumerate(netzplan["stufen"])
            for kennung in stufe
        }

        vorgaenger_anzahl = {kennung: 0 for kennung in netzplan["vorgaenge"]}
        nachfolger_anzahl = {kennung: 0 for kennung in netzplan["vorgaenge"]}

        for vorgaenger, nachfolger in netzplan["kanten"]:
            self.assertGreater(position[nachfolger], position[vorgaenger])
            nachfolger_anzahl[vorgaenger] += 1
            vorgaenger_anzahl[nachfolger] += 1

        self.assertTrue(all(wert <= max_pro_stufe for wert in vorgaenger_anzahl.values()))
        self.assertTrue(all(wert <= max_pro_stufe for wert in nachfolger_anzahl.values()))

    def test_verzweigungen_und_zusammenfuehrungen(self):
        netzplan = self.netzplan
        vorgaenger_anzahl = {kennung: 0 for kennung in netzplan["vorgaenge"]}
        nachfolger_anzahl = {kennung: 0 for kennung in netzplan["vorgaenge"]}

        for vorgaenger, nachfolger in netzplan["kanten"]:
            nachfolger_anzahl[vorgaenger] += 1
            vorgaenger_anzahl[nachfolger] += 1

        verzweigungen = sum(wert >= 2 for wert in nachfolger_anzahl.values())
        zusammenfuehrungen = sum(wert >= 2 for wert in vorgaenger_anzahl.values())

        self.assertEqual(verzweigungen, netzplan["soll_verzweigungen"])
        self.assertEqual(zusammenfuehrungen, netzplan["soll_zusammenfuehrungen"])


# ============================================================
# 2. DETAILAUSGABE
# ============================================================


def details_ausgeben(netzplan: Netzplan):
    vorgaenge = netzplan["vorgaenge"]
    kanten = netzplan["kanten"]
    stufen = netzplan["stufen"]

    vorgaenger_anzahl = {kennung: 0 for kennung in vorgaenge}
    nachfolger_anzahl = {kennung: 0 for kennung in vorgaenge}

    for vorgaenger, nachfolger in kanten:
        nachfolger_anzahl[vorgaenger] += 1
        vorgaenger_anzahl[nachfolger] += 1

    print("\n========== NETZPLANDETAILS ==========")
    print("Schwierigkeitsgrad:", netzplan["schwierigkeitsgrad"])
    print("Vorgangszahl:", netzplan["vorgangszahl"])
    print("Stufenzahl:", netzplan["stufenzahl"])
    print("Maximale Vorgänge pro Stufe:", netzplan["max_vorgaenge_pro_stufe"])
    print("Anzahl Kanten:", netzplan["anzahl_kanten"])
    print("Verzweigungen:", netzplan["anzahl_verzweigungen"])
    print("Zusammenführungen:", netzplan["anzahl_zusammenfuehrungen"])
    print("Optionale zusätzliche Kanten:", netzplan["anzahl_optionale_zusatzkanten"])
    print("Kanten über dem Minimum (N-1):", netzplan["anzahl_kanten_ueber_minimum"])
    print("Tatsächliche maximale Vorgängerzahl:", netzplan["max_tatsaechliche_vorgaenger"])
    print("Tatsächliche maximale Nachfolgerzahl:", netzplan["max_tatsaechliche_nachfolger"])

    print("\nVORGÄNGE:")
    for kennung, daten in vorgaenge.items():
        print(f"{kennung} | Bezeichnung: {daten['bezeichnung']} | Dauer: {daten['dauer']}")

    print("\nEBENEN:")
    for index, stufe in enumerate(stufen, start=1):
        print(f"Ebene {index}: {stufe}")

    print("\nKANTEN:")
    for vorgaenger, nachfolger in kanten:
        print(f"{vorgaenger} -> {nachfolger}")

    print("\nVORGÄNGER UND NACHFOLGER:")
    for kennung in vorgaenge:
        print(
            f"{kennung} | Vorgänger: {vorgaenger_anzahl[kennung]}"
            f" | Nachfolger: {nachfolger_anzahl[kennung]}"
        )

    print("=====================================")


# ============================================================
# 3. BENUTZERABFRAGE UND TESTLAUF
# ============================================================


def details_abfragen(frage: str) -> bool:
    while True:
        print(f"\n{frage}")
        print("1 = Ja")
        print("2 = Nein")
        auswahl = input("Auswahl: ").strip()

        if auswahl == "1":
            return True
        if auswahl == "2":
            return False

        print("Ungültige Eingabe. Bitte 1 oder 2 eingeben.")


def tests_ausfuehren(netzplan: Netzplan) -> bool:
    NetzplanTests.netzplan = netzplan
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NetzplanTests)
    ausgabe = io.StringIO()
    runner = unittest.TextTestRunner(stream=ausgabe, verbosity=0)
    ergebnis = runner.run(suite)

    fehler = len(ergebnis.failures) + len(ergebnis.errors)
    bestanden = ergebnis.testsRun - fehler

    print("\n========== TESTERGEBNIS ==========")
    print(f"({bestanden}/{ergebnis.testsRun}) Tests bestanden.")

    for test, meldung in ergebnis.failures + ergebnis.errors:
        beschreibung = test.shortDescription() or test._testMethodName
        letzte_zeile = meldung.strip().splitlines()[-1]
        print(f"\nFEHLER: {beschreibung}")
        print(letzte_zeile)

    print("==================================")
    return ergebnis.wasSuccessful()


def starten():
    try:
        netzplan = netzplan_generieren()
    except Exception as fehler:
        print("\nFEHLER BEI DER NETZPLANGENERIERUNG:")
        print(fehler)
        return

    if not tests_ausfuehren(netzplan):
        print("\nDer Netzplan hat die Tests nicht bestanden. Keine Grafik wird erstellt.")
        return

    if details_abfragen("Details vor der Netzplanausgabe anzeigen?"):
        details_ausgeben(netzplan)

    print("\n========== NETZPLAN ==========")
    try:
        netzplan_ausgeben(
            netzplan["stufen"],
            netzplan["kanten"],
            netzplan["vorgaenge"]
        )
    except Exception as fehler:
        print("Die grafische Ausgabe konnte nicht erstellt werden:")
        print(fehler)
        return

    if details_abfragen("Details nach der Netzplanausgabe zusätzlich anzeigen?"):
        details_ausgeben(netzplan)

    print("\nProgramm beendet.")


if __name__ == "__main__":
    starten()
