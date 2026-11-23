"""Tests für die REST-Vorbereitung des Netzplangenerators."""

import unittest
from unittest.mock import patch

import api


class APIAntwortTests(unittest.TestCase):

    def setUp(self):
        self.plan = {
            "schwierigkeitsgrad": "Einfach",
            "vorgangszahl": 2,
            "anzahl_kanten": 1,
            "vorgaenge": {
                "A": {"bezeichnung": "A", "dauer": 2, "ebene": 1},
                "B": {"bezeichnung": "B", "dauer": 3, "ebene": 2},
            },
            "kanten": [
                {"vorgaenger": "A", "nachfolger": "B", "art": "Grundstruktur"}
            ],
            "startvorgaenge": ["A"],
            "endvorgaenge": ["B"],
            "stufen": [["A"], ["B"]],
        }

    @patch("api.netzplan_ausgeben")
    @patch("api.aufgabenstellung_generieren", return_value="Aufgabentext")
    @patch("api.netzplan_generieren")
    def test_antwort_ohne_ki(self, generator_mock, aufgabe_mock, svg_mock):
        generator_mock.return_value = self.plan

        antwort = api.netzplan_antwort_erstellen()

        self.assertEqual(antwort["bezeichnungen"], {})
        self.assertEqual(antwort["aufgabenstellung"], "Aufgabentext")
        self.assertEqual(antwort["svg_url"], "/api/v1/netzplan.svg")
        generator_mock.assert_called_once_with("Einfach")
        aufgabe_mock.assert_called_once_with(self.plan, {})
        svg_mock.assert_called_once()

    @patch("api.netzplan_ausgeben")
    @patch("api.aufgabenstellung_generieren", return_value="KI-Aufgabentext")
    @patch("api.bezeichnungen_mit_ki_generieren", return_value={"A": "Anlage prüfen", "B": "Produkt verpacken"})
    @patch("api.netzplan_generieren")
    def test_antwort_mit_ki(self, generator_mock, ki_mock, aufgabe_mock, svg_mock):
        generator_mock.return_value = self.plan

        antwort = api.netzplan_antwort_erstellen(ki_bezeichnungen=True)

        self.assertEqual(antwort["bezeichnungen"]["A"], "Anlage prüfen")
        self.assertEqual(antwort["aufgabenstellung"], "KI-Aufgabentext")
        ki_mock.assert_called_once_with(self.plan)
        aufgabe_mock.assert_called_once_with(self.plan, ki_mock.return_value)
        svg_mock.assert_called_once()

    def test_ungueltige_ki_option(self):
        with self.assertRaises(ValueError):
            api.netzplan_antwort_erstellen(ki_bezeichnungen="ja")


if __name__ == "__main__":
    unittest.main(verbosity=2)
