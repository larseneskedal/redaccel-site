"""
Flask web application for the Redaccel marketing website.
"""
from flask import Flask, render_template, request, jsonify, abort, redirect, send_from_directory
import socket
import os
import smtplib
import requests
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import TemplateNotFound
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Local dev quality-of-life: don't aggressively cache templates/static.
# IMPORTANT: keep this scoped to local dev only (Render/gunicorn should keep defaults).
_is_local_dev = os.getenv("FLASK_ENV") == "development" or os.getenv("DEBUG") == "True"
if _is_local_dev:
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    try:
        app.jinja_env.auto_reload = True
    except Exception:
        # If Jinja env isn't ready for some reason, fail open.
        pass


@app.route("/<filename>.html")
def serve_verification_file(filename: str):
    """
    Serve third-party HTML verification files from `static/verification/` at the site root.

    Many providers require a file like `abc123.html` to be accessible at:
    https://www.example.com/abc123.html
    """
    safe = (filename or "").strip()
    if "/" in safe or "\\" in safe or ".." in safe:
        abort(404)

    verification_dir = os.path.join(app.static_folder or "static", "verification")
    requested = f"{safe}.html"
    file_path = os.path.join(verification_dir, requested)
    if not os.path.isfile(file_path):
        # Not a verification file — fall through to the static site (e.g. /404.html)
        return _serve_site_path(requested)

    return send_from_directory(verification_dir, requested)


def _request_host():
    """Host the client used (respects X-Forwarded-Host behind Render/proxies)."""
    raw = request.headers.get("X-Forwarded-Host") or request.host or ""
    # Can be "host" or "host:port" or "host1, host2" (proxies)
    host = raw.split(",")[0].strip().lower().split(":")[0]
    return host


@app.before_request
def redirect_apex_to_www():
    """Redirect redaccel.com to https://www.redaccel.com so one canonical host is used."""
    host = _request_host()
    if host != "redaccel.com":
        return None
    path = request.path or "/"
    qs = request.query_string
    url = f"https://www.redaccel.com{path}"
    if qs:
        url += "?" + qs.decode()
    return redirect(url, code=301)


def get_local_ip():
    """Get the local IP address for external access."""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


# ---------------------------------------------------------------------------
# The site is now the static GEO build in `site/`. Flask serves it directly so
# the existing Render service (gunicorn redaccel_app:app) needs no config
# changes. Old URLs from the previous template-based site 301 to their closest
# equivalents so inbound links and search equity carry over.
# ---------------------------------------------------------------------------

SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")

LEGACY_REDIRECTS = {
    "/blog/how-llms-are-changing-seo": "/geo-vs-seo/",
    "/blog/optimizing-for-ai-search": "/what-is-geo/",
    "/blog/reddit-traffic-potential": "/reddit-marketing-2026/",
    "/blog/reddit-psychology": "/reddit-marketing-2026/",
    "/blog/why-reddit-posts-rank-quickly": "/reddit-marketing-2026/",
    "/blog/case-study-90-days": "/about/",
    "/case-studies/gpm-music-group": "/about/",
    "/case-studies/creator-management-platform": "/about/",
}


def _serve_site_path(path: str):
    """Serve a file or directory index from the static site build in `site/`."""
    clean = (path or "").strip("/")
    if clean.startswith("functions"):
        abort(404)  # Cloudflare-only backend code; never serve it as content
    if not clean:
        return send_from_directory(SITE_DIR, "index.html")
    candidate = os.path.normpath(os.path.join(SITE_DIR, clean))
    if not candidate.startswith(SITE_DIR):
        abort(404)
    if os.path.isfile(candidate):
        return send_from_directory(SITE_DIR, clean)
    if os.path.isfile(os.path.join(candidate, "index.html")):
        if not (request.path or "").endswith("/"):
            return redirect(request.path + "/", code=301)
        return send_from_directory(SITE_DIR, clean + "/index.html")
    return send_from_directory(SITE_DIR, "404.html"), 404


@app.route("/")
def index():
    return _serve_site_path("")


@app.route("/<path:path>")
def site_page(path: str):
    target = LEGACY_REDIRECTS.get("/" + path.strip("/"))
    if target:
        return redirect(target, code=301)
    return _serve_site_path(path)


