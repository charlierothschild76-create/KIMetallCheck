"""
KIMetallCheck - Haupteinstiegspunkt
Spänerkennung an Drehteilen am Förderband

Verwendung:
    python main.py              → Produktionsbetrieb starten
    python main.py referenz     → Referenzbild aufnehmen (einmalig, vor Produktionsstart)
    python main.py demo         → Demo ohne Handy-Kamera (USB-Webcam 0, Mock-Ausschleuser)
"""

import sys
import threading
import logging
import time

import config
from core.chip_detector import ChipDetector
from core.reference_manager import ReferenceManager
from core.conveyor_loop import ConveyorLoop
from hardware.camera_source import CameraSource
from hardware.rejection_controller import RejectionController
import ui.server as web_server

# ---------------------------------------------------------------------------
# Logging konfigurieren
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def mode_referenz():
    """
    Referenzmodus: Nimmt ein Bild eines sauberen Drehteils auf und speichert es.
    Dieser Schritt muss VOR dem Produktionsbetrieb einmalig durchgeführt werden.
    """
    logger.info("=== REFERENZ-MODUS ===")
    logger.info("Sauberes Drehteil OHNE Späne vor die Kamera legen.")
    logger.info("Kamera: %s", config.CAMERA_SOURCE)

    camera = CameraSource(config.CAMERA_SOURCE)
    ref_manager = ReferenceManager(config.REFERENCE_IMAGE)

    for _ in range(10):
        if camera.is_connected:
            break
        logger.info("Warte auf Kamera...")
        time.sleep(1.0)

    if not camera.is_connected:
        logger.error("Kamera nicht erreichbar. CAMERA_SOURCE in config.py prüfen.")
        sys.exit(1)

    input("\n  >>> ENTER drücken wenn das Drehteil korrekt positioniert ist <<<\n")

    frame = camera.capture_single()
    if frame is None:
        logger.error("Kein Bild von der Kamera erhalten.")
        camera.release()
        sys.exit(1)

    ref_manager.save(frame)
    camera.release()

    logger.info("Referenzbild gespeichert: %s", config.REFERENCE_IMAGE)
    logger.info("Jetzt Produktionsbetrieb starten: python main.py")


def mode_produktion(camera_source=None):
    """
    Produktionsbetrieb: Überwacht das Förderband und schleust NOK-Teile aus.
    """
    logger.info("=== PRODUKTIONSBETRIEB ===")
    logger.info("Kamera:       %s", camera_source or config.CAMERA_SOURCE)
    logger.info("Ausschleuser: %s (Dauer: %d ms)", config.REJECTION_MODE, config.REJECTION_DURATION_MS)
    logger.info("Schwellwert:  %d | Min. Fläche: %d px²", config.DIFF_THRESHOLD, config.MIN_CHIP_AREA)

    camera = CameraSource(camera_source or config.CAMERA_SOURCE)
    detector = ChipDetector(
        diff_threshold=config.DIFF_THRESHOLD,
        min_chip_area=config.MIN_CHIP_AREA,
    )
    rejector = RejectionController(
        mode=config.REJECTION_MODE,
        gpio_pin=config.REJECTION_GPIO_PIN,
        relay_port=config.REJECTION_RELAY_PORT,
        duration_ms=config.REJECTION_DURATION_MS,
    )
    ref_manager = ReferenceManager(config.REFERENCE_IMAGE)

    ref_image = ref_manager.load()
    if ref_image is None:
        logger.warning(
            "Kein Referenzbild vorhanden!\n"
            "  → 'python main.py referenz' ausführen\n"
            "  → Oder im Browser http://localhost:%d Referenz aufnehmen",
            config.WEB_PORT,
        )
    else:
        detector.set_reference(ref_image)

    loop = ConveyorLoop(
        camera=camera,
        detector=detector,
        rejector=rejector,
        check_interval_ms=config.CHECK_INTERVAL_MS,
    )

    web_server.init(loop, ref_manager, detector, camera)

    prod_thread = threading.Thread(target=_run_loop, args=(loop,), daemon=True)
    prod_thread.start()

    logger.info("Web-Monitor: http://localhost:%d", config.WEB_PORT)
    logger.info("Im Netzwerk: http://<IP-Adresse>:%d", config.WEB_PORT)
    logger.info("Strg+C zum Beenden")

    try:
        web_server.run(host=config.WEB_HOST, port=config.WEB_PORT)
    except KeyboardInterrupt:
        logger.info("Beende...")
        loop.stop()
        prod_thread.join(timeout=3.0)


def _run_loop(loop):
    """Wrapper für ConveyorLoop.start() - startet nur wenn Referenz vorhanden."""
    if loop.detector.has_reference:
        loop.start()
    else:
        # Warten bis Referenz über Web-UI aufgenommen wird
        logger.info("Warte auf Referenzbild (über Web-UI aufnehmen)...")
        while not loop.detector.has_reference:
            time.sleep(1.0)
        logger.info("Referenzbild erkannt - Produktionsschleife startet")
        loop.start()


if __name__ == "__main__":
    modus = sys.argv[1] if len(sys.argv) > 1 else "produktion"

    if modus == "referenz":
        mode_referenz()
    elif modus == "demo":
        logger.info("DEMO-Modus: USB-Webcam (0), Mock-Ausschleuser")
        mode_produktion(camera_source=0)
    elif modus == "produktion":
        mode_produktion()
    else:
        print(__doc__)
        sys.exit(1)
