NETZPLAN-GENERATOR V4
====================

Dateien
-------
main.py
    Enthält das Schwierigkeitsprofil, die Generierungslogik und die
    strukturelle Validierung. Die Funktion netzplan_generieren() liefert
    einen vollständigen Netzplan als Datenstruktur zurück.

tests.py
    Führt kurze Strukturtests aus, zeigt auf Wunsch die Details und startet
    die grafische Ausgabe. Die Tests sind bewusst nur Kontrollmechanismen;
    sie sind nicht Teil der eigentlichen Generierungslogik.

netzplan_ausgabe.py
    Erstellt die Graphviz-SVG-Darstellung. Die Datei ausgaben/netzplan.svg
    wird bei jedem Lauf überschrieben.

ausgaben/
    Zielordner für die SVG-Datei.

Installation
------------
1. Graphviz für Windows installieren.
2. Sicherstellen, dass Graphvizs bin-Ordner (dot.exe) im PATH liegt.
3. Im Projektordner ausführen:

       python -m pip install -r requirements.txt

Start
-----
Im Projektordner ausführen:

       python tests.py

Aktuelle Generierungslogik
--------------------------
- Vorgangszahl und Dauern werden zufällig aus dem Profil gezogen.
- Start und Ende sind jeweils einzelne Vorgänge.
- Die mittleren Vorgänge werden zufällig in Sammlungen von maximal drei
  Vorgängen gruppiert.
- Zwischen benachbarten Sammlungen wird eine zusammenhängende Grundstruktur
  erzeugt: Jeder Vorgang besitzt einen Vorgänger und einen Nachfolger,
  ausgenommen Start und Ende.
- Die Anzahl der Verzweigungs- und Zusammenführungsknoten wird unabhängig
  aus den jeweiligen Profilbereichen ausgewählt.
- Zusätzliche strukturelle Kanten dürfen Ebenen überspringen und werden so
  gewählt, dass die Zielanzahl an Verzweigungen und Zusammenführungen entsteht.
- Optionale weitere Kanten werden nur zwischen bereits verzweigenden und
  bereits zusammenführenden Vorgängen ergänzt. Sie erzeugen keine neuen
  Verzweigungs- oder Zusammenführungsknoten.
- Die Ebenen werden nach der Kantenstruktur anhand des längsten Pfades vom
  Startvorgang abgeleitet.
- Die maximale Ebenenbreite beträgt aktuell drei Vorgänge. Daraus wird auch
  eine maximale Vorgänger- und Nachfolgerzahl von drei abgeleitet.
- Kreisläufe, isolierte Vorgänge, fehlende Verbindungen, doppelte Kanten und
  Überschreitungen der Grenzwerte werden verhindert bzw. erkannt.

Noch nicht enthalten
--------------------
- Berechnung der Netzplanzeiten und des kritischen Pfades.
- Musterlösung und automatische Bewertung von Schülerantworten.
- REST-Schnittstelle und ALADIN-Integration.