@app.route("/api/audit", methods=["POST"])
def audit_request():
    """Handle free AI visibility audit requests from the new site's form."""
    data = request.get_json(silent=True) or {}

    def clean(key: str) -> str:
        value = data.get(key)
        return value.strip()[:500] if isinstance(value, str) else ""

    brand = clean("brand")
    website = clean("website")
    category = clean("category")
    competitors = clean("competitors")
    email = clean("email")

    if not all([brand, website, category, competitors, email]) or "@" not in email:
        return jsonify({"error": "All fields are required"}), 400

    body = "\n".join([
        "New free AI visibility audit request",
        "",
        f"Brand:       {brand}",
        f"Website:     {website}",
        f"Category:    {category}",
        f"Competitors: {competitors}",
        f"Reply to:    {email}",
        "",
        "The 48-hour clock starts now.",
    ])
    ok, error = send_email(email, f"Audit request: {brand} ({category})", body)
    if not ok:
        # 503 makes the site's JS show the mailto fallback, so no lead is lost.
        return jsonify({"error": error or "Email delivery not configured"}), 503
    return jsonify({"ok": True})

def send_email(reply_to_email: str, subject: str, email_body: str):
    """Send email using SMTP."""
    try:
        # Get email configuration from environment (defaults to Hostinger SMTP)
        smtp_server = os.getenv('MAIL_SERVER', 'smtp.hostinger.com')
        smtp_port = int(os.getenv('MAIL_PORT', 465))
        smtp_username = os.getenv('MAIL_USERNAME', 'contact@redaccel.com')
        smtp_password = os.getenv('MAIL_PASSWORD', '')
        sender_email = os.getenv('MAIL_DEFAULT_SENDER', smtp_username or 'contact@redaccel.com')
        recipient_email = 'contact@redaccel.com'
        
        # Hostinger requires authentication
        if not smtp_username or not smtp_password:
            error_msg = "Email credentials not configured. Please set MAIL_USERNAME and MAIL_PASSWORD as environment variables (in .env file for local, or in Render dashboard for production)."
            print(f"Error: {error_msg}")
            return False, error_msg
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        if reply_to_email:
            msg['Reply-To'] = reply_to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        # Connect to server and send email
        if smtp_port == 465:
            # SSL connection
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # TLS connection
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        # Login if credentials are provided
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        return True, None
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending email: {error_msg}")
        return False, error_msg

def _fetch_calendly_details(event_uri: Optional[str], invitee_uri: Optional[str]):
    """
    Best-effort enrichment of meeting details (start/end time, etc.) from Calendly's API.
    Requires CALENDLY_API_TOKEN to be set in the environment.
    """
    token = os.getenv("CALENDLY_API_TOKEN", "").strip()
    if not token:
        return None

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    details = {
        "event_uri": event_uri,
        "invitee_uri": invitee_uri,
    }

    try:
        if invitee_uri:
            inv = requests.get(invitee_uri, headers=headers, timeout=12)
            inv.raise_for_status()
            invitee_resource = inv.json().get("resource", {})
            details["invitee_name"] = invitee_resource.get("name")
            details["invitee_email"] = invitee_resource.get("email")
            details["scheduled_event"] = invitee_resource.get("scheduled_event") or invitee_resource.get("event")
            # If Calendly has custom Q&A configured, it may show up here:
            details["questions_and_answers"] = invitee_resource.get("questions_and_answers")

            # Prefer the scheduled_event URI from the invitee response if present.
            if not event_uri and details.get("scheduled_event"):
                event_uri = details["scheduled_event"]
                details["event_uri"] = event_uri

        if event_uri:
            ev = requests.get(event_uri, headers=headers, timeout=12)
            ev.raise_for_status()
            event_resource = ev.json().get("resource", {})
            details["event_name"] = event_resource.get("name")
            details["start_time"] = event_resource.get("start_time")
            details["end_time"] = event_resource.get("end_time")
            details["status"] = event_resource.get("status")
            details["location"] = event_resource.get("location")

        return details
    except Exception as e:
        print(f"Calendly enrichment failed: {e}")
        return details


@app.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submission."""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        company = data.get('company', '').strip()
        message = data.get('message', '').strip()
        
        if not name or not email or not message:
            return jsonify({'success': False, 'error': 'Name, email, and message are required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
        
        subject = f'New Contact Form Submission from {name}'
        email_body = f"""New contact form submission from Redaccel website:

Name: {name}
Email: {email}
Company: {company if company else 'Not provided'}

Message:
{message}

