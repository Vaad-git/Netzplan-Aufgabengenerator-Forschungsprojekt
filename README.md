# Netzplan-Aufgabengenerator

Forschungs- und Entwicklungsprojekt zur dynamischen Erzeugung, Darstellung und Bewertung von Netzplanaufgaben im Kontext von VocationALADIN.

## Aktueller Entwicklungsstand

Der aktive Entwicklungsstand befindet sich in [`Netzplan_Generator_V5/`](Netzplan_Generator_V5/). V5 umfasst die zufällige Netzplangenerierung, die SVG-Ausgabe, eine strukturierte Aufgabenstellung, optionale KI-generierte Vorgangsbezeichnungen über die Gemini Developer API, die Musterlösungsberechnung sowie einen direkten Einzelvergleich mit einer Schülerlösung. Zusätzlich stehen ein lokaler Konsolentest und eine einfache REST-Schnittstelle zur Verfügung.

Die Funktionen und bekannten Einschränkungen sind in der [V5-Projektdokumentation](Netzplan_Generator_V5/README.md) beschrieben. Die [technische Ablaufübersicht](Netzplan_Generator_V5/docs/Netzplan_Generator_V5_Ablaufuebersicht.adoc) dokumentiert den Aufbau und die Generierungslogik.

## Repository-Struktur

```text
Netzplan-Aufgabengenerator-Forschungsprojekt/
├── Netzplan_Generator_V5/    # Aktiver Entwicklungsstand
├── Backup/                   # Historische Prototypen V3 und V4
├── konzept-netzplangenerator-v4.adoc  # Historisches Konzept V4
└── README.md                 # Repository-Übersicht
```

Die Verzeichnisse `Backup/Python_Prototyp_V3/`, `Backup/Netzplan_Generator_V4/` und das separate Konzeptdokument V4 sind historische Entwicklungsstände. Sie werden in dieser Projektfassung nicht aktualisiert.
