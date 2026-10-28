"""
Every page, redirect, 410 and form endpoint of redaccel.com, through Flask's test client.

Written 2026-10-28 after the free audit form returned HTTP 500 on every submission for
20 days without anyone noticing. If a test here fails, the push is refused (pre-push
hook on the mini, GitHub Actions for everything else) and Render does not deploy.
"""
import glob
import json
import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import pytest

import redaccel_app

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def _sitemap_paths():
    paths = []
    for f in sorted(glob.glob(os.path.join(SITE, "sitemap-*.xml"))):
        for loc in ET.parse(f).getroot().findall("sm:url/sm:loc", NS):
            paths.append(urlparse(loc.text.strip()).path or "/")
    return paths


def _index_paths():
    out = []
    for f in sorted(glob.glob(os.path.join(SITE, "**", "index.html"), recursive=True)):
        rel = os.path.relpath(os.path.dirname(f), SITE)
        if rel.startswith("functions"):
            continue
        out.append("/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/")
    return out


SITEMAP_PATHS = _sitemap_paths()
INDEX_PATHS = _index_paths()


def test_sitemaps_are_not_empty():
    assert len(SITEMAP_PATHS) >= 20, SITEMAP_PATHS


def test_sitemap_index_lists_every_sitemap(client):
    root = ET.parse(os.path.join(SITE, "sitemap.xml")).getroot()
    listed = {urlparse(l.text).path for l in root.findall("sm:sitemap/sm:loc", NS)}
    on_disk = {"/" + os.path.basename(f) for f in glob.glob(os.path.join(SITE, "sitemap-*.xml"))}
    assert listed == on_disk
    for path in listed:
        assert client.get(path).status_code == 200, path


@pytest.mark.parametrize("path", SITEMAP_PATHS)
def test_sitemap_page_is_200(client, path):
    r = client.get(path)
    assert r.status_code == 200, f"{path} -> {r.status_code}"
    assert b"</html>" in r.data.lower()


@pytest.mark.parametrize("path", INDEX_PATHS)
def test_every_built_page_is_200(client, path):
    r = client.get(path)
    assert r.status_code == 200, f"{path} -> {r.status_code}"


@pytest.mark.parametrize("path", [
    "/robots.txt", "/llms.txt", "/llms-full.txt", "/sitemap.xml", "/search-index.json",
    "/favicon.svg", "/apple-touch-icon.png", "/assets/js/main.js",
])
def test_root_files_are_200(client, path):
    assert client.get(path).status_code == 200, path


def test_local_assets_referenced_by_pages_exist(client):
    """Every /assets/ or /static/ file a page links to must serve, or the page breaks."""
    missing = set()
    for path in INDEX_PATHS:
        html = client.get(path).get_data(as_text=True)
        for ref in re.findall(r'(?:src|href)="(/(?:assets|static)/[^"?#]+)', html):
            if client.get(ref).status_code != 200:
                missing.add(f"{ref} (on {path})")
    assert not missing, sorted(missing)


def test_audit_page_has_working_form(client):
    html = client.get("/free-ai-visibility-audit/").get_data(as_text=True)
    assert 'data-endpoint="/api/audit"' in html
    for field in ("brand", "website", "category", "competitors", "email"):
        assert f'name="{field}"' in html, field
    js = client.get("/assets/js/main.js").get_data(as_text=True)
    assert "audit-form[data-endpoint]" in js and "fetch(" in js


def test_unknown_page_is_404(client):
    r = client.get("/this-page-does-not-exist/")
    assert r.status_code == 404
    assert b"</html>" in r.data.lower()


@pytest.mark.parametrize("path", ["/functions/api/audit.js", "/../redaccel_app.py", "/..%2fredaccel_app.py"])
def test_private_files_are_not_served(client, path):
    r = client.get(path)
    assert r.status_code in (400, 404), f"{path} -> {r.status_code}"
    assert b"import" not in r.data


def test_directory_without_slash_redirects(client):
    r = client.get("/pricing")
    assert r.status_code == 301
    assert r.headers["Location"].endswith("/pricing/")


