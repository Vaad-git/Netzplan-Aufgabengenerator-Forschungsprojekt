"""REST-Schnittstelle für die Erzeugung von Netzplanaufgaben."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

from netzplan.generator import SCHWIERIGKEITSPROFILE, netzplan_generieren
from netzplan.aufgabenstellung import aufgabenstellung_generieren
from netzplan.ki_aufgabenstellung import bezeichnungen_mit_ki_generieren
from netzplan.netzplan_ausgabe import netzplan_ausgeben

PROJEKTORDNER = Path(__file__).resolve().parent
AUSGABE_DATEI = PROJEKTORDNER / "ausgaben" / "netzplan.svg"
AUSGABE_DATEI.parent.mkdir(parents=True, exist_ok=True)


def netzplan_antwort_erstellen(schwierigkeitsgrad="Einfach", ki_bezeichnungen=False):
    """Erzeugt Netzplan, optionale KI-Bezeichnungen, Aufgabenstellung und SVG."""

    if not isinstance(schwierigkeitsgrad, str):
        raise ValueError("Der Schwierigkeitsgrad muss als Text angegeben werden.")
    if not isinstance(ki_bezeichnungen, bool):
        raise ValueError("ki_bezeichnungen muss true oder false sein.")

    plan = netzplan_generieren(schwierigkeitsgrad)
    bezeichnungen = {}

    if ki_bezeichnungen:
        bezeichnungen = bezeichnungen_mit_ki_generieren(plan)

    netzplan_ausgeben(plan, AUSGABE_DATEI, bezeichnungen=bezeichnungen)
    aufgabenstellung = aufgabenstellung_generieren(plan, bezeichnungen)

    return {
        **plan,
        "bezeichnungen": bezeichnungen,
        "aufgabenstellung": aufgabenstellung,
        "svg_url": "/api/v1/netzplan.svg",
    }


class APIHandler(BaseHTTPRequestHandler):
    """Verarbeitet die REST-Endpunkte des Entwicklungsprototyps."""

    def do_GET(self):
        if self.path == "/health":
            self.json_antwort({"status": "ok"})
        elif self.path == "/api/v1/profile":
            self.json_antwort(SCHWIERIGKEITSPROFILE)
        elif self.path == "/api/v1/netzplan.svg":
            self.svg_antwort()
        else:
            self.json_antwort({"fehler": "Endpunkt nicht gefunden."}, 404)

    def do_POST(self):
        if self.path != "/api/v1/netzplaene":
            self.json_antwort({"fehler": "Endpunkt nicht gefunden."}, 404)
            return

        try:
            laenge = int(self.headers.get("Content-Length", "0"))
            if laenge < 0 or laenge > 65536:
                self.json_antwort({"fehler": "Die Anfrage ist zu groß oder ungültig."}, 413)
                return

            text = self.rfile.read(laenge).decode("utf-8")
            daten = json.loads(text) if text else {}
            if not isinstance(daten, dict):
                raise ValueError("Der Anfrageinhalt muss ein JSON-Objekt sein.")

            schwierigkeitsgrad = daten.get("schwierigkeitsgrad", "Einfach")
            ki_bezeichnungen = daten.get("ki_bezeichnungen", False)
            antwort = netzplan_antwort_erstellen(schwierigkeitsgrad, ki_bezeichnungen)

        except (UnicodeDecodeError, json.JSONDecodeError) as fehler:
            self.json_antwort({"fehler": f"Ungültiger JSON-Anfrageinhalt: {fehler}"}, 400)
            return
        except ValueError as fehler:
            self.json_antwort({"fehler": str(fehler)}, 400)
            return
        except RuntimeError as fehler:
            self.json_antwort({"fehler": str(fehler)}, 502)
            return
        except Exception:
            self.json_antwort({"fehler": "Die Netzplanaufgabe konnte nicht erstellt werden."}, 500)
            return

        self.json_antwort(antwort)

    def svg_antwort(self):
        """Gibt die zuletzt erzeugte SVG-Datei zurück."""

        if not AUSGABE_DATEI.exists():
            self.json_antwort({"fehler": "Es wurde noch kein Netzplan erzeugt."}, 404)
            return

        inhalt = AUSGABE_DATEI.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(inhalt)))
        self.end_headers()
        self.wfile.write(inhalt)

    def json_antwort(self, daten, status=200):
        inhalt = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(inhalt)))
        self.end_headers()
        self.wfile.write(inhalt)

    def log_message(self, format_string, *args):
        """Unterdrückt Standard-Zugriffslogs des einfachen Entwicklungsservers."""

        return


if __name__ == "__main__":
    print("Netzplangenerator-API: http://localhost:8000")
    HTTPServer(("0.0.0.0", 8000), APIHandler).serve_forever()
