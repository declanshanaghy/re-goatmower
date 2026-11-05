"""Tests for tools/eco_passwd.py pure function eco_passwd()."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from eco_passwd import eco_passwd, MAGIC


def test_sha256sum_mode_known_vector():
    """sha256sum mode returns the DEF CON 32 reference implementation output."""
    pw = eco_passwd("AI_px30", "TEST1234567")
    assert pw == "YTQ1ODMx"


def test_raw_mode_known_vector():
    """raw digest mode produces a different (shorter-encoded) base64 prefix."""
    pw = eco_passwd("AI_px30", "TEST1234567", digest_mode="raw")
    assert pw == "pFgxUKkN"


def test_truncate_zero_returns_full_base64():
    """truncate=0 returns the full base64 string, not just 8 chars."""
    pw = eco_passwd("AI_px30", "TEST1234567", truncate=0)
    assert pw == (
        "YTQ1ODMxNTBhOTBkNjhlNGMzYzQzOGNjOGNjNzdkMmMxMzNiZjE2ZWY1YWM0"
        "MjI3MmZjZDkyM2YwNGU0M2JhYiAgLQo="
    )


def test_different_model_and_serial():
    """Different model/serial yields a different password (no hash collision)."""
    pw1 = eco_passwd("AI_px30", "TEST1234567")
    pw2 = eco_passwd("GOAT_A3000", "SN20250001")
    assert pw2 == "YjE2M2Fk"
    assert pw1 != pw2


def test_invalid_digest_mode_raises():
    """An unrecognised digest_mode raises ValueError."""
    with pytest.raises(ValueError, match="digest_mode"):
        eco_passwd("AI_px30", "TEST1234567", digest_mode="md5")


def test_custom_magic_changes_output():
    """Changing the MAGIC constant produces a different password."""
    pw_default = eco_passwd("AI_px30", "TEST1234567")
    pw_custom = eco_passwd("AI_px30", "TEST1234567", magic="00:11:22:33:44:55")
    assert pw_default != pw_custom


def test_password_length_default():
    """Default truncation returns exactly 8 characters."""
    pw = eco_passwd("AI_px30", "TEST1234567")
    assert len(pw) == 8
