# KIMetallCheck - Spänerkennung an Drehteilen

Erkennt anhaftende Späne (Metallspäne) an Stahl-Drehteilen auf dem Förderband und löst automatisch einen Pneumatikzylinder zum Ausschleusen aus.

## Schnellstart

```bash
pip install -r requirements.txt

# 1. Einmalig: Referenzbild aufnehmen (sauberes Teil ohne Späne)
python main.py referenz

# 2. Produktionsbetrieb starten
python main.py

# Browser öffnen: http://localhost:5000
```

## Kamera einrichten (Handy)

1. Android-App **"IP Webcam"** installieren (kostenlos)
2. App starten → "Server starten"
3. Angezeigte IP-Adresse in `config.py` eintragen:
   ```python
   CAMERA_SOURCE = "http://192.168.x.x:8080/video"
   ```

## Ausschleuser konfigurieren

In `config.py`:

| Wert | Beschreibung |
|------|-------------|
| `REJECTION_MODE = "mock"` | Test ohne Hardware (Konsolenausgabe) |
| `REJECTION_MODE = "rpi"` | Raspberry Pi GPIO-Pin |
| `REJECTION_MODE = "relay"` | USB-Relay-Modul |
| `REJECTION_DURATION_MS = 400` | Impulsdauer in ms |

## Erkennungsparameter anpassen

| Parameter | Wert | Bedeutung |
|-----------|------|-----------|
| `DIFF_THRESHOLD` | 35 | Empfindlichkeit (niedriger = sensitiver) |
| `MIN_CHIP_AREA` | 400 | Mindestgröße Span in px² |
| `CHECK_INTERVAL_MS` | 500 | Prüfintervall (an Bandgeschwindigkeit anpassen) |

## Projektstruktur

```
core/
  chip_detector.py       # Spanerkennung (Differenzbild-Methode)
  reference_manager.py   # Referenzbild verwalten
  conveyor_loop.py       # Produktionsschleife
io/
  camera_source.py       # Kamera-Abstraktion (USB / Handy-Stream)
  rejection_controller.py # Ausschleuser (GPIO / USB-Relay / Mock)
ui/
  server.py              # Web-Monitor (Flask)
data/references/         # Referenzbilder sauberer Teile
config.py                # Alle Einstellungen
main.py                  # Einstiegspunkt
```
