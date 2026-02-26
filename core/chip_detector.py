"""
Spanerkennung für Stahl-Drehteile mittels Differenzbild-Methode.

Prinzip:
    1. Referenzbild (sauberes Drehteil) wird geladen
    2. Neues Frame wird mit Referenz verglichen (Pixeldifferenz)
    3. Starke Abweichungen mit genügend Fläche = Span erkannt
    4. Annotiertes Bild für Web-Monitor wird erstellt
"""

import cv2
import numpy as np
import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    chips_found: bool
    chip_count: int
    contours: List = field(default_factory=list)
    diff_image: Optional[np.ndarray] = None
    annotated_frame: Optional[np.ndarray] = None
    confidence: float = 0.0


class ChipDetector:
    """Erkennt anhaftende Späne auf gedrehten Stahlteilen."""

    def __init__(self, diff_threshold: int = 35, min_chip_area: int = 400):
        """
        Args:
            diff_threshold: Pixelwert-Unterschied ab dem eine Abweichung
                            als möglicher Span gewertet wird (0–255).
                            Niedrig = empfindlicher, Hoch = robuster.
            min_chip_area:  Mindestfläche einer Kontur in Pixeln².
                            Filtert Bildrauschen heraus.
        """
        self.diff_threshold = diff_threshold
        self.min_chip_area = min_chip_area
        self._reference: Optional[np.ndarray] = None
        # Elliptischer Kernel für morphologische Operationen
        self._kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

    @property
    def has_reference(self) -> bool:
        return self._reference is not None

    def set_reference(self, image: np.ndarray) -> None:
        """
        Setzt das Referenzbild (sauberes Drehteil ohne Späne).
        Muss vor detect() aufgerufen werden.
        """
        self._reference = self._preprocess(image)
        logger.info(
            "Referenzbild gesetzt (%dx%d px)",
            self._reference.shape[1],
            self._reference.shape[0],
        )

    def detect(self, frame: np.ndarray) -> DetectionResult:
        """
        Analysiert ein Frame auf anhaftende Späne.

        Args:
            frame: BGR-Bild von der Kamera (numpy array)

        Returns:
            DetectionResult mit Ergebnis, Konturen und Debug-Bildern
        """
        if not self.has_reference:
            raise RuntimeError(
                "Kein Referenzbild vorhanden. Erst set_reference() aufrufen "
                "oder Modus 'referenz' starten."
            )

        gray = self._preprocess(frame)

        # 1. Differenzbild: Abweichung vom Referenzbild
        diff = cv2.absdiff(gray, self._reference)

        # 2. Binärmaske: Pixel über Schwellwert = möglicher Span
        _, mask = cv2.threshold(diff, self.diff_threshold, 255, cv2.THRESH_BINARY)

        # 3. Morphologisches Öffnen: Kleines Rauschen entfernen
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self._kernel)
        # Leichtes Aufweiten damit zusammenhängende Späne eine Kontur bilden
        mask = cv2.dilate(mask, self._kernel, iterations=1)

        # 4. Konturen finden
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # 5. Kleine Konturen (Rauschen) herausfiltern
        chip_contours = [
            c for c in contours if cv2.contourArea(c) > self.min_chip_area
        ]

        # 6. Annotiertes Bild für Web-Monitor erstellen
        annotated = frame.copy()
        if chip_contours:
            for contour in chip_contours:
                cv2.drawContours(annotated, [contour], -1, (0, 0, 255), 2)
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 220), 1)
            cv2.putText(
                annotated,
                f"NOK - SPAN ({len(chip_contours)}x)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2,
            )
        else:
            cv2.putText(
                annotated,
                "OK",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 200, 0),
                2,
            )

        chips_found = len(chip_contours) > 0
        # Confidence = Anteil der Span-Pixel an der Gesamtbildfläche
        confidence = (
            float(np.count_nonzero(mask)) / float(mask.size)
            if chips_found
            else 0.0
        )

        if chips_found:
            logger.warning(
                "SPAN ERKANNT: %d Kontur(en), confidence=%.4f",
                len(chip_contours),
                confidence,
            )
        else:
            logger.debug("OK - kein Span erkannt")

        return DetectionResult(
            chips_found=chips_found,
            chip_count=len(chip_contours),
            contours=chip_contours,
            diff_image=diff,
            annotated_frame=annotated,
            confidence=confidence,
        )

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Graubild + CLAHE Kontrastverstärkung.
        CLAHE gleicht ungleichmäßige Beleuchtung und Stahlreflexionen aus.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)
