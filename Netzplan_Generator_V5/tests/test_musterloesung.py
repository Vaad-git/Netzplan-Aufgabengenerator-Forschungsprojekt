
"""Tests für die Berechnung und den Vergleich der Musterlösung."""

import unittest

from netzplan.musterloesung import musterloesung_berechnen, loesung_vergleichen


class MusterloesungTests(unittest.TestCase):

    def setUp(self):
        # Fest vorgegebener Netzplan zum Testen.
        self.netzplan = {
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
            ]
        }

        # Die von Hand berechnete Musterlösung.
        self.erwartete_werte = {
            "A": {"FAZ": 0, "FEZ": 6, "SAZ": 0, "SEZ": 6, "GP": 0},
            "B": {"FAZ": 0, "FEZ": 3, "SAZ": 6, "SEZ": 9, "GP": 6},
            "C": {"FAZ": 6, "FEZ": 11, "SAZ": 6, "SEZ": 11, "GP": 0},
            "D": {"FAZ": 6, "FEZ": 10, "SAZ": 7, "SEZ": 11, "GP": 1},
            "E": {"FAZ": 3, "FEZ": 5, "SAZ": 9, "SEZ": 11, "GP": 6},
            "F": {"FAZ": 11, "FEZ": 15, "SAZ": 11, "SEZ": 15, "GP": 0},
            "G": {"FAZ": 15, "FEZ": 17, "SAZ": 15, "SEZ": 17, "GP": 0},
        }

        self.musterloesung = musterloesung_berechnen(self.netzplan)

    def test_musterloesung_berechnen(self):
        self.assertEqual(self.musterloesung["projektdauer"], 17)
        self.assertEqual(
            self.musterloesung["vorgaenge"],
            self.erwartete_werte
        )

    def test_alle_schuelerwerte_richtig(self):
        schuelerloesung = {
            "vorgaenge": {
                name: werte.copy()
                for name, werte in self.erwartete_werte.items()
            }
        }

        ergebnis = loesung_vergleichen(
            self.musterloesung,
            schuelerloesung
        )

        self.assertEqual(ergebnis["anzahl_richtig"], 35)
        self.assertEqual(ergebnis["anzahl_werte"], 35)
        self.assertTrue(ergebnis["alles_korrekt"])

    def test_ein_falscher_wert(self):
        schuelerloesung = {
            "vorgaenge": {
                name: werte.copy()
                for name, werte in self.erwartete_werte.items()
            }
        }

        # SAZ von Vorgang D absichtlich falsch eintragen.
        schuelerloesung["vorgaenge"]["D"]["SAZ"] = 6

        ergebnis = loesung_vergleichen(
            self.musterloesung,
            schuelerloesung
        )

        self.assertEqual(ergebnis["anzahl_richtig"], 34)
        self.assertFalse(
            ergebnis["vorgaenge"]["D"]["werte"]["SAZ"]["richtig"]
        )
        self.assertFalse(ergebnis["alles_korrekt"])

    def test_fehlender_wert(self):
        schuelerloesung = {
            "vorgaenge": {
                name: werte.copy()
                for name, werte in self.erwartete_werte.items()
            }
        }

        # FAZ von Vorgang A nicht eintragen.
        del schuelerloesung["vorgaenge"]["A"]["FAZ"]

        ergebnis = loesung_vergleichen(
            self.musterloesung,
            schuelerloesung
        )

        self.assertEqual(ergebnis["anzahl_richtig"], 34)
        self.assertFalse(
            ergebnis["vorgaenge"]["A"]["werte"]["FAZ"]["richtig"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
