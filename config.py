# Konfiguration KIMetallCheck - Spänerkennung an Drehteilen
# Alle Werte können über Umgebungsvariablen überschrieben werden.
import os

# ---------------------------------------------------------------------------
# Kamera
# ---------------------------------------------------------------------------
# Handy (Android "IP Webcam" App): "http://192.168.x.x:8080/video"
# USB-Webcam:                       0  (oder 1, 2, ...)
# Videodatei zum Testen:            "test.mp4"
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "http://192.168.178.119:8080/video")

# ---------------------------------------------------------------------------
# Spänerkennung
# ---------------------------------------------------------------------------
# Pixeldifferenz ab der eine Abweichung als Span gewertet wird (0-255)
# Niedrig = empfindlich (mehr Fehlalarme), Hoch = robuster (übersieht kleine Späne)
DIFF_THRESHOLD = int(os.getenv("DIFF_THRESHOLD", "35"))

# Mindestfläche einer erkannten Kontur in Pixeln²
# Zu kleiner Wert → Bildrauschen wird als Span erkannt
MIN_CHIP_AREA = int(os.getenv("MIN_CHIP_AREA", "400"))

# Wie oft pro Sekunde geprüft wird (abhängig von Bandgeschwindigkeit)
CHECK_INTERVAL_MS = int(os.getenv("CHECK_INTERVAL_MS", "500"))

# ---------------------------------------------------------------------------
# Ausschleuser (Pneumatikzylinder)
# ---------------------------------------------------------------------------
# "mock"  → nur Konsolenausgabe (Testen ohne Hardware)
# "rpi"   → Raspberry Pi GPIO-Pin
# "relay" → USB-Relay-Modul (serielle Schnittstelle)
REJECTION_MODE = os.getenv("REJECTION_MODE", "mock")

# Raspberry Pi: BCM-Pinnummer
REJECTION_GPIO_PIN = int(os.getenv("REJECTION_GPIO_PIN", "17"))

# USB-Relay: serieller Port
REJECTION_RELAY_PORT = os.getenv("REJECTION_RELAY_PORT", "/dev/ttyUSB0")

# Dauer des Ausschleuse-Impulses in Millisekunden
REJECTION_DURATION_MS = int(os.getenv("REJECTION_DURATION_MS", "400"))

# ---------------------------------------------------------------------------
# Referenzbilder
# ---------------------------------------------------------------------------
REFERENCE_DIR = os.getenv("REFERENCE_DIR", "data/references")
REFERENCE_IMAGE = os.path.join(REFERENCE_DIR, "clean_part.jpg")

# ---------------------------------------------------------------------------
# Web-Monitor
# ---------------------------------------------------------------------------
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "5000"))
