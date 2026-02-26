"""
Verwaltet das Referenzbild eines sauberen Drehteils ohne Späne.

Das Referenzbild wird einmalig aufgenommen und gespeichert.
Bei jedem Start wird es automatisch geladen, falls vorhanden.
"""

import cv2
import logging
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class ReferenceManager:
    def __init__(self, reference_path: str):
        self.reference_path = Path(reference_path)
        self.reference_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def exists(self) -> bool:
        return self.reference_path.exists()

    def save(self, image: np.ndarray) -> None:
        """Speichert ein Bild als neues Referenzbild."""
        cv2.imwrite(str(self.reference_path), image)
        logger.info("Referenzbild gespeichert: %s", self.reference_path)

    def load(self) -> Optional[np.ndarray]:
        """Lädt das gespeicherte Referenzbild. Gibt None zurück wenn nicht vorhanden."""
        if not self.exists:
            logger.warning(
                "Kein Referenzbild gefunden unter: %s", self.reference_path
            )
            return None
        img = cv2.imread(str(self.reference_path))
        if img is None:
            logger.error(
                "Referenzbild konnte nicht gelesen werden: %s", self.reference_path
            )
            return None
        logger.info("Referenzbild geladen: %s", self.reference_path)
        return img
