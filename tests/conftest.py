"""
Shared fixtures for the site tests.

Every test runs with the network cut off: SMTP, Calendly and any other outbound call
must be stubbed by the test itself, so nothing here can ever send a real mail.
"""
import os
import socket
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Known values before the app module reads its environment.
os.environ.pop("PROBE_SECRET", None)
os.environ.update({
    "MAIL_SERVER": "smtp.test.invalid",
    "MAIL_PORT": "465",
    "MAIL_USERNAME": "contact@redaccel.com",
    "MAIL_PASSWORD": "test-password",
    "MAIL_DEFAULT_SENDER": "contact@redaccel.com",
    "CALENDLY_API_TOKEN": "",
})

import redaccel_app  # noqa: E402  (import errors in the app fail every test here)

HOST = "www.redaccel.com"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise RuntimeError("tests must not open network connections")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture
def app():
    redaccel_app.app.config.update(TESTING=False, PROPAGATE_EXCEPTIONS=False)
    return redaccel_app.app


@pytest.fixture
def client(app):
    c = app.test_client()
    c.environ_base["HTTP_HOST"] = HOST
    return c


class FakeSMTP:
    """Stands in for smtplib.SMTP_SSL / SMTP and records what would have been sent."""
    sent = []
    fail_with = None

    def __init__(self, server, port, *a, **kw):
        self.server, self.port = server, port

    def starttls(self):
        pass

    def login(self, user, password):
        if FakeSMTP.fail_with:
            raise FakeSMTP.fail_with

    def sendmail(self, sender, recipient, text):
        FakeSMTP.sent.append({"from": sender, "to": recipient, "text": text})

    def quit(self):
        pass


@pytest.fixture
def smtp(monkeypatch):
    FakeSMTP.sent = []
    FakeSMTP.fail_with = None
    monkeypatch.setattr(redaccel_app.smtplib, "SMTP_SSL", FakeSMTP)
    monkeypatch.setattr(redaccel_app.smtplib, "SMTP", FakeSMTP)
    return FakeSMTP
