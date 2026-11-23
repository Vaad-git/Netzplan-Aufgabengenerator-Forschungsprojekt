# Gemini Developer API – Einrichtung

Die optionale KI-Namensgebung verwendet die Gemini Developer API. Für die API-Kommunikation wird das offizielle Python-Paket `google-genai` eingesetzt. Der API-Schlüssel wird ausschließlich über die Umgebungsvariable `GEMINI_API_KEY` bereitgestellt.

## 1. API-Schlüssel erstellen

1. Google AI Studio unter <https://aistudio.google.com/> öffnen.
2. Mit einem Google-Konto anmelden.
3. Die Seite <https://aistudio.google.com/apikey> öffnen.
4. Einen API-Schlüssel erstellen oder einen vorhandenen Schlüssel auswählen.
5. Den Schlüssel sicher speichern.

Für den kostenlosen Einstieg ist kein Wechsel auf einen kostenpflichtigen Tarif erforderlich. Die kostenlose Nutzung ist auf bestimmte Modelle und Kontingente begrenzt. Es darf kein kostenpflichtiges Billing-Upgrade aktiviert werden, wenn ausschließlich der kostenlose Tarif verwendet werden soll.

## 2. Modell und kostenloser Tarif

Das Projekt verwendet standardmäßig das Modell `gemini-3.5-flash-lite`. Es ist auf niedrige Latenz und kosteneffiziente Textverarbeitung ausgelegt. Google weist für dieses Modell im kostenlosen API-Tarif kostenlose Ein- und Ausgabetokens aus; die Nutzung bleibt durch modell- und kontingentabhängige Ratenlimits begrenzt. Die Modellkonstante befindet sich in `netzplan/ki_aufgabenstellung.py` unter `GEMINI_MODELL`.

Google kann Modellverfügbarkeit, kostenlose Kontingente und Ratenlimits ändern. Vor einer Änderung des Modellnamens oder bei Fehlermeldungen sind die aktuellen Angaben zu prüfen:

- Preise und kostenlose Kontingente: <https://ai.google.dev/gemini-api/docs/pricing>
- Modellübersicht: <https://ai.google.dev/gemini-api/docs/models>
- Ratenlimits: <https://ai.google.dev/gemini-api/docs/rate-limits>

Im kostenlosen Tarif können übermittelte Inhalte zur Verbesserung von Google-Produkten verwendet werden. Es dürfen daher keine vertraulichen oder personenbezogenen Daten an die API übermittelt werden. Die vom Prototyp erzeugten Netzplandaten sind synthetische Testdaten.

## 3. API-Schlüssel für Docker Compose hinterlegen

Die Datei `.env.example` im Verzeichnis `Netzplan_Generator_V5` dient als Vorlage. Eine lokale `.env`-Datei wird erstellt:

```powershell
Copy-Item .env.example .env
```

Die Datei `.env` öffnen und den tatsächlichen Schlüssel eintragen:

```text
GEMINI_API_KEY=API_SCHLUESSEL
```

Die Datei `.env` muss im selben Verzeichnis wie `docker-compose.yml` liegen. Docker Compose liest sie automatisch ein und übergibt den Wert an den Container.

Die Datei `.env` ist in `.gitignore` ausgeschlossen und darf nicht in das Repository übernommen werden. Für die Versionskontrolle ist ausschließlich `.env.example` ohne echten Schlüssel vorgesehen.

Der Schlüssel darf nicht in Quellcode, Screenshots, öffentlichen Protokollen oder Commit-Nachrichten veröffentlicht werden. Bei einer versehentlichen Veröffentlichung ist der Schlüssel in Google AI Studio zu widerrufen und neu zu erstellen.

## 4. Docker-Container erstellen und starten

Voraussetzungen: Docker Desktop ist installiert und gestartet. Die Befehle werden im Verzeichnis `Netzplan_Generator_V5` ausgeführt.

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

Der Container installiert Graphviz und die Python-Abhängigkeiten aus `requirements.txt`. Die API wird auf Port 8000 gestartet. Die lokale Erreichbarkeit kann geprüft werden mit:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Die API ist unter `http://localhost:8000` erreichbar. Docker Compose bindet den lokalen Ausgabeordner `ausgaben` in den Container ein.

## 5. API-Funktion testen

Zunächst kann ein Netzplan ohne KI-Namensgebung erzeugt werden. Dieser Aufruf prüft die Netzplangenerierung, Aufgabenstellung und SVG-Ausgabe unabhängig von der Gemini API:

```powershell
$body = @{
    schwierigkeitsgrad = "Einfach"
    ki_bezeichnungen = $false
} | ConvertTo-Json

$antwort = Invoke-RestMethod -Method Post `
    -Uri http://localhost:8000/api/v1/netzplaene `
    -ContentType "application/json" `
    -Body $body

$antwort.aufgabenstellung
```

Anschließend kann die KI-Namensgebung aktiviert werden:

```powershell
$body = @{
    schwierigkeitsgrad = "Einfach"
    ki_bezeichnungen = $true
} | ConvertTo-Json

$antwort = Invoke-RestMethod -Method Post `
    -Uri http://localhost:8000/api/v1/netzplaene `
    -ContentType "application/json" `
    -Body $body

$antwort.bezeichnungen
$antwort.aufgabenstellung
```

Die SVG kann unter `http://localhost:8000/api/v1/netzplan.svg` im Browser geöffnet werden. Alternativ befindet sich die Datei lokal unter `ausgaben/netzplan.svg`. Jede erfolgreiche Generierung überschreibt die vorherige SVG-Datei.

## 6. Tests

Die automatisierten Tests verwenden simulierte KI-Antworten. Für sie ist kein echter API-Schlüssel erforderlich. Für lokale Ausführung müssen Python und Graphviz installiert sein:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Ein echter Gemini-Aufruf wird über `main.py` oder den POST-Endpunkt mit `ki_bezeichnungen: true` ausgeführt.

## 7. Logs und Container beenden

Containerlogs anzeigen:

```powershell
docker compose logs -f
```

Container beenden:

```powershell
docker compose down
```

Die SVG-Ausgabe im lokalen Verzeichnis `ausgaben` bleibt erhalten.

## 8. Fehlerbehebung

| Meldung / Status | Mögliche Ursache und Maßnahme |
|---|---|
| API-Schlüssel fehlt oder ungültig | Inhalt und Speicherort der `.env`-Datei prüfen; Container nach Änderungen neu erstellen. |
| Python-Paket fehlt | Docker-Image mit `docker compose up --build -d` neu erstellen. |
| HTTP 400 / 403 von Google | API-Schlüssel, API-Zugriff und Modellverfügbarkeit in Google AI Studio prüfen. |
| HTTP 429 | Kostenloses Kontingent oder Ratenlimit erreicht; Limits prüfen und später erneut versuchen. |
| Modell nicht verfügbar | Modellkennung in `GEMINI_MODELL` und aktuelle Modellübersicht prüfen. |
| Container startet nicht | `docker compose logs` prüfen. |
| Port 8000 belegt | Anderen lokalen Port in `docker-compose.yml` konfigurieren. |

Bei Änderungen an `.env`, `Dockerfile`, `requirements.txt` oder `docker-compose.yml` ist der Container mit `docker compose up --build -d` neu zu erstellen.
