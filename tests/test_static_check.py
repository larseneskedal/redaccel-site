"""
Static check: undefined names, syntax errors and broken imports in every .py file.

This is the check that would have caught 39dfcb8 (re used without being imported) before
it ever reached redaccel.com. Ruff's E9/F63/F7/F82 are the "this crashes at runtime"
rules; style warnings are deliberately not included.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ruff():
    exe = os.path.join(os.path.dirname(sys.executable), "ruff")
    return exe if os.path.exists(exe) else shutil.which("ruff")


def test_no_undefined_names_or_syntax_errors():
    ruff = _ruff()
    assert ruff, "ruff is not installed (pip install -r requirements-dev.txt)"
    out = subprocess.run(
        [ruff, "check", "--no-cache", "--select", "E9,F63,F7,F82", "--output-format", "concise",
         "--exclude", ".venv,venv,node_modules", ROOT],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr


def test_app_imports_cleanly():
    out = subprocess.run([sys.executable, "-c", "import redaccel_app"], cwd=ROOT,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
