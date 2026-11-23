# Netzplangenerator V5

V5 ist ein Entwicklungsprototyp zur zufälligen Erzeugung gerichteter, kreislauffreier Netzpläne und zugehöriger Netzplanaufgaben. Der Prototyp umfasst die Netzplangenerierung, die regelbasierte Aufgabenstellung, optionale KI-Vorgangsbezeichnungen mit der Gemini Developer API, die Berechnung einer Musterlösung sowie einen direkten Soll-Ist-Vergleich.

## Funktionsumfang

- Zufällige Netzpläne auf Grundlage vordefinierter Schwierigkeitsprofile
- Zusammenhängende Grundstruktur durch schrittweise Collection-Zusammenführung
- Ergänzung notwendiger Verzweigungen und Zusammenführungen
- Validierung der erzeugten Netzstruktur
- SVG-Ausgabe mit Graphviz
- Strukturierte Aufgabenstellung mit Vorgangsdauern und direkten Abhängigkeiten
- Optionale KI-generierte Vorgangsbezeichnungen über die Gemini Developer API
- Berechnung von FAZ, FEZ, SAZ, SEZ und Gesamtpuffer
- Direkter Einzelvergleich von Schülerwerten und Musterlösung
- Lokaler Konsolentest und einfache REST-Schnittstelle

Die zusammenhängende textuelle Projektbeschreibung sowie eine Folgefehlerbewertung sind noch nicht implementiert.

## Projektstruktur

```text
Netzplan_Generator_V5/
├── netzplan/                 # Fachlogik und Ausgabefunktionen
│   ├── generator.py          # Netzplangenerierung und Validierung
│   ├── musterloesung.py      # Zeitrechnung und direkter Lösungsvergleich
│   ├── aufgabenstellung.py   # Strukturierte Aufgabenstellung
│   ├── ki_aufgabenstellung.py# Gemini-Anbindung und Namensvalidierung
│   └── netzplan_ausgabe.py   # Graphviz-/SVG-Ausgabe
├── tests/                    # Automatisierte Tests
├── docs/                     # Technische Dokumentation und KI-Einrichtung
├── ausgaben/                 # Generierte SVG-Datei
├── api.py                    # REST-Einstiegspunkt
├── main.py                   # Lokaler Konsolen-Einstiegspunkt
├── Dockerfile                # Containerdefinition
├── docker-compose.yml        # Lokale Container-Orchestrierung
├── requirements.txt          # Python-Abhängigkeiten
└── README.md
```

## Voraussetzungen

Für den lokalen Betrieb werden benötigt:

- Python 3.10 oder neuer
- Graphviz als Systemprogramm; der Befehl `dot` muss im `PATH` verfügbar sein
- Für die KI-Namensgebung: ein Gemini-API-Schlüssel und das Python-Paket `google-genai`

Die Python-Abhängigkeiten werden im Projektordner installiert:

```powershell
python -m pip install -r requirements.txt
```

## Gemini API

Die KI-Namensgebung ist optional. Der API-Schlüssel wird über die Umgebungsvariable `GEMINI_API_KEY` bereitgestellt. Eine detaillierte Einrichtung, Hinweise zum kostenlosen Tarif und Datenschutz sowie Fehlerbehebung sind in [`docs/KI_SETUP.md`](docs/KI_SETUP.md) beschrieben.

PowerShell, nur für das aktuelle Terminal:

```powershell
$env:GEMINI_API_KEY = "API_SCHLUESSEL"
```

Ohne verfügbaren API-Schlüssel bleibt der lokale Prototyp nutzbar; die strukturierte Aufgabenstellung verwendet dann die technischen Vorgangs-IDs.

## Lokaler Konsolentest

Im Verzeichnis `Netzplan_Generator_V5`:

```powershell
python main.py
```

Der Ablauf erzeugt einen Netzplan, die SVG-Grafik und eine strukturierte Aufgabenstellung. Sofern ein API-Schlüssel verfügbar ist, werden zuvor KI-Bezeichnungen erzeugt. Anschließend stehen drei Eingabemodi zur Verfügung:

1. Manuelle Eingabe der fünf Zeitwerte je Vorgang
2. Automatische Übernahme der Musterlösung als Test
3. Automatische Übernahme der Musterlösung mit einem zufällig ausgewählten, um eins erhöhten Wert

Die SVG-Datei wird unter `ausgaben/netzplan.svg` gespeichert und bei einer neuen Generierung überschrieben.

## Tests

Alle Tests werden aus dem Verzeichnis `Netzplan_Generator_V5` gestartet:

```powershell
python -m unittest discover -s tests -v
```

Die Tests für Datenaufbereitung, Antwortvalidierung, Musterlösung, Vergleich und API-Antwortaufbau benötigen keinen gültigen Gemini-API-Schlüssel. Ein echter API-Aufruf wird separat über `python main.py` oder die REST-Schnittstelle mit aktivierter KI-Option geprüft.

## REST-Schnittstelle

Die REST-Schnittstelle wird lokal gestartet mit:

```powershell
python api.py
```

| Methode | Pfad | Zweck |
|---|---|---|
| GET | `/health` | Dienststatus |
| GET | `/api/v1/profile` | Verfügbare Schwierigkeitsprofile |
| POST | `/api/v1/netzplaene` | Netzplan und Aufgabenstellung erzeugen |
| GET | `/api/v1/netzplan.svg` | Zuletzt erzeugte SVG-Datei abrufen |

Beispiel für eine Anfrage ohne KI:

```json
{
  "schwierigkeitsgrad": "Einfach",
  "ki_bezeichnungen": false
}
```

Beispiel für eine Anfrage mit KI-Namensgebung:

```json
{
  "schwierigkeitsgrad": "Einfach",
  "ki_bezeichnungen": true
}
```

Die JSON-Antwort enthält den Netzplan, die gegebenenfalls erzeugten Bezeichnungen, den strukturierten Aufgabentext und die URL der SVG-Datei. Die Musterlösung wird nicht über diesen öffentlichen Entwicklungsendpunkt ausgegeben. Eine Schnittstelle zur Abgabe und Bewertung von Schülerlösungen ist noch nicht implementiert.

Die API verwendet derzeit den Python-Standardserver `HTTPServer`, verarbeitet Anfragen nacheinander und besitzt keine Authentifizierung. Sie ist daher als Entwicklungs- und Integrationsprototyp vorgesehen, nicht als produktiver öffentlicher Dienst.

## Docker

Docker installiert Graphviz und die in `requirements.txt` aufgeführten Python-Pakete. Für die optionale KI-Namensgebung kann `GEMINI_API_KEY` über die Umgebungsvariable oder eine lokale `.env`-Datei bereitgestellt werden.

```powershell
docker compose up --build
```

Die API ist anschließend unter `http://localhost:8000` erreichbar. Zum Beenden:

```powershell
docker compose down
```

## Bekannte Einschränkungen

- Das Profil `Einfach` ist derzeit das einzige implementierte Schwierigkeitsprofil.
- Es werden ausschließlich Ende-Anfang-Abhängigkeiten verwendet.
- Die Strukturerweiterung verhindert doppelte identische Kanten, prüft aber keine transitive Redundanz.
- Branch- und Merge-Zielzahlen werden exakt angestrebt; nicht erreichbare Generierungsversuche werden verworfen.
- Der Musterlösungsvergleich bewertet jeden Wert unabhängig und berücksichtigt keine Folgefehler.
- Die KI erzeugt nur Vorgangsbezeichnungen; die Netzstruktur, Dauern und Abhängigkeiten bleiben deterministisch durch den Generator vorgegeben.
- Die KI-Ausgabe wird formal validiert; eine fachliche Qualitätskontrolle der erzeugten Bezeichnungen bleibt erforderlich.
- Die Fließtext-Aufgabenvariante, eine Eingabeoberfläche und eine vollständige Integration in VocationALADIN sind noch offen.