def test_verification_files_are_served(client):
    for f in os.listdir(os.path.join(ROOT, "static", "verification")):
        if f.endswith(".html"):
            assert client.get("/" + f).status_code == 200, f


# ---------------------------------------------------------------------------
# Redirects and 410s
# ---------------------------------------------------------------------------

def test_apex_redirects_to_www_keeping_path_and_query(client):
    r = client.get("/pricing/?utm_source=chatgpt.com", headers={"Host": "redaccel.com"})
    assert r.status_code == 301
    assert r.headers["Location"] == "https://www.redaccel.com/pricing/?utm_source=chatgpt.com"


def test_apex_redirect_respects_forwarded_host(client):
    r = client.get("/", headers={"X-Forwarded-Host": "redaccel.com"})
    assert r.status_code == 301
    assert r.headers["Location"] == "https://www.redaccel.com/"


def test_onrender_host_is_not_redirected(client):
    assert client.get("/", headers={"Host": "redaccel-site.onrender.com"}).status_code == 200


@pytest.mark.parametrize("old,new", sorted(redaccel_app.LEGACY_REDIRECTS.items()))
def test_legacy_redirects(client, old, new):
    r = client.get(old)
    assert r.status_code == 301, old
    assert r.headers["Location"].endswith(new)
    assert client.get(new).status_code == 200, f"redirect target {new} is not 200"


GONE_PATHS = sorted(getattr(redaccel_app, "GONE_PATHS", ()))
GONE_PREFIXES = tuple(getattr(redaccel_app, "GONE_PREFIXES", ()))


@pytest.mark.parametrize("path", GONE_PATHS + [p + "/" for p in GONE_PATHS])
def test_gone_pages_are_410(client, path):
    r = client.get(path)
    assert r.status_code == 410, path
    assert r.headers.get("X-Robots-Tag") == "noindex"


def test_gone_prefixes_are_410(client):
    for prefix in GONE_PREFIXES:
        r = client.get(prefix + "anything.png")
        assert r.status_code == 410, prefix


@pytest.mark.skipif("/case-studies/gpm-music-group" not in GONE_PATHS, reason="no 410s in this version")
def test_gone_check_is_case_insensitive(client):
    assert client.get("/Case-Studies/GPM-Music-Group/").status_code == 410


# ---------------------------------------------------------------------------
# /api/audit (the free AI visibility audit form)
# ---------------------------------------------------------------------------

VALID = {
    "brand": "Pearle",
    "website": "pearle.com",
    "category": "Plant-based caviar",
    "competitors": "Caviar Co, Ossetra",
    "email": "ash@example.com",
}


def test_audit_valid_submission_sends_one_mail(client, smtp):
    r = client.post("/api/audit", json=VALID)
    assert r.status_code == 200, r.data
    assert r.get_json() == {"ok": True}
    assert len(smtp.sent) == 1
    mail = smtp.sent[0]
    assert mail["to"] == "contact@redaccel.com"
    assert "Subject: Audit request: Pearle (Plant-based caviar)" in mail["text"]
    assert "Reply-To: ash@example.com" in mail["text"]
    assert "https://pearle.com" in mail["text"]  # bare domain normalised


@pytest.mark.parametrize("website,expected", [
    ("pearle.com", "https://pearle.com"),
    ("https://www.Pearle.com/shop?x=1", "https://www.pearle.com/shop?x=1"),
    ("http://pearle.co.uk", "http://pearle.co.uk"),
    ("pearle.com:8080/", "https://pearle.com/"),
    ("not a domain", ""),
    ("pearle", ""),
    ("ftp://pearle.com", ""),
    ("", ""),
])
def test_normalise_website(website, expected):
    assert redaccel_app.normalise_website(website) == expected


