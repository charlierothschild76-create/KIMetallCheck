# KI-gestützte Inspektions-App für Metallteile

Diese Anwendung dient der automatisierten Inspektion von Metallteilen mittels Künstlicher Intelligenz. Sie nutzt modernste Objektdetektionsmodelle (wie YOLOv8) zur Erkennung von Defekten auf Metalloberflächen und integriert eine präzise Maßprüfung basierend auf computergestützter Bildverarbeitung.

## Funktionen

- **Defekterkennung:** Identifizierung verschiedener Defektarten (Kratzer, Risse, Dellen, Korrosion) auf Metalloberflächen.
- **Maßprüfung:** Präzise Messung von Bauteilmaßen und Erkennung von Abweichungen gegenüber Sollmaßen.
- **Robustheit:** Algorithmen zur Kompensation variabler Lichtverhältnisse und Reflexionen.
- **Echtzeitfähigkeit:** Optimiert für schnelle Bildverarbeitung und geringe Latenz in industriellen Umgebungen.
- **Benutzeroberfläche:** Interaktives Dashboard zur Visualisierung von Defekten und Maßabweichungen, Berichterstellung und Datenexport.
- **Modelltraining und Update:** Modulare Pipeline für kontinuierliches Modelltraining und -aktualisierung.
- **Schnittstellen:** API und Dateischnittstellen zur Integration in bestehende Fertigungssysteme.

## Projektstruktur

```
metal_inspection_app/
├── venv/                   # Virtuelle Python-Umgebung
├── app/                    # Hauptanwendungsordner
│   ├── api/                # API-Endpunkte
│   ├── models/             # KI-Modelle (YOLOv8, etc.)
│   ├── services/           # Geschäftslogik und Bildverarbeitung
│   ├── static/             # Statische Dateien (Frontend-Assets)
│   ├── templates/          # HTML-Templates (für Flask-Frontend)
│   └── main.py             # Hauptanwendungsdatei (Flask-App)
├── requirements.txt        # Python-Abhängigkeiten
├── README.md               # Projektbeschreibung
└── todo.md                 # Aufgabenliste
```

## Installation

1.  **Klonen Sie das Repository:**

    ```bash
    git clone <repository_url>
    cd metal_inspection_app
    ```

2.  **Virtuelle Umgebung einrichten und aktivieren:**

    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Abhängigkeiten installieren:**

    ```bash
    pip install -r requirements.txt
    ```

## Nutzung

Weitere Anweisungen zur Nutzung der Anwendung folgen in späteren Phasen der Entwicklung.


