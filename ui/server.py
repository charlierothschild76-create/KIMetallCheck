"""
Web-Monitor für KIMetallCheck.

Zeigt im Browser:
    - Live-Kamerabild mit Span-Markierungen
    - OK/NOK-Zähler und Ausschussquote
    - Status der Kamera und des Referenzbildes
    - Schaltfläche zum Aufnehmen eines neuen Referenzbildes

Aufruf im Browser: http://<IP>:5000
"""

import cv2
import threading
import time
import logging
from flask import Flask, Response, jsonify, request

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Wird von main.py gesetzt
_loop = None          # ConveyorLoop-Instanz
_ref_manager = None   # ReferenceManager-Instanz
_detector = None      # ChipDetector-Instanz
_camera = None        # CameraSource-Instanz (für Referenzaufnahme)


def init(loop, ref_manager, detector, camera):
    """Verbindet den Web-Server mit den Produktions-Objekten."""
    global _loop, _ref_manager, _detector, _camera
    _loop = loop
    _ref_manager = ref_manager
    _detector = detector
    _camera = camera


def _encode_frame(frame):
    """Kodiert ein BGR-Frame als JPEG für den MJPEG-Stream."""
    if frame is None:
        # Platzhalter-Bild wenn keine Kamera
        import numpy as np
        placeholder = 50 * np.ones((480, 640, 3), dtype="uint8")
        cv2.putText(
            placeholder,
            "Keine Kamera",
            (160, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (100, 100, 255),
            2,
        )
        frame = placeholder
    _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
    return jpeg.tobytes()


def _mjpeg_generator():
    """Generator für MJPEG-Livestream."""
    while True:
        frame, result = _loop.get_latest() if _loop else (None, None)
        display = result.annotated_frame if (result and result.annotated_frame is not None) else frame
        jpeg = _encode_frame(display)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
        )
        time.sleep(0.05)  # ~20 fps


@app.route("/")
def index():
    return _html_dashboard()


@app.route("/video_feed")
def video_feed():
    return Response(
        _mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/status")
def api_status():
    """JSON-Endpunkt für Statistiken (wird per JS live abgefragt)."""
    stats = _loop.stats if _loop else None
    ref_exists = _ref_manager.exists if _ref_manager else False
    cam_ok = _camera.is_connected if _camera else False

    return jsonify(
        {
            "total": stats.total if stats else 0,
            "ok": stats.ok if stats else 0,
            "nok": stats.nok if stats else 0,
            "nok_rate": round(stats.nok_rate, 1) if stats else 0.0,
            "last_result": stats.last_result if stats else None,
            "reference_exists": ref_exists,
            "camera_connected": cam_ok,
        }
    )


@app.route("/api/capture_reference", methods=["POST"])
def capture_reference():
    """Nimmt ein neues Referenzbild auf und lädt es in den Detektor."""
    if not _camera or not _ref_manager or not _detector:
        return jsonify({"success": False, "error": "System nicht initialisiert"}), 500

    frame = _camera.capture_single()
    if frame is None:
        return jsonify({"success": False, "error": "Kein Bild von Kamera"}), 503

    _ref_manager.save(frame)
    _detector.set_reference(frame)
    logger.info("Neues Referenzbild aufgenommen via Web-UI")
    return jsonify({"success": True})


def run(host: str = "0.0.0.0", port: int = 5000):
    """Startet den Flask-Server (in eigenem Thread aufrufen)."""
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARNING)  # Flask-Logs reduzieren
    app.run(host=host, port=port, threaded=True, use_reloader=False)


# ---------------------------------------------------------------------------
# HTML-Seite (inline, kein Template-Verzeichnis nötig)
# ---------------------------------------------------------------------------

def _html_dashboard() -> str:
    return """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KIMetallCheck - Spänerkennung</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }
  header { background: #16213e; padding: 16px 24px; display: flex; align-items: center; gap: 16px; border-bottom: 2px solid #0f3460; }
  header h1 { font-size: 1.4rem; font-weight: 600; color: #e94560; }
  header .subtitle { font-size: 0.85rem; color: #888; }
  .main { display: grid; grid-template-columns: 1fr 320px; gap: 16px; padding: 16px; height: calc(100vh - 72px); }
  .camera-box { background: #16213e; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; }
  .camera-box img { max-width: 100%; max-height: 100%; object-fit: contain; }
  .sidebar { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; }
  .card { background: #16213e; border-radius: 8px; padding: 16px; border-left: 4px solid #0f3460; }
  .card h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: #888; margin-bottom: 10px; }
  .status-badge { display: inline-block; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 1.1rem; }
  .ok { background: #1a4731; color: #4ade80; }
  .nok { background: #4b1c1c; color: #f87171; }
  .neutral { background: #333; color: #aaa; }
  .stat-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #0f3460; }
  .stat-row:last-child { border-bottom: none; }
  .stat-label { color: #888; font-size: 0.85rem; }
  .stat-value { font-size: 1.2rem; font-weight: 600; }
  .stat-value.green { color: #4ade80; }
  .stat-value.red { color: #f87171; }
  .stat-value.yellow { color: #fbbf24; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
  .dot.green { background: #4ade80; }
  .dot.red { background: #f87171; }
  .dot.gray { background: #555; }
  button { width: 100%; padding: 12px; border-radius: 6px; border: none; cursor: pointer; font-size: 0.95rem; font-weight: 600; transition: opacity 0.2s; }
  button:hover { opacity: 0.85; }
  .btn-ref { background: #0f3460; color: #eee; }
  .btn-ref:active { background: #0a2545; }
  .toast { position: fixed; bottom: 20px; right: 20px; padding: 12px 20px; border-radius: 8px; font-weight: 600; opacity: 0; transition: opacity 0.3s; }
  .toast.show { opacity: 1; }
  .toast.success { background: #1a4731; color: #4ade80; }
  .toast.error { background: #4b1c1c; color: #f87171; }
</style>
</head>
<body>
<header>
  <div>
    <h1>KIMetallCheck</h1>
    <div class="subtitle">Spänerkennung an Drehteilen</div>
  </div>
</header>
<div class="main">
  <div class="camera-box">
    <img src="/video_feed" alt="Kamerabild">
  </div>
  <div class="sidebar">
    <div class="card">
      <h2>Letztes Ergebnis</h2>
      <div id="last-result" class="status-badge neutral">Warte auf Prüfung...</div>
    </div>
    <div class="card">
      <h2>Statistik</h2>
      <div class="stat-row">
        <span class="stat-label">Geprüft gesamt</span>
        <span class="stat-value" id="total">0</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">OK</span>
        <span class="stat-value green" id="ok">0</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">NOK (Span)</span>
        <span class="stat-value red" id="nok">0</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Ausschussquote</span>
        <span class="stat-value yellow" id="nok-rate">0.0 %</span>
      </div>
    </div>
    <div class="card">
      <h2>Systemstatus</h2>
      <div class="stat-row">
        <span class="stat-label"><span class="dot gray" id="dot-cam"></span>Kamera</span>
        <span id="cam-status" style="font-size:0.85rem">-</span>
      </div>
      <div class="stat-row">
        <span class="stat-label"><span class="dot gray" id="dot-ref"></span>Referenzbild</span>
        <span id="ref-status" style="font-size:0.85rem">-</span>
      </div>
    </div>
    <div class="card">
      <h2>Referenzbild</h2>
      <p style="font-size:0.8rem;color:#888;margin-bottom:10px;">
        Sauberes Drehteil <strong>ohne Späne</strong> vor die Kamera legen, dann aufnehmen.
      </p>
      <button class="btn-ref" onclick="captureReference()">Referenz aufnehmen</button>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast ' + type + ' show';
  setTimeout(() => t.className = 'toast', 3000);
}

async function captureReference() {
  try {
    const r = await fetch('/api/capture_reference', { method: 'POST' });
    const d = await r.json();
    if (d.success) showToast('Referenzbild gespeichert!', 'success');
    else showToast('Fehler: ' + d.error, 'error');
  } catch(e) { showToast('Verbindungsfehler', 'error'); }
}

async function updateStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('total').textContent = d.total;
    document.getElementById('ok').textContent = d.ok;
    document.getElementById('nok').textContent = d.nok;
    document.getElementById('nok-rate').textContent = d.nok_rate.toFixed(1) + ' %';

    const badge = document.getElementById('last-result');
    if (d.last_result === true)  { badge.textContent = 'OK - Kein Span'; badge.className = 'status-badge ok'; }
    else if (d.last_result === false) { badge.textContent = 'NOK - SPAN!'; badge.className = 'status-badge nok'; }

    const camDot = document.getElementById('dot-cam');
    const camTxt = document.getElementById('cam-status');
    camDot.className = 'dot ' + (d.camera_connected ? 'green' : 'red');
    camTxt.textContent = d.camera_connected ? 'Verbunden' : 'Getrennt';

    const refDot = document.getElementById('dot-ref');
    const refTxt = document.getElementById('ref-status');
    refDot.className = 'dot ' + (d.reference_exists ? 'green' : 'red');
    refTxt.textContent = d.reference_exists ? 'Vorhanden' : 'Fehlt!';
  } catch(e) {}
}

setInterval(updateStatus, 1000);
updateStatus();
</script>
</body>
</html>"""
