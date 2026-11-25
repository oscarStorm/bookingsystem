"""Repo-hygiene seam: secrets live only in env vars, so `.env` must be
gitignored and must never be tracked — this is what keeps DATABASE_URL,
RESEND_API_KEY, SECRET_KEY and SEED_ADMIN_PASSWORD out of git history.
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_env_file_is_gitignored():
    result = subprocess.run(
        ["git", "check-ignore", "-v", ".env"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, ".env must be gitignored so secrets never reach git"


def test_env_file_is_not_tracked():
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", ".env"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, ".env must not be tracked in git"


def test_env_example_is_tracked():
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", ".env.example"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, ".env.example must be committed as the template"
