"""
Craig chat box — drop-in Flask blueprint for the Dead Brands CRM portal.

What it does: adds a "Craig" panel to the portal where David can chat
with Craig directly. The portal is ONLY a UI client — Craig's brain stays
on his own Cloudflare Worker. The portal forwards David's messages to the
Worker's Telegram-style endpoint and renders the reply.

Deploy (parent-side, on the PC portal):
  1. Copy this file to <portal>/app/craig_chat.py
  2. Copy templates/craig_panel.html to <portal>/app/templates/craig_panel.html
  3. In <portal>/app/main.py:  from .craig_chat import bp as craig_bp;
     app.register_blueprint(craig_bp)
  4. Set env on the portal host: CRAIG_WORKER_URL, CRAIG_PORTAL_SECRET
     (shared secret the Worker checks on /portal-message — add it as a
     wrangler secret too, and extend the Worker's fetch() accordingly)
  5. Restart the portal. The panel appears for logged-in users only
     (reuse the portal's existing @login_required).

Auth: reuses the portal's session auth — never expose this blueprint
without login_required.
"""
import os
import hmac
import requests
from flask import Blueprint, request, jsonify, render_template, session

bp = Blueprint("craig", __name__, url_prefix="/craig")

WORKER_URL = os.environ.get("CRAIG_WORKER_URL", "").rstrip("/")
PORTAL_SECRET = os.environ.get("CRAIG_PORTAL_SECRET", "")
TIMEOUT = 60


def _signed(payload: dict) -> dict:
    """Attach an HMAC so the Worker knows the message came from the portal."""
    import json as _json
    body = _json.dumps(payload, sort_keys=True)
    sig = hmac.new(PORTAL_SECRET.encode(), body.encode(), "sha256").hexdigest()
    return {"payload": payload, "sig": sig}


@bp.route("/panel")
def panel():
    # Wrap with the portal's login decorator at registration time if the
    # portal exposes one; otherwise ensure main.py registers with protection.
    return render_template("craig_panel.html")


@bp.route("/api/message", methods=["POST"])
def message():
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "empty"}), 400
    if not WORKER_URL or not PORTAL_SECRET:
        return jsonify({"ok": False, "error": "craig not configured"}), 503

    who = session.get("user_email", "david")  # portal session identity
    try:
        r = requests.post(
            f"{WORKER_URL}/portal-message",
            json=_signed({"from": who, "text": text}),
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        reply = r.json().get("reply", "")
        return jsonify({"ok": True, "reply": reply})
    except Exception as e:  # noqa: BLE001 — surface as portal error, log server-side
        return jsonify({"ok": False, "error": f"worker unreachable: {type(e).__name__}"}), 502


@bp.route("/api/status")
def status():
    try:
        r = requests.get(f"{WORKER_URL}/health", timeout=10)
        return jsonify({"ok": True, "worker": r.json()})
    except Exception as e:  # noqa: BLE001
        return jsonify({"ok": False, "error": type(e).__name__}), 502