---
This email was sent from the Redaccel contact form.
"""

        # Send email
        success, error = send_email(email, subject, email_body)
        
        if success:
            return jsonify({'success': True, 'message': 'Your inquiry has been sent to contact@redaccel.com. We\'ll get back to you soon!'})
        else:
            # Provide helpful error message
            error_message = 'Failed to send message. '
            if 'authentication' in error.lower() or 'login' in error.lower():
                error_message += 'Email server authentication failed. Please check your email configuration.'
            elif 'connection' in error.lower() or 'refused' in error.lower():
                error_message += 'Could not connect to email server. Please check your internet connection.'
            else:
                error_message += 'Please try again later or contact us directly at contact@redaccel.com'
            
            return jsonify({'success': False, 'error': error_message}), 500
        
    except Exception as e:
        print(f"Error in contact endpoint: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred. Please try again later.'}), 500


@app.route('/api/booking', methods=['POST'])
def booking():
    """
    Called from the Calendly embed after an invitee schedules a meeting.
    We email contact@redaccel.com with the lead intake + meeting details.
    """
    try:
        data = request.json or {}
        lead = data.get("lead") or {}
        calendly = data.get("calendly") or {}

        name = str(lead.get("name", "")).strip()
        email = str(lead.get("email", "")).strip()
        business = str(lead.get("business", "")).strip()
        goals = str(lead.get("goals", "")).strip()
        found_us = str(lead.get("found_us", "")).strip()
        page_url = str(data.get("page_url", "")).strip()

        event_uri = str(calendly.get("event_uri", "") or "").strip() or None
        invitee_uri = str(calendly.get("invitee_uri", "") or "").strip() or None

        if not name or not email or not business or not goals or not found_us:
            return jsonify({"success": False, "error": "Missing required lead fields"}), 400

        if '@' not in email or '.' not in email.split('@')[1]:
            return jsonify({"success": False, "error": "Please enter a valid email address"}), 400

        calendly_details = _fetch_calendly_details(event_uri=event_uri, invitee_uri=invitee_uri)

        subject = f"New meeting booking: {name} ({found_us})"

        lines = [
            "New meeting booking (via Redaccel website)",
            "",
            f"Name: {name}",
            f"Email: {email}",
            f"Business: {business}",
            f"Package / goals: {goals if goals else 'Not provided'}",
            f"How they found us: {found_us}",
        ]

        if page_url:
            lines.append(f"Page URL: {page_url}")

        lines += ["", "Calendly booking:"]

        if calendly_details and calendly_details.get("start_time"):
            lines.append(f"Start time: {calendly_details.get('start_time')}")
        if calendly_details and calendly_details.get("end_time"):
            lines.append(f"End time: {calendly_details.get('end_time')}")
        if calendly_details and calendly_details.get("event_name"):
            lines.append(f"Event name: {calendly_details.get('event_name')}")

        if event_uri:
            lines.append(f"Event URI: {event_uri}")
        if invitee_uri:
            lines.append(f"Invitee URI: {invitee_uri}")

        if calendly_details and calendly_details.get("questions_and_answers"):
            lines += ["", "Calendly questions & answers:"]
            for qa in calendly_details.get("questions_and_answers") or []:
                q = (qa.get("question") or "").strip()
                a = (qa.get("answer") or "").strip()
                if q or a:
                    lines.append(f"- {q}: {a}")

        if calendly_details is None:
            lines += [
                "",
                "Note: CALENDLY_API_TOKEN is not set, so meeting time may not be included above.",
                "You will still receive the booking in Calendly + your connected calendar as usual."
            ]

        email_body = "\n".join(lines) + "\n"

        success, error = send_email(email, subject, email_body)
        if success:
            return jsonify({"success": True})
        return jsonify({"success": False, "error": error or "Failed to send email"}), 500

    except Exception as e:
        print(f"Error in booking endpoint: {str(e)}")
        return jsonify({"success": False, "error": "An unexpected error occurred. Please try again later."}), 500

if __name__ == '__main__':
    import sys
    import atexit
    
    # Auto-start in background if requested
    if '--background' in sys.argv or '--bg' in sys.argv:
        import subprocess
        import os
        script_path = os.path.abspath(__file__)
        subprocess.Popen([sys.executable, script_path], 
                        stdout=open('redaccel_server.log', 'a'),
                        stderr=subprocess.STDOUT,
                        start_new_session=True)
        print("✅ Server starting in background...")
        print("📍 Access at: http://localhost:5002")
        print("📝 Logs: tail -f redaccel_server.log")
        sys.exit(0)
    
    local_ip = get_local_ip()
    print("\n" + "="*60)
    print("🚀 Redaccel Marketing Website - Server Starting")
    print("="*60)
    print("\n📍 Server running at:")
    print(f"   Local:  http://localhost:5002")
    print(f"   Network: http://{local_ip}:5002")
    print("\n📝 Open either URL in your browser to view the site")
    print("\n⚠️  Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")
    
    # Register cleanup function
    def cleanup():
        print("\n🛑 Server shutting down...")
    
    atexit.register(cleanup)
    
    # Use PORT from environment (for Render) or default to 5002
    port = int(os.getenv('PORT', 5002))
    # Disable debug mode in production (Render sets FLASK_ENV or similar)
    debug_mode = os.getenv('FLASK_ENV') == 'development' or os.getenv('DEBUG') == 'True'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)
