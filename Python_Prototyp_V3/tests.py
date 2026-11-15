
import unittest
import io

from main import netzplan_generieren, Netzplan
from netzplan_ausgabe import netzplan_ausgeben


# ============================================================
# 1. TESTKLASSE
# ============================================================

class NetzplanTests(unittest.TestCase):

    netzplan: Netzplan

    # --------------------------------------------------------
    # Test 1: Vorgänge vollständig und genau einmal verteilt
    # --------------------------------------------------------

    def test_vorgaenge_sind_vollstaendig_verteilt(self):
        """Alle Vorgänge kommen genau einmal in den Stufen vor."""

        vorgaenge = self.netzplan["vorgaenge"]
        stufen = self.netzplan["stufen"]

        alle_vorgaenge = [
            vorgang
            for stufe in stufen
            for vorgang in stufe
        ]

        self.assertTrue(stufen, "Es wurden keine Stufen erzeugt.")

        self.assertTrue(
            all(stufe for stufe in stufen),
            "Mindestens eine Stufe ist leer."
        )

        self.assertCountEqual(
            alle_vorgaenge,
            vorgaenge.keys(),
            "Vorgänge fehlen oder wurden mehrfach verteilt."
        )

        self.assertEqual(
            len(alle_vorgaenge),
            len(set(alle_vorgaenge)),
            "Ein Vorgang wurde mehrfach zugeordnet."
        )

    # --------------------------------------------------------
    # Test 2: Kanten verweisen auf existierende Vorgänge
    # --------------------------------------------------------

    def test_kanten_verweisen_auf_existierende_vorgaenge(self):
        """Alle Vorgänger und Nachfolger existieren."""

        vorgaenge = self.netzplan["vorgaenge"]
        kanten = self.netzplan["kanten"]

        for vorgaenger, nachfolger in kanten:

            self.assertIn(
                vorgaenger,
                vorgaenge,
                f"Vorgänger {vorgaenger} existiert nicht."
            )

            self.assertIn(
                nachfolger,
                vorgaenge,
                f"Nachfolger {nachfolger} existiert nicht."
            )

            self.assertNotEqual(
                vorgaenger,
                nachfolger,
                f"Selbstabhängigkeit bei Vorgang {vorgaenger}."
            )

        self.assertEqual(
            len(kanten),
            len(set(kanten)),
            "Eine Kante wurde mehrfach erzeugt."
        )

    # --------------------------------------------------------
    # Test 3: Kanten verbinden benachbarte Stufen
    # --------------------------------------------------------

    def test_kanten_verbinden_benachbarte_stufen(self):
        """Jede Kante verbindet zwei direkt aufeinanderfolgende Stufen."""

        stufen = self.netzplan["stufen"]
        kanten = self.netzplan["kanten"]

        positionen = {}

        for stufenindex, stufe in enumerate(stufen):
            for vorgang in stufe:
                positionen[vorgang] = stufenindex

        for vorgaenger, nachfolger in kanten:

            self.assertEqual(
                positionen[nachfolger],
                positionen[vorgaenger] + 1,
                f"Kante {vorgaenger} -> {nachfolger} "
                "verbindet keine benachbarten Stufen."
            )

    # --------------------------------------------------------
    # Test 4: Vorgänger- und Nachfolgerlimits
    # --------------------------------------------------------

    def test_vorgaenger_und_nachfolgerlimits(self):
        """Alle Vorgänge halten die festgelegten Grenzwerte ein."""

        vorgaenge = self.netzplan["vorgaenge"]
        kanten = self.netzplan["kanten"]

        max_vorgaenger = self.netzplan["max_vorgaenger"]
        max_nachfolger = self.netzplan["max_nachfolger"]

        anzahl_vorgaenger = {
            kennung: 0 for kennung in vorgaenge
        }

        anzahl_nachfolger = {
            kennung: 0 for kennung in vorgaenge
        }

        for vorgaenger, nachfolger in kanten:
            anzahl_nachfolger[vorgaenger] += 1
            anzahl_vorgaenger[nachfolger] += 1

        startvorgang = self.netzplan["stufen"][0][0]
        endvorgang = self.netzplan["stufen"][-1][0]

        for kennung in vorgaenge:

            self.assertLessEqual(
                anzahl_vorgaenger[kennung],
                max_vorgaenger,
                f"Vorgang {kennung} hat zu viele Vorgänger."
            )

            self.assertLessEqual(
                anzahl_nachfolger[kennung],
                max_nachfolger,
                f"Vorgang {kennung} hat zu viele Nachfolger."
            )

            if kennung != startvorgang:
                self.assertGreaterEqual(
                    anzahl_vorgaenger[kennung],
                    1,
                    f"Vorgang {kennung} besitzt keinen Vorgänger."
                )

            if kennung != endvorgang:
                self.assertGreaterEqual(
                    anzahl_nachfolger[kennung],
                    1,
                    f"Vorgang {kennung} besitzt keinen Nachfolger."
                )

    # --------------------------------------------------------
    # Test 5: Start- und Endvorgang
    # --------------------------------------------------------

    def test_start_und_endvorgang(self):
        """Erste und letzte Stufe enthalten jeweils genau einen Vorgang."""

        stufen = self.netzplan["stufen"]
        vorgaenge = self.netzplan["vorgaenge"]

        self.assertEqual(
            len(stufen[0]),
            1,
            "Die erste Stufe muss genau einen Startvorgang enthalten."
        )

        self.assertEqual(
            len(stufen[-1]),
            1,
            "Die letzte Stufe muss genau einen Endvorgang enthalten."
        )

        self.assertEqual(
            stufen[0][0],
            list(vorgaenge.keys())[0],
            "Der Startvorgang ist nicht korrekt zugeordnet."
        )

        self.assertEqual(
            stufen[-1][0],
            list(vorgaenge.keys())[-1],
            "Der Endvorgang ist nicht korrekt zugeordnet."
        )


# ============================================================
# 2. DETAILAUSGABE
# ============================================================

def details_ausgeben(netzplan: Netzplan):

    vorgaenge = netzplan["vorgaenge"]
    kanten = netzplan["kanten"]
    stufen = netzplan["stufen"]

    anzahl_vorgaenger = {
        kennung: 0 for kennung in vorgaenge
    }

    anzahl_nachfolger = {
        kennung: 0 for kennung in vorgaenge
    }

    for vorgaenger, nachfolger in kanten:
        anzahl_nachfolger[vorgaenger] += 1
        anzahl_vorgaenger[nachfolger] += 1

    print("\n========== NETZPLANDETAILS ==========")

    print("\nGENERIERUNGSPARAMETER:")
    print("Schwierigkeitsgrad:", netzplan["schwierigkeitsgrad"])
    print("Vorgangszahl:", netzplan["vorgangszahl"])
    print("Stufenzahl:", netzplan["stufenzahl"])
    print("Maximale Vorgänger:", netzplan["max_vorgaenger"])
    print("Maximale Nachfolger:", netzplan["max_nachfolger"])

    print("\nVORGÄNGE:")

    for kennung, daten in vorgaenge.items():
        print(
            kennung,
            "| Bezeichnung:", daten["bezeichnung"],
            "| Dauer:", daten["dauer"]
        )

    print("\nSTUFEN:")

    for i, stufe in enumerate(stufen):
        print(f"Ebene {i + 1}: {stufe}")

    print("\nKANTEN:")

    for vorgaenger, nachfolger in kanten:
        print(f"{vorgaenger} -> {nachfolger}")

    print("\nVORGÄNGER UND NACHFOLGER:")

    for kennung in vorgaenge:
        print(
            kennung,
            "| Vorgänger:", anzahl_vorgaenger[kennung],
            "| Nachfolger:", anzahl_nachfolger[kennung]
        )

    print("\n=====================================")


# ============================================================
# 3. BENUTZERABFRAGE
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


# ============================================================
# 4. TESTS AUSFÜHREN
# ============================================================

def tests_ausfuehren(netzplan: Netzplan) -> bool:

    NetzplanTests.netzplan = netzplan

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        NetzplanTests
    )

    ausgabe = io.StringIO()

    runner = unittest.TextTestRunner(
        stream=ausgabe,
        verbosity=0
    )

    ergebnis = runner.run(suite)

    anzahl_fehler = len(ergebnis.failures) + len(ergebnis.errors)
    anzahl_bestanden = ergebnis.testsRun - anzahl_fehler

    print("\n========== TESTERGEBNIS ==========")
    print(f"({anzahl_bestanden}/{ergebnis.testsRun}) Tests bestanden.")

    # Fehlgeschlagene Tests ausgeben
    for test, fehler in ergebnis.failures + ergebnis.errors:

        beschreibung = (
            test.shortDescription()
            or test._testMethodName
        )

        fehlerzeilen = fehler.strip().splitlines()
        fehlermeldung = fehlerzeilen[-1] if fehlerzeilen else "Unbekannter Fehler"

        print(f"\nFEHLER: {beschreibung}")
        print(fehlermeldung)

    print("==================================")

    return ergebnis.wasSuccessful()


# ============================================================
# 5. PROGRAMMSTART
# ============================================================

def starten():

    # Netzplan generieren
    try:
        netzplan = netzplan_generieren()

    except Exception as fehler:
        print("\nFEHLER BEI DER NETZPLANGENERIERUNG:")
        print(fehler)
        return

    # Tests ausführen
    if not tests_ausfuehren(netzplan):
        print("\nDer Netzplan hat die Tests nicht bestanden.")
        print("Eine grafische Ausgabe wird nicht erstellt.")
        return

    # Erste Detailabfrage
    if details_abfragen("Details vor der Netzplanausgabe anzeigen?"):
        details_ausgeben(netzplan)

    # Grafische Netzplanausgabe
    print("\n========== NETZPLAN ==========")
    netzplan_ausgeben(
        netzplan["stufen"],
        netzplan["kanten"],
        netzplan["vorgaenge"]
    )

    # Zweite Detailabfrage
    if details_abfragen("Details nach der Netzplanausgabe zusätzlich anzeigen?"):
        details_ausgeben(netzplan)

    print("\nProgramm beendet.")


# ============================================================
# 6. STARTPUNKT
# ============================================================

if __name__ == "__main__":
    starten()