@pytest.mark.parametrize("change", [
    {"brand": ""}, {"website": ""}, {"category": ""}, {"competitors": ""}, {"email": ""},
    {"email": "no-at-sign"}, {"website": "not a domain"}, {"website": "pearle"},
    {"brand": 123}, {"email": None},
])
def test_audit_invalid_submission_is_400_and_sends_nothing(client, smtp, change):
    r = client.post("/api/audit", json={**VALID, **change})
    assert r.status_code == 400, (change, r.data)
    assert "error" in r.get_json()
    assert smtp.sent == []


@pytest.mark.parametrize("kwargs", [
    {"data": "not json", "content_type": "text/plain"},
    {"data": "brand=x&email=y", "content_type": "application/x-www-form-urlencoded"},
    {"data": "{broken", "content_type": "application/json"},
    {"json": []},
    {},
])
def test_audit_bad_body_is_400_not_500(client, smtp, kwargs):
    r = client.post("/api/audit", **kwargs)
    assert r.status_code == 400, r.data
    assert smtp.sent == []


def test_audit_smtp_failure_is_503_so_the_page_shows_the_mailto_fallback(client, smtp):
    smtp.fail_with = OSError("connection refused")
    r = client.post("/api/audit", json=VALID)
    assert r.status_code == 503
    assert smtp.sent == []


def test_audit_missing_mail_password_is_503(client, smtp, monkeypatch):
    monkeypatch.setenv("MAIL_PASSWORD", "")
    r = client.post("/api/audit", json=VALID)
    assert r.status_code == 503


def test_audit_logs_the_submission_before_anything_else(client, smtp, capsys):
    client.post("/api/audit", json=VALID)
    out = capsys.readouterr().out
    line = next(l for l in out.splitlines() if l.startswith("AUDIT_SUBMISSION "))
    assert json.loads(line.split(" ", 1)[1])["email"] == "ash@example.com"


def test_audit_get_is_not_a_server_error(client):
    assert client.get("/api/audit").status_code in (404, 405)


def test_long_fields_are_cut_not_crashed(client, smtp):
    r = client.post("/api/audit", json={**VALID, "competitors": "x" * 10000})
    assert r.status_code == 200
    assert "x" * 501 not in smtp.sent[0]["text"]


# ---------------------------------------------------------------------------
# The monitoring probe path on /api/audit
# ---------------------------------------------------------------------------

SECRET = "probe-secret-for-tests"


@pytest.fixture
def probe_secret(monkeypatch):
    monkeypatch.setenv("PROBE_SECRET", SECRET)
    return SECRET


def test_probe_dry_runs_everything_but_sends_nothing(client, smtp, probe_secret, capsys):
    r = client.post("/api/audit", json=VALID, headers={"X-Redaccel-Probe": probe_secret})
    assert r.status_code == 200, r.data
    assert r.get_json() == {"ok": True, "probe": "dry"}
    assert smtp.sent == []
    assert "AUDIT_SUBMISSION" not in capsys.readouterr().out


def test_probe_dry_still_validates(client, smtp, probe_secret):
    r = client.post("/api/audit", json={**VALID, "website": "nope"},
                    headers={"X-Redaccel-Probe": probe_secret})
    assert r.status_code == 400


def test_probe_dry_reports_missing_mail_config(client, smtp, probe_secret, monkeypatch):
    monkeypatch.setenv("MAIL_PASSWORD", "")
    r = client.post("/api/audit", json=VALID, headers={"X-Redaccel-Probe": probe_secret})
    assert r.status_code == 503


def test_probe_send_marks_the_subject_test(client, smtp, probe_secret):
    r = client.post("/api/audit", json=VALID,
                    headers={"X-Redaccel-Probe": probe_secret, "X-Redaccel-Probe-Mode": "send"})
    assert r.status_code == 200
    assert len(smtp.sent) == 1
    assert "Subject: [TEST] Audit request: Pearle" in smtp.sent[0]["text"]
    assert smtp.sent[0]["to"] == "contact@redaccel.com"


