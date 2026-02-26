"""
Hauptschleife für den Produktionsbetrieb am Förderband.

Ablauf pro Zyklus:
    1. Frame von Kamera lesen
    2. Span-Erkennung prüfen (mit konfiguriertem Intervall)
    3. Bei Span-Fund: Ausschleuser auslösen
    4. Statistik aktualisieren (für Web-Monitor)
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple
import numpy as np

from core.chip_detector import DetectionResult

logger = logging.getLogger(__name__)


@dataclass
class ProductionStats:
    total: int = 0
    ok: int = 0
    nok: int = 0
    last_result: Optional[bool] = None     # True=OK, False=NOK, None=noch keine Prüfung
    last_check_time: float = 0.0

    @property
    def nok_rate(self) -> float:
        """Ausschussquote in Prozent."""
        return (self.nok / self.total * 100) if self.total > 0 else 0.0


class ConveyorLoop:
    """
    Koordiniert Kamera, Span-Erkennung und Ausschleuser.

    Läuft als Endlosschleife in einem eigenen Thread.
    Das letzte Frame und Ergebnis sind für den Web-Monitor abrufbar.
    """

    def __init__(self, camera, detector, rejector, check_interval_ms: int = 500):
        """
        Args:
            camera:             CameraSource-Instanz
            detector:           ChipDetector-Instanz (mit geladenem Referenzbild)
            rejector:           RejectionController-Instanz
            check_interval_ms:  Prüfintervall in ms - an Bandgeschwindigkeit anpassen.
                                Bei schnellem Band: kleiner Wert, bei langsamem: größer.
        """
        self.camera = camera
        self.detector = detector
        self.rejector = rejector
        self.check_interval = check_interval_ms / 1000.0
        self.stats = ProductionStats()
        self._running = False
        self._last_frame: Optional[np.ndarray] = None
        self._last_result: Optional[DetectionResult] = None

    def start(self) -> None:
        """Startet die Produktionsschleife (blockierend - in Thread aufrufen)."""
        if not self.detector.has_reference:
            raise RuntimeError(
                "Kein Referenzbild geladen! Erst 'python main.py referenz' ausführen."
            )
        self._running = True
        logger.info(
            "Produktionsschleife gestartet (Intervall: %.0f ms)", self.check_interval * 1000
        )
        try:
            self._loop()
        finally:
            self._running = False
            self.camera.release()
            self.rejector.cleanup()
            logger.info("Produktionsschleife beendet.")

    def stop(self) -> None:
        """Stoppt die Schleife sauber."""
        self._running = False

    def get_latest(self) -> Tuple[Optional[np.ndarray], Optional[DetectionResult]]:
        """Gibt aktuelles Frame + letztes Ergebnis zurück (für Web-Monitor)."""
        return self._last_frame, self._last_result

    def _loop(self) -> None:
        next_check = time.time()

        while self._running:
            frame = self.camera.read()

            if frame is None:
                logger.warning("Kein Frame von Kamera - Verbindung prüfen")
                time.sleep(1.0)
                continue

            self._last_frame = frame
            now = time.time()

            if now >= next_check:
                try:
                    result = self.detector.detect(frame)
                except Exception as e:
                    logger.error("Fehler bei Erkennung: %s", e)
                    next_check = now + self.check_interval
                    continue

                self._last_result = result
                self.stats.total += 1
                self.stats.last_check_time = now

                if result.chips_found:
                    self.stats.nok += 1
                    self.stats.last_result = False
                    self.rejector.reject()
                else:
                    self.stats.ok += 1
                    self.stats.last_result = True

                next_check = now + self.check_interval
            else:
                # Kurze Pause um CPU zu schonen
                time.sleep(0.02)
