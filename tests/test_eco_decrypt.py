"""Round-trip tests for tools/eco_decrypt.py (CVE-2024-52331 OTA decryptor).

Builds synthetic AES-128-CBC-encrypted OTA images with the same deterministic
key/IV derivation the device uses (per github.com/denysvitali/ecovacs-firmware-tools),
then decrypts them with the tool and asserts byte equality.
"""
import base64
import hashlib
import json
import struct
import sys
import os

import pytest
from Crypto.Cipher import AES

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import eco_decrypt  # noqa: E402


def pad(data: bytes) -> bytes:
    n = 16 - len(data) % 16
    return data + bytes([n]) * n


def build_section(section_type: int, plaintext: bytes, model: str = "px30") -> bytes:
    """Encrypt one section exactly like the device/updater does."""
    key, iv = eco_decrypt.derive_key_iv(section_type, len(pad(plaintext)), model)
    ct = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(plaintext))
    header = struct.pack("<BBHI", 1, 1, section_type << 12, len(ct))
    checksum = hashlib.sha256(header + ct).hexdigest().encode()
    return header + ct + checksum


def build_image(sections, model="px30"):
    return b"".join(build_section(t, pt, model) for t, pt in sections)


def test_derivation_golden_vector():
    # Independently computed with the Go reference algorithm
    # (github.com/denysvitali/ecovacs-firmware-tools, pkg/decrypt/decrypt.go)
    key, iv = eco_decrypt.derive_key_iv(1, 32, "px30")
    assert key == b"eaa0e74269698c13"
    assert iv == b"a0a8cf54c397ae4f"
    assert len(key) == 16 and len(iv) == 16


def test_derivation_depends_on_type_and_size():
    k1, _ = eco_decrypt.derive_key_iv(1, 32)
    k2, _ = eco_decrypt.derive_key_iv(2, 32)
    k3, _ = eco_decrypt.derive_key_iv(1, 48)
    assert len({k1, k2, k3}) == 3


def test_find_sections_and_roundtrip():
    manifest = json.dumps({
        "fw_ver": "1.4.9", "hw_ver": "0", "product": "T9AF_px30",
        "release_date": "2021-07-23",
        "sections": [
            {"name": "pre_upgrade_script", "type": "sh_script", "size": 256},
            {"name": "normal_boot", "type": "bin", "size": 4096},
            {"name": "normal_fs", "type": "fs", "size": 1048576},
        ],
    }).encode()
    script = b"#!/bin/sh\necho pre-upgrade\n" * 4
    boot = bytes(range(256)) * 4
    plaintexts = [manifest, script, boot]
    image = build_image([(1, manifest), (2, script), (3, boot)])

    sections = eco_decrypt.find_sections(image)
    assert len(sections) == 3
    assert [s.section_type for s in sections] == [1, 2, 3]
    assert all(s.unkn1 == 1 and s.type == 1 for s in sections)

    for i, (sec, pt) in enumerate(zip(sections, plaintexts)):
        key, iv = eco_decrypt.derive_key_iv(sec.section_type, sec.size)
        out, pad_ok = eco_decrypt.pkcs7_unpad(
            eco_decrypt.decrypt_section(image[sec.data_offset:sec.data_offset + sec.size], key, iv))
        assert pad_ok
        assert out == pt  # byte equality with the original plaintext


def test_find_sections_skips_garbage_prefix():
    manifest = b'{"fw_ver": "1.0"}'
    image = b"\x00" * 33 + build_image([(1, manifest)])
    sections = eco_decrypt.find_sections(image)
    assert len(sections) == 1
    key, iv = eco_decrypt.derive_key_iv(sections[0].section_type, sections[0].size)
    out, ok = eco_decrypt.pkcs7_unpad(
        eco_decrypt.decrypt_section(image[sections[0].data_offset:sections[0].data_offset + sections[0].size], key, iv))
    assert ok and out == manifest


def test_pkcs7_unpad_rejects_bad_padding():
    assert eco_decrypt.pkcs7_unpad(b"\x01" * 15 + b"\x02")[1] is False
    assert eco_decrypt.pkcs7_unpad(b"\x10" * 16)[1] is True  # full-block pad


def test_entropy_and_printable():
    import os as _os
    rnd = _os.urandom(4096)
    txt = b"#!/bin/sh\n" * 400
    assert eco_decrypt.entropy(rnd) > 7.0
    assert eco_decrypt.entropy(txt) < eco_decrypt.entropy(rnd)
    assert eco_decrypt.printable_ratio(txt) > 0.9


def run_cli(tmp_path, args):
    image = tmp_path / "fw.bin"
    manifest = json.dumps({
        "fw_ver": "1.4.9", "product": "T9AF_px30", "release_date": "2021-07-23",
        "sections": [{"name": "pre_upgrade_script", "type": "sh_script", "size": 256}],
    }).encode()
    script = b"#!/bin/sh\nid\n" * 8
    image.write_bytes(build_image([(1, manifest), (2, script)]))
    old = sys.argv[:]
    sys.argv = ["eco_decrypt.py"] + [str(image)] + args
    try:
        eco_decrypt.main()
    finally:
        sys.argv = old


def test_cli_list_and_verify(tmp_path, capsys):
    run_cli(tmp_path, ["--list"])
    out = capsys.readouterr().out
    assert "found 2 section(s)" in out
    run_cli(tmp_path, ["--verify"])
    out = capsys.readouterr().out
    assert "all sections verified" in out


def test_cli_verify_fails_on_corrupt(tmp_path):
    image = tmp_path / "fw.bin"
    manifest = b'{"fw_ver": "1.0"}'
    img = bytearray(build_image([(1, manifest)]))
    img[9] ^= 0xFF  # corrupt one ciphertext byte
    image.write_bytes(bytes(img))
    old = sys.argv[:]
    sys.argv = ["eco_decrypt.py", str(image), "--verify"]
    try:
        with pytest.raises(SystemExit):
            eco_decrypt.main()
    finally:
        sys.argv = old


def test_cli_decrypt_to_files(tmp_path, capsys):
    manifest = json.dumps({
        "fw_ver": "1.4.9", "product": "T9AF_px30", "release_date": "2021-07-23",
        "sections": [{"name": "pre_upgrade_script", "type": "sh_script", "size": 256}],
    }).encode()
    script = b"#!/bin/sh\necho hi\n" * 8
    img = tmp_path / "fw.bin"
    img.write_bytes(build_image([(1, manifest), (2, script)]))
    outdir = tmp_path / "out"

    old = sys.argv[:]
    sys.argv = ["eco_decrypt.py", str(img), "-o", str(outdir)]
    try:
        eco_decrypt.main()
    finally:
        sys.argv = old

    manifest_out = json.loads((outdir / "manifest.json").read_text())
    assert manifest_out["fw_ver"] == "1.4.9"
    assert (outdir / "pre_upgrade_script.sh").read_bytes() == script