@pytest.mark.parametrize("header", ["wrong", "", SECRET[:-1]])
def test_wrong_probe_secret_is_a_normal_submission(client, smtp, probe_secret, header):
    r = client.post("/api/audit", json=VALID, headers={"X-Redaccel-Probe": header})
    assert r.get_json() == {"ok": True}
    assert len(smtp.sent) == 1
    assert "[TEST]" not in smtp.sent[0]["text"]


def test_probe_is_off_when_no_secret_is_configured(client, smtp, monkeypatch):
    monkeypatch.delenv("PROBE_SECRET", raising=False)
    r = client.post("/api/audit", json=VALID, headers={"X-Redaccel-Probe": ""})
    assert r.get_json() == {"ok": True}
    assert len(smtp.sent) == 1


# ---------------------------------------------------------------------------
# /api/contact and /api/booking (older endpoints, no page posts to them today)
# ---------------------------------------------------------------------------

CONTACT = {"name": "Ash", "email": "ash@example.com", "company": "Pearle", "message": "Hi"}


def test_contact_valid(client, smtp):
    r = client.post("/api/contact", json=CONTACT)
    assert r.status_code == 200 and r.get_json()["success"] is True
    assert len(smtp.sent) == 1


@pytest.mark.parametrize("change", [{"name": ""}, {"email": ""}, {"message": ""}, {"email": "ash@nodot"}])
def test_contact_invalid_is_400(client, smtp, change):
    r = client.post("/api/contact", json={**CONTACT, **change})
    assert r.status_code == 400
    assert smtp.sent == []


def test_contact_smtp_failure_is_handled(client, smtp):
    smtp.fail_with = OSError("Connection refused")
    r = client.post("/api/contact", json=CONTACT)
    assert r.status_code == 500 and r.get_json()["success"] is False


BOOKING = {
    "lead": {"name": "Ash", "email": "ash@example.com", "business": "Pearle",
             "goals": "AI search", "found_us": "ChatGPT"},
    "calendly": {"event_uri": "https://api.calendly.com/scheduled_events/X",
                 "invitee_uri": "https://api.calendly.com/scheduled_events/X/invitees/Y"},
    "page_url": "https://www.redaccel.com/",
}


def test_booking_valid_without_calendly_token(client, smtp):
    r = client.post("/api/booking", json=BOOKING)
    assert r.status_code == 200 and r.get_json()["success"] is True
    assert "CALENDLY_API_TOKEN is not set" in smtp.sent[0]["text"]


def test_booking_enriches_from_calendly_when_token_set(client, smtp, monkeypatch):
    monkeypatch.setenv("CALENDLY_API_TOKEN", "t")

    class Resp:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return {"resource": self.payload}

    def fake_get(url, headers=None, timeout=None):
        if "invitees" in url:
            return Resp({"name": "Ash", "email": "ash@example.com", "questions_and_answers": [
                {"question": "Site", "answer": "pearle.com"}]})
        return Resp({"name": "30 min", "start_time": "2026-10-29T13:00:00Z", "end_time": "2026-10-29T13:30:00Z"})

    monkeypatch.setattr(redaccel_app.requests, "get", fake_get)
    r = client.post("/api/booking", json=BOOKING)
    assert r.status_code == 200
    text = smtp.sent[0]["text"]
    assert "Start time: 2026-10-29T13:00:00Z" in text and "- Site: pearle.com" in text


def test_booking_survives_calendly_outage(client, smtp, monkeypatch):
    monkeypatch.setenv("CALENDLY_API_TOKEN", "t")

    def boom(*a, **kw):
        raise OSError("calendly down")

    monkeypatch.setattr(redaccel_app.requests, "get", boom)
    r = client.post("/api/booking", json=BOOKING)
    assert r.status_code == 200
    assert len(smtp.sent) == 1


@pytest.mark.parametrize("field", ["name", "email", "business", "goals", "found_us"])
def test_booking_missing_field_is_400(client, smtp, field):
    body = json.loads(json.dumps(BOOKING))
    body["lead"][field] = ""
    r = client.post("/api/booking", json=body)
    assert r.status_code == 400
    assert smtp.sent == []
