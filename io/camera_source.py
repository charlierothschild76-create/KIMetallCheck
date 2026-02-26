"""
Kamera-Abstraktion für verschiedene Quellen.

Unterstützte Quellen:
    USB-Webcam:   CameraSource(0)
    Handy-Stream: CameraSource("http://192.168.x.x:8080/video")
                  → Android: App "IP Webcam" installieren, Stream starten
    Videodatei:   CameraSource("test.mp4")   (für Tests ohne Hardware)
"""

import cv2
import time
import logging
from typing import Optional, Union
import numpy as np

logger = logging.getLogger(__name__)


class CameraSource:
    def __init__(self, source: Union[int, str], reconnect_delay: float = 3.0):
        """
        Args:
            source:           Kamera-Index (int) oder Stream-URL (str)
            reconnect_delay:  Sekunden bis zum nächsten Verbindungsversuch
        """
        self.source = source
        self.reconnect_delay = reconnect_delay
        self._cap: Optional[cv2.VideoCapture] = None
        self._last_connect_attempt = 0.0
        self._connect()

    def _connect(self) -> None:
        now = time.time()
        if now - self._last_connect_attempt < self.reconnect_delay:
            return
        self._last_connect_attempt = now

        if self._cap:
            self._cap.release()

        self._cap = cv2.VideoCapture(self.source)
        if self._cap.isOpened():
            # Puffergröße 1: immer das aktuellste Bild lesen (kein Versatz)
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            logger.info("Kamera verbunden: %s", self.source)
        else:
            self._cap = None
            if isinstance(self.source, str) and self.source.startswith("http"):
                logger.warning(
                    "Handy-Stream nicht erreichbar: %s\n"
                    "  → IP Webcam App starten\n"
                    "  → URL in config.py prüfen (CAMERA_SOURCE)",
                    self.source,
                )
            else:
                logger.warning("Kamera nicht erreichbar: %s", self.source)

    def read(self) -> Optional[np.ndarray]:
        """
        Liest einen Frame.
        Gibt None zurück wenn Kamera nicht verfügbar (reconnect wird automatisch versucht).
        """
        if self._cap is None or not self._cap.isOpened():
            self._connect()
            return None

        ret, frame = self._cap.read()
        if not ret:
            logger.warning("Frame-Lesefehler - reconnect...")
            self._cap.release()
            self._cap = None
            return None

        return frame

    def capture_single(self) -> Optional[np.ndarray]:
        """Nimmt ein Einzelbild auf (für Referenzaufnahme)."""
        # Mehrere Frames verwerfen damit Auto-Exposure eingeschwungen ist
        for _ in range(5):
            self.read()
            time.sleep(0.1)
        return self.read()

    def release(self) -> None:
        """Gibt die Kamera frei."""
        if self._cap:
            self._cap.release()
            self._cap = None
            logger.info("Kamera freigegeben")

    @property
    def is_connected(self) -> bool:
        return self._cap is not None and self._cap.isOpened()
