"""
Ausschleuse-Steuerung für den Pneumatikzylinder.

Unterstützte Modi:
    "mock"  → Nur Konsolenausgabe (Entwicklung, Tests ohne Hardware)
    "rpi"   → Raspberry Pi GPIO-Ausgang (direkter Pin → Relais → Ventil)
    "relay" → USB-Relay-Modul über serielle Schnittstelle
              (z.B. SainSmart USB Relay, CH340-basiert)

Anschluss Pneumatik:
    GPIO-Pin → Relais-Modul → 24V Magnetventil → Zylinder
    Oder: USB-Relay → 24V Magnetventil → Zylinder
"""

import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RejectionController:
    def __init__(
        self,
        mode: str = "mock",
        gpio_pin: int = 17,
        relay_port: str = "/dev/ttyUSB0",
        duration_ms: int = 400,
    ):
        """
        Args:
            mode:        "mock", "rpi" oder "relay"
            gpio_pin:    BCM-Pin am Raspberry Pi (Standard: GPIO17 = Pin 11)
            relay_port:  Serieller Port des USB-Relay-Moduls
            duration_ms: Impulsdauer in ms (wie lange der Zylinder ausfährt)
        """
        self.mode = mode
        self.gpio_pin = gpio_pin
        self.relay_port = relay_port
        self.duration_s = duration_ms / 1000.0
        self._gpio = None
        self._serial = None
        self._reject_count = 0
        self._setup()

    def _setup(self) -> None:
        if self.mode == "rpi":
            try:
                import RPi.GPIO as GPIO
                self._gpio = GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.gpio_pin, GPIO.OUT, initial=GPIO.LOW)
                logger.info("Raspberry Pi GPIO %d (BCM) initialisiert", self.gpio_pin)
            except ImportError:
                logger.error("RPi.GPIO nicht installiert → Fallback auf mock")
                self.mode = "mock"
            except Exception as e:
                logger.error("GPIO-Initialisierung fehlgeschlagen: %s → mock", e)
                self.mode = "mock"

        elif self.mode == "relay":
            try:
                import serial
                self._serial = serial.Serial(self.relay_port, 9600, timeout=1)
                logger.info("USB-Relay auf Port %s geöffnet", self.relay_port)
            except ImportError:
                logger.error("pyserial nicht installiert → pip install pyserial → Fallback auf mock")
                self.mode = "mock"
            except Exception as e:
                logger.error("Relay-Verbindung fehlgeschlagen (%s): %s → mock", self.relay_port, e)
                self.mode = "mock"

        if self.mode == "mock":
            logger.info(
                "Ausschleuser im MOCK-Modus - kein echtes IO-Signal wird gesendet"
            )

    def reject(self) -> None:
        """Löst den Pneumatikzylinder für die konfigurierte Dauer aus."""
        self._reject_count += 1
        logger.warning(
            "AUSSCHLEUSER ausgelöst (#%d, %.0f ms, Modus: %s)",
            self._reject_count,
            self.duration_s * 1000,
            self.mode,
        )

        if self.mode == "rpi" and self._gpio:
            self._gpio.output(self.gpio_pin, self._gpio.HIGH)
            time.sleep(self.duration_s)
            self._gpio.output(self.gpio_pin, self._gpio.LOW)

        elif self.mode == "relay" and self._serial:
            # SainSmart USB Relay Protokoll:
            # Einschalten: 0xA0, Relay-Nr (1-basiert), 0x01, Checksumme
            # Ausschalten: 0xA0, Relay-Nr, 0x00, Checksumme
            self._serial.write(bytes([0xA0, 0x01, 0x01, 0xA2]))
            time.sleep(self.duration_s)
            self._serial.write(bytes([0xA0, 0x01, 0x00, 0xA1]))

        else:
            # Mock: visuelle Ausgabe in der Konsole
            bar = "=" * 40
            print(f"\n  {bar}")
            print(f"  >>> AUSSCHLEUSER #{self._reject_count} <<<")
            print(f"  >>> Impuls: {self.duration_s*1000:.0f} ms (MOCK) <<<")
            print(f"  {bar}\n")

    @property
    def reject_count(self) -> int:
        return self._reject_count

    def cleanup(self) -> None:
        """Gibt Hardware-Ressourcen frei (bei Programmende aufrufen)."""
        if self.mode == "rpi" and self._gpio:
            try:
                self._gpio.output(self.gpio_pin, self._gpio.LOW)
                self._gpio.cleanup()
                logger.info("GPIO freigegeben")
            except Exception:
                pass
        if self._serial:
            try:
                # Sicherheitshalber Relay ausschalten
                self._serial.write(bytes([0xA0, 0x01, 0x00, 0xA1]))
                self._serial.close()
                logger.info("Relay-Verbindung geschlossen")
            except Exception:
                pass
