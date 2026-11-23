# Netzplangenerator V5

Ein kleiner Python-Prototyp zur Erzeugung gerichteter, kreislauffreier Netzpläne. Die Collections werden schrittweise verbunden. Der Generator kann lokal oder in Docker laufen und stellt eine einfache REST-Schnittstelle bereit.

## Was ist bewusst einfach gehalten?

- Kein Seed und keine Möglichkeit, Zufallsfolgen über einen Seed zu reproduzieren.
- Keine gesonderte Logging-Konfiguration oder Fehlerprotokoll-Dateien.
- Keine externen Python-Pakete. REST wird mit der Python-Standardbibliothek umgesetzt.
- Graphviz wird als Systemprogramm für die SVG-Grafik verwendet.
- Ein Schwierigkeitsprofil, das später erweitert werden kann.
- Eine SVG-Ausgabedatei, die bei jeder neuen Generierung überschrieben wird.

## Projektdateien

```text
Netzplan_Generator_V5_vereinfacht/
├── generator.py          # Schwierigkeitsprofil und gesamte Generierungslogik
├── netzplan_ausgabe.py   # Graphviz-Grafik
├── api.py                # einfache REST-Schnittstelle mit Python-Standardbibliothek
├── main.py               # lokaler Testlauf ohne REST
├── tests.py              # wenige automatische Tests
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .dockerignore
└── ausgaben/
```

## Wie der Generator arbeitet

1. Ein Schwierigkeitsprofil legt die Wertebereiche fest.
2. Die Vorgänge A, B, C usw. werden erzeugt und erhalten zufällige Dauern.
3. Jeder Vorgang startet in einer eigenen Collection.
4. Eine zufällige topologische Reihenfolge legt fest, in welche Richtung Kanten verlaufen dürfen.
5. Zwei getrennte Collections werden ausgewählt. Eine zulässige Kante verbindet zwei Vorgänge aus diesen Collections; anschließend werden die Collections vereinigt.
6. Das wird wiederholt, bis eine gemeinsame Collection übrig bleibt.
7. Falls noch Verzweigungen oder Zusammenführungen fehlen, werden nur dafür benötigte Kanten ergänzt.
8. Zum Schluss werden die Ebenen aus dem längsten Pfad berechnet und der fertige Netzplan geprüft.

Die Ebenen haben keinen Einfluss auf die Generierung. Sie werden nur für die Grafik und mögliche spätere Auswertung verwendet.

## Aktuelles Profil „Einfach"

| Parameter | Werte |
|---|---:|
| Vorgänge | 6–8 |
| Vorgangsdauer | 1–5 |
| Startvorgänge | 1–2 |
| Endvorgänge | 1–2 |
| Verzweigungen | 1–2 |
| Zusammenführungen | 1–2 |
| Maximale Vorgänger | 3 |
| Maximale Nachfolger | 3 |

Die konkrete Anzahl wird bei jeder Generierung zufällig aus dem Profil gewählt. Nicht jede beliebige Kombination ist mathematisch möglich; der Generator berücksichtigt das bei der Auswahl.

## Start mit Docker

Voraussetzung ist Docker Desktop bzw. Docker Engine mit Docker Compose.

Im Projektordner:

```bash
docker compose up --build
```

Die API ist dann erreichbar unter:

- Health-Check: http://localhost:8000/health
- Profile: http://localhost:8000/api/v1/profile

Zum Erzeugen eines Netzplans wird eine POST-Anfrage an `http://localhost:8000/api/v1/netzplaene` gesendet.

Beispiel mit PowerShell:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/api/v1/netzplaene `
  -ContentType "application/json" `
  -Body '{"schwierigkeitsgrad":"Einfach"}'
```

Die Antwort enthält Vorgänge, Kanten, Start- und Endvorgänge, Verzweigungen, Zusammenführungen, Ebenen und die URL der Grafik.

Die Grafik kann anschließend im Browser geöffnet werden:

http://localhost:8000/api/v1/netzplan.svg

Jede neue Generierung überschreibt die vorherige Grafik unter `ausgaben/netzplan.svg`.

Wenn ein anderer Container im selben Docker-Netzwerk läuft, kann er den Generator unter `http://netzplan-generator:8000` aufrufen. Für ein separates ALADIN-Compose-Projekt richten wir später ein gemeinsames Docker-Netzwerk ein.

Docker stoppen:

```bash
docker compose down
```

## Lokal ohne Docker starten

Voraussetzungen: Python 3.10 oder neuer und Graphviz als Systemprogramm. Der Befehl `dot` muss im PATH liegen. Python-Pakete müssen nicht installiert werden.

```bash
python main.py
```

Die REST-Schnittstelle kann lokal mit `python api.py` gestartet werden.

Die Grafik wird unter `ausgaben/netzplan.svg` gespeichert.

## Tests

Die Tests benötigen außer Python und Graphviz keine weiteren Pakete:

```bash
python -m unittest tests -v
```

Die Tests verwenden normale Zufallswerte. Es gibt bewusst keine Seed-Einstellungen.

## REST-Endpunkte

| Methode | Pfad | Zweck |
|---|---|---|
| GET | `/health` | Prüft, ob der Dienst läuft |
| GET | `/api/v1/profile` | Gibt die verfügbaren Profilwerte zurück |
| POST | `/api/v1/netzplaene` | Erzeugt einen Netzplan |
| GET | `/api/v1/netzplan.svg` | Gibt die zuletzt erzeugte Grafik zurück |

Beispiel für den POST-Body:

```json
{
  "schwierigkeitsgrad": "Einfach"
}
```

Die API ist für den Entwicklungsprototyp gedacht. Der eingebaute Python-HTTP-Server verarbeitet Anfragen nacheinander. Für einen späteren produktiven Einsatz mit Vocation ALADIN kann bei Bedarf ein leistungsfähigerer Server ergänzt werden. Die eigentliche Generierungslogik muss dafür nicht verändert werden.
