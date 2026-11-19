"""REST-Schnittstelle nur mit Python-Standardbibliothek."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

from generator import SCHWIERIGKEITSPROFILE, netzplan_generieren
from netzplan_ausgabe import netzplan_ausgeben

AUSGABE_DATEI = Path("ausgaben/netzplan.svg")
AUSGABE_DATEI.parent.mkdir(parents=True, exist_ok=True)


class APIHandler(BaseHTTPRequestHandler):
    """Behandelt die REST-Endpunkte des Prototyps."""

    def do_GET(self):
        if self.path == "/health":
            self.json_antwort({"status": "ok"})

        elif self.path == "/api/v1/profile":
            self.json_antwort(SCHWIERIGKEITSPROFILE)

        elif self.path == "/api/v1/netzplan.svg":
            if not AUSGABE_DATEI.exists():
                self.json_antwort({"fehler": "Es wurde noch kein Netzplan erzeugt."}, 404)
            else:
                inhalt = AUSGABE_DATEI.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/svg+xml")
                self.send_header("Content-Length", str(len(inhalt)))
                self.end_headers()
                self.wfile.write(inhalt)

        else:
            self.json_antwort({"fehler": "Endpunkt nicht gefunden."}, 404)

    def do_POST(self):
        if self.path != "/api/v1/netzplaene":
            self.json_antwort({"fehler": "Endpunkt nicht gefunden."}, 404)
            return

        laenge = int(self.headers.get("Content-Length", 0))
        text = self.rfile.read(laenge).decode("utf-8")

        try:
            daten = json.loads(text) if text else {}
            schwierigkeitsgrad = daten.get("schwierigkeitsgrad", "Einfach")
            plan = netzplan_generieren(schwierigkeitsgrad)
            netzplan_ausgeben(plan, AUSGABE_DATEI)
        except (ValueError, RuntimeError) as fehler:
            self.json_antwort({"fehler": str(fehler)}, 400)
            return
        except Exception:
            self.json_antwort({"fehler": "Der Netzplan konnte nicht erstellt werden."}, 500)
            return

        self.json_antwort({**plan, "svg_url": "/api/v1/netzplan.svg"})

    def json_antwort(self, daten, status=200):
        inhalt = json.dumps(daten, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(inhalt)))
        self.end_headers()
        self.wfile.write(inhalt)

    def log_message(self, format_string, *args):
        # Für den einfachen Prototyp werden keine Zugriffslogs ausgegeben.
        pass


if __name__ == "__main__":
    print("Netzplangenerator läuft auf http://localhost:8000")
    HTTPServer(("0.0.0.0", 8000), APIHandler).serve_forever()
