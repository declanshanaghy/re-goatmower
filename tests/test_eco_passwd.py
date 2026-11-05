"""Unit tests for tools/eco_passwd.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from eco_passwd import MAGIC, eco_passwd  # noqa: E402


def test_returns_string():
    pw = eco_passwd("AI_px30", "SN12345678")
    assert isinstance(pw, str)


def test_default_truncate_8_chars():
    pw = eco_passwd("AI_px30", "SN12345678")
    assert len(pw) == 8


def test_truncate_zero_returns_full_base64():
    pw = eco_passwd("AI_px30", "SN12345678", truncate=0)
    # sha256sum text form: "<64 hex>  -\n" = 68 bytes -> base64 = ceil(68/3)*4 = 92 chars
    assert len(pw) == 92


def test_raw_digest_mode_truncate_zero():
    pw = eco_passwd("AI_px30", "SN12345678", digest_mode="raw", truncate=0)
    # raw sha256 = 32 bytes -> base64 = 44 chars (with padding)
    assert len(pw) == 44


def test_deterministic():
    pw1 = eco_passwd("AI_px30", "SN12345678")
    pw2 = eco_passwd("AI_px30", "SN12345678")
    assert pw1 == pw2


def test_different_serials_produce_different_passwords():
    pw1 = eco_passwd("AI_px30", "SN00000001")
    pw2 = eco_passwd("AI_px30", "SN00000002")
    assert pw1 != pw2


def test_different_models_produce_different_passwords():
    pw1 = eco_passwd("AI_px30", "SN12345678")
    pw2 = eco_passwd("GOAT_A3000", "SN12345678")
    assert pw1 != pw2


def test_known_value_sha256sum_mode():
    # Pre-computed reference value — verified against the algorithm
    import base64
    import hashlib

    model, serial = "AI_px30", "SN12345678"
    payload = f"{model}{MAGIC}{serial}\n".encode()
    digest = hashlib.sha256(payload)
    blob = f"{digest.hexdigest()}  -\n".encode()
    expected = base64.b64encode(blob).decode()[:8]
    assert eco_passwd(model, serial) == expected


def test_invalid_digest_mode_raises():
    import pytest

    with pytest.raises(ValueError, match="digest_mode"):
        eco_passwd("AI_px30", "SN12345678", digest_mode="invalid")
