"""Erzeugt sinnvolle Vorgangsbezeichnungen mit der Gemini Developer API."""

import json
import os


# Dieses Modell ist laut aktueller Google-Preisseite im kostenlosen Tarif verfügbar.
GEMINI_MODELL = "gemini-3.5-flash-lite"


def _netzplan_fuer_ki_aufbereiten(netzplan):
    """Bereitet Vorgänge, Dauern, Ebenen und direkte Abhängigkeiten für die KI auf."""

    vorgaenge = netzplan["vorgaenge"]
    vorgaenger = {name: [] for name in vorgaenge}
    nachfolger = {name: [] for name in vorgaenge}

    for kante in netzplan["kanten"]:
        von = kante["vorgaenger"]
        nach = kante["nachfolger"]
        vorgaenger[nach].append(von)
        nachfolger[von].append(nach)

    daten = []

    for name, vorgang in vorgaenge.items():
        daten.append({
            "id": name,
            "dauer": vorgang["dauer"],
            "ebene": vorgang.get("ebene"),
            "direkte_vorgaenger": sorted(vorgaenger[name]),
            "direkte_nachfolger": sorted(nachfolger[name]),
        })

    return daten


def _bezeichnungen_validieren(bezeichnungen, vorgangsnamen):
    """Prüft, ob die KI genau einen eindeutigen Namen pro Vorgang geliefert hat."""

    if not isinstance(bezeichnungen, dict):
        raise ValueError("Die KI-Antwort ist kein JSON-Objekt.")

    if set(bezeichnungen) != set(vorgangsnamen):
        raise ValueError("Die KI-Antwort enthält fehlende oder zusätzliche Vorgangs-IDs.")

    ergebnis = {}
    bereits_verwendete_namen = set()

    for name in vorgangsnamen:
        bezeichnung = bezeichnungen[name]

        if not isinstance(bezeichnung, str):
            raise ValueError(f"Die Bezeichnung für Vorgang {name} ist kein Text.")

        bezeichnung = " ".join(bezeichnung.strip().split())

        if not bezeichnung:
            raise ValueError(f"Die Bezeichnung für Vorgang {name} ist leer.")

        if len(bezeichnung) > 70:
            raise ValueError(f"Die Bezeichnung für Vorgang {name} ist zu lang.")

        vergleichsname = bezeichnung.casefold()
        if vergleichsname in bereits_verwendete_namen:
            raise ValueError("Die KI hat eine Vorgangsbezeichnung mehrfach vergeben.")

        bereits_verwendete_namen.add(vergleichsname)
        ergebnis[name] = bezeichnung

    return ergebnis


def bezeichnungen_mit_ki_generieren(netzplan, modell=GEMINI_MODELL):
    """Erzeugt für jeden Vorgang einen passenden Namen mit der Gemini API.

    Die KI darf ausschließlich die Bezeichnungen erzeugen. Vorgangs-IDs,
    Dauern und Abhängigkeiten des eigentlichen Netzplans bleiben unverändert.
    Der API-Schlüssel wird aus der Umgebungsvariable GEMINI_API_KEY gelesen.
    """

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Der Gemini-API-Schlüssel fehlt. Setze die Umgebungsvariable "
            "GEMINI_API_KEY. Die Einrichtung steht in KI_SETUP.md."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as fehler:
        raise RuntimeError(
            "Das Gemini-Python-Paket fehlt. Installiere es mit: "
            "python -m pip install -r requirements.txt"
        ) from fehler

    vorgangsdaten = _netzplan_fuer_ki_aufbereiten(netzplan)
    vorgangsnamen = list(netzplan["vorgaenge"])

    # Das JSON-Schema begrenzt die Antwort auf exakt die vorhandenen Vorgangs-IDs.
    json_schema = {
        "type": "object",
        "properties": {
            name: {"type": "string"} for name in vorgangsnamen
        },
        "required": vorgangsnamen,
        "additionalProperties": False,
    }

    system_prompt = (
        "Du bist ein Experte für Projektplanung und formulierst präzise, "
        "natürliche deutsche Vorgangsbezeichnungen. "
        "Du erhältst einen bereits feststehenden Netzplan. "
        "Erfinde keine Vorgänge und ändere keine Abhängigkeiten oder Dauern. "
        "Gib jedem vorhandenen Vorgang genau eine kurze, eindeutige und "
        "inhaltlich sinnvolle Bezeichnung mit ungefähr 2 bis 5 Wörtern. "
        "Verwende möglichst eine Tätigkeit mit einem passenden Objekt, "
        "zum Beispiel 'Materialbestand prüfen' oder 'Maschinen vorbereiten'. "
        "Alle Bezeichnungen müssen zu EINEM gemeinsamen, realistischen "
        "Projekt passen und inhaltlich zueinander passen. "
        "Berücksichtige Dauer, Ebene sowie direkte Vorgänger und Nachfolger. "
        "Startvorgänge beschreiben vorbereitende oder initiale Tätigkeiten, "
        "niemals bereits den Projektabschluss. Endvorgänge beschreiben "
        "passende abschließende Tätigkeiten. Zwischenschritte müssen zum "
        "Ablauf passen. Die Bezeichnungen müssen untereinander verschieden sein. "
        "Liefere ausschließlich ein JSON-Objekt mit den vorgegebenen IDs "
        "als Schlüsseln und den Bezeichnungen als Textwerten. Keine Erklärung."
    )

    user_prompt = (
        "Erzeuge passende Bezeichnungen für diesen Netzplan. "
        "Die Daten enthalten die tatsächlichen direkten Abhängigkeiten:\n"
        + json.dumps(vorgangsdaten, ensure_ascii=False, indent=2)
    )

    try:
        # Der Client wird nach der Anfrage wieder geschlossen.
        with genai.Client(api_key=api_key) as client:
            antwort = client.models.generate_content(
                model=modell,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_json_schema=json_schema,
                    temperature=0.3,
                    max_output_tokens=1024,
                ),
            )
    except Exception as fehler:
        raise RuntimeError(
            "Die Anfrage an die Gemini API ist fehlgeschlagen. "
            "Prüfe den API-Schlüssel, das Modell und das kostenlose Kontingent. "
            f"Details: {fehler}"
        ) from fehler

    try:
        if not antwort.text:
            raise ValueError("Die Gemini-Antwort enthält keinen Text.")
        ki_bezeichnungen = json.loads(antwort.text)
        return _bezeichnungen_validieren(ki_bezeichnungen, vorgangsnamen)
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as fehler:
        raise RuntimeError(
            f"Gemini hat keine gültigen Vorgangsbezeichnungen geliefert: {fehler}"
        ) from fehler
