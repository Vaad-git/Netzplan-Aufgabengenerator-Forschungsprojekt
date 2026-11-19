"""Wenige grundlegende Tests für den Netzplangenerator."""

import unittest
from pathlib import Path

from generator import netzplan_generieren, netzplan_validieren
from netzplan_ausgabe import netzplan_ausgeben


class NetzplanTests(unittest.TestCase):
    def test_100_generierungen(self):
        for _ in range(100):
            plan = netzplan_generieren()
            netzplan_validieren(plan)

    def test_anzahl_verzweigungen_und_zusammenfuehrungen(self):
        plan = netzplan_generieren()
        self.assertEqual(plan["anzahl_verzweigungen"], plan["soll_verzweigungen"])
        self.assertEqual(plan["anzahl_zusammenfuehrungen"], plan["soll_zusammenfuehrungen"])

    def test_start_und_ende(self):
        plan = netzplan_generieren()
        self.assertEqual(len(plan["startvorgaenge"]), plan["soll_startvorgaenge"])
        self.assertEqual(len(plan["endvorgaenge"]), plan["soll_endvorgaenge"])

    def test_graphviz_ausgabe(self):
        plan = netzplan_generieren()
        datei = netzplan_ausgeben(plan, "ausgaben/test-netzplan.svg")
        self.assertTrue(Path(datei).exists())
        self.assertIn("<svg", Path(datei).read_text(encoding="utf-8"))
        Path(datei).unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
