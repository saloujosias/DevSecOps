import os
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException
from flask import Flask, request, jsonify, abort, make_response, render_template_string

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("JWT_SECRET", "dev-secret-CHANGE-ME")
app.config["JSON_SORT_KEYS"] = False

HOME = """
<h1>Mission Pipeline</h1>
<p>Objectif : sécuriser <b>la supply chain</b> (build/test/scan), les <b>secrets</b>, et l'app (<b>SSRF</b>, auth, logs).</p>
<ul>
  <li><a href="/status">/status</a></li>
  <li><a href="/whoami">/whoami</a></li>
  <li><a href="/fetch?url=http://example.com">/fetch</a></li>
  <li><a href="/admin?token=...">/admin</a></li>
  <li><a href="/docs">/docs</a></li>
</ul>
<p><b>Note</b> : tout reste local. Les “flags” sont dans les variables d’environnement.</p>
"""

@app.get("/")
def index():
    return render_template_string(HOME)

@app.get("/status")
def status():
    return jsonify({"service": "escape-app-expert", "ok": True})

@app.get("/whoami")
def whoami():
    user = request.headers.get("X-User", "anonymous")
    resp = make_response(jsonify({"user": user}))
    resp.set_cookie("session", "dev", httponly=False, samesite="Lax")
    return resp

@app.get("/fetch")
def fetch():
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    try:
        parsed = urlparse(url)
    except Exception:
        return jsonify({"error": "Invalid URL"}), 400

    if parsed.scheme not in {"http", "https"}:
        return jsonify({"error": "Only http and https URLs are allowed"}), 400

    if not parsed.hostname:
        return jsonify({"error": "Invalid hostname"}), 400

    hostname = parsed.hostname.lower().strip()

    # Blocage explicite des hôtes internes
    blocked_hosts = {"localhost", "127.0.0.1", "::1", "vault"}
    if hostname in blocked_hosts:
        return jsonify({"error": "Access to this host is forbidden"}), 403

    # Blocage simple des IP privées les plus classiques
    if hostname.startswith("10.") or hostname.startswith("192.168.") or hostname.startswith("172.16."):
        return jsonify({"error": "Access to this host is forbidden"}), 403

    try:
        response = requests.get(url, timeout=2, allow_redirects=False)
        return (
            response.text,
            response.status_code,
            {"Content-Type": response.headers.get("Content-Type", "text/plain")}
        )
    except RequestException:
        return jsonify({"error": "Upstream request failed"}), 502

@app.get("/admin")
def admin():
    token = request.args.get("token", "")
    if token != os.getenv("ADMIN_TOKEN", ""):
        abort(403)

    return jsonify({
        "admin": True,
        "flag_supply_chain": os.getenv("FLAG_SUPPLY", "FLAG{missing}"),
        "hint": "Try auditing the pipeline scripts & dependencies. Also check internal services.",
    })

@app.get("/docs")
def docs():
    return render_template_string("""
<h2>DevSecOps targets (expert)</h2>
<ol>
  <li>Supply chain: tests + SAST + dependency audit + image scan + SBOM + signing</li>
  <li>Secrets hygiene: no .env committed, no tokens in repo, add secret scanning</li>
  <li>AppSec: SSRF mitigation, auth hardening, safer cookies, logging</li>
  <li>Build hardening: pin base image, non-root user, .dockerignore, minimal image</li>
</ol>
<p>Tip: there is an internal service on the Docker network you should not be able to read from the web app.</p>
""")

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "access denied"}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "internal server error"}), 500

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug)