"""Tests der Aufbereitung und Validierung für die KI-Namensgebung."""

import os
import unittest
from unittest.mock import patch

from netzplan.ki_aufgabenstellung import (
    _netzplan_fuer_ki_aufbereiten,
    _bezeichnungen_validieren,
    bezeichnungen_mit_ki_generieren,
)


class KINamensgebungTests(unittest.TestCase):

    def setUp(self):
        self.netzplan = {
            "vorgaenge": {
                "A": {"dauer": 5, "ebene": 1},
                "B": {"dauer": 2, "ebene": 2},
                "C": {"dauer": 4, "ebene": 2},
                "D": {"dauer": 3, "ebene": 3},
            },
            "kanten": [
                {"vorgaenger": "A", "nachfolger": "B"},
                {"vorgaenger": "A", "nachfolger": "C"},
                {"vorgaenger": "B", "nachfolger": "D"},
                {"vorgaenger": "C", "nachfolger": "D"},
            ],
        }

    def test_netplan_wird_mit_ebenen_und_abhaengigkeiten_aufbereitet(self):
        daten = _netzplan_fuer_ki_aufbereiten(self.netzplan)
        vorgang_d = next(item for item in daten if item["id"] == "D")

        self.assertEqual(vorgang_d["dauer"], 3)
        self.assertEqual(vorgang_d["ebene"], 3)
        self.assertEqual(vorgang_d["direkte_vorgaenger"], ["B", "C"])
        self.assertEqual(vorgang_d["direkte_nachfolger"], [])

    def test_gueltige_bezeichnungen(self):
        namen = {"A": "Anlage vorbereiten", "B": "Material prüfen"}
        ergebnis = _bezeichnungen_validieren(namen, ["A", "B"])
        self.assertEqual(ergebnis, namen)

    def test_fehlende_id_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            _bezeichnungen_validieren({"A": "Anlage vorbereiten"}, ["A", "B"])

    def test_doppelte_bezeichnung_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            _bezeichnungen_validieren(
                {"A": "Material prüfen", "B": "Material prüfen"},
                ["A", "B"],
            )

    def test_leere_bezeichnung_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            _bezeichnungen_validieren({"A": "   "}, ["A"])

    def test_fehlender_api_schluessel_wird_erkannt(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                bezeichnungen_mit_ki_generieren(self.netzplan)


if __name__ == "__main__":
    unittest.main(verbosity=2)
