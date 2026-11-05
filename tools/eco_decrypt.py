#!/usr/bin/env python3
"""Ecovacs OTA firmware decryptor (CVE-2024-52331).

OTA firmware images are AES-128-CBC encrypted but NOT signed; the per-section
key/IV are deterministically derived from a format string built from the
model, section type and section length (Dennis Giese & braelynn, DEF CON 32,
slide 76; format string RE'd with tihmstar). Reference implementation:
github.com/denysvitali/ecovacs-firmware-tools (MIT, Go).

Derivation (per the Go reference, pkg/decrypt/decrypt.go):
    s       = TEMPLATE % (model, section_type, "%x" % section_len)
    blob    = base64(s)[4:]            # skip 4 chars
    blob    = blob[:len(s)]             # truncate back to original length
    digest  = sha256(blob).hexdigest()  # 64 ASCII hex chars
    IV      = digest[0:16]  (ASCII)
    KEY     = digest[35:51] (ASCII)

NOTE on the slide transcription (docs/00-prior-art.md:108-115): the slide
template `vX2Z3X3RhcmdldCA%s1jdSAt%sbyBtYW4%dy5iaW4%s%x825xx%s` with args
("ECO-PT", model, section_type, "", section_len, "jeff-hk@126.com") does not
round-trip against the Go tool: the working Go source uses the prefix
"ZWNvX2Z3X3RhcmdldCA" (note the leading "ZWNv", lost in the OCR), a literal
"ECO-PT", and derives KEY/IV from the *hex text* of the digest -- slicing raw
digest bytes at [35:51] is impossible (SHA-256 is only 32 bytes). This tool
follows the Go source of truth.

Image layout (per the Go reference): a sequence of sections, each
    [8-byte header][size bytes ciphertext][64-byte ASCII sha256 checksum]
header = u8 unkn1 (must be 1), u8 type (must be 1), u16 LE unkn2
(section_type = unkn2 >> 12), u32 LE size. Sections may be zero-padded apart.

Usage:
    tools/eco_decrypt.py --list image.bin            # inspect section table
    tools/eco_decrypt.py --verify image.bin           # decrypt in memory, sanity-check
    tools/eco_decrypt.py image.bin -o outdir          # decrypt sections to files
"""
import argparse
import base64
import hashlib
import json
import math
import os
import struct
import sys

from Crypto.Cipher import AES

# Go: "ZWNvX2Z3X3RhcmdldCAECO-PT1jdSAtpx30byBtYW4%dy5iaW4%s825xxjeff-hk@126.com"
# ("px30" = model placeholder; %d = section_type; %s = "%x" % section_len)
TEMPLATE = "ZWNvX2Z3X3RhcmdldCAECO-PT1jdSAt{model}byBtYW4{stype:d}y5iaW4{size:x}825xxjeff-hk@126.com"

SECTION_TYPES = {
    1: "manifest", 2: "pre_upgrade_script", 3: "normal_boot",
    4: "normal_fs", 5: "mcu", 6: "post_upgrade_script",
}


def derive_key_iv(section_type: int, section_size: int, model: str = "px30"):
    """Derive the AES-128-CBC key + IV for one section (Go reference semantics)."""
    s = TEMPLATE.format(model=model, stype=section_type, size=section_size)
    encoded = base64.b64encode(s.encode()).decode("ascii")
    encoded_skipped = encoded[4:]
    if len(encoded_skipped) > len(s):
        encoded_skipped = encoded_skipped[: len(s)]
    digest = hashlib.sha256(encoded_skipped.encode()).hexdigest()
    if len(digest) < 51:
        raise ValueError("hash too short for key/IV extraction")
    return digest[35:51].encode("ascii"), digest[0:16].encode("ascii")  # key, iv


def pkcs7_unpad(data: bytes):
    """Strip PKCS#7 padding. Returns (unpadded, padding_valid)."""
    if not data or len(data) % 16:
        return data, False
    pad = data[-1]
    if pad < 1 or pad > 16 or pad > len(data):
        return data, False
    if data[-pad:] != bytes([pad]) * pad:
        return data, False
    return data[:-pad], True


def entropy(data: bytes) -> float:
    """Shannon entropy in bits/byte (0..8)."""
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    total = len(data)
    return -sum((c / total) * math.log2(c / total) for c in counts if c)


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    return sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13)) / len(data)


class Section:
    offset: int
    unkn1: int
    type: int
    unkn2: int
    size: int
    data_offset: int
    checksum_offset: int
    checksum: str
    __slots__ = ("offset", "unkn1", "type", "unkn2", "size", "data_offset", "checksum_offset", "checksum")

    def __init__(self, offset, header):
        self.offset = offset
        self.unkn1 = header[0]
        self.type = header[1]
        self.unkn2 = struct.unpack("<H", header[2:4])[0]
        self.size = struct.unpack("<I", header[4:8])[0]
        self.data_offset = offset + 8
        self.checksum_offset = self.data_offset + self.size
        self.checksum = ""

    @property
    def section_type(self):
        return self.unkn2 >> 12

    @property
    def total_size(self):
        return 8 + self.size + 64

    def type_name(self):
        return SECTION_TYPES.get(self.section_type, "type_%d" % self.section_type)


def find_sections(data: bytes):
    """Scan an OTA image for section headers (Go reference heuristics)."""
    sections = []
    offset = 0
    n = len(data)
    while offset < n - 72:
        if offset + 8 > n:
            break
        sec = Section(offset, data[offset:offset + 8])
        if sec.size <= 0 or offset + sec.total_size > n:
            offset += 1
            continue
        if sec.unkn1 != 1 or sec.type != 1:
            offset += 1
            continue
        sec.checksum = data[sec.checksum_offset:sec.checksum_offset + 64].decode("ascii", errors="replace")
        sections.append(sec)
        offset += sec.total_size
        while offset < n and data[offset] == 0:
            offset += 1
    return sections


def decrypt_section(ct: bytes, key: bytes, iv: bytes):
    """AES-128-CBC decrypt (no unpadding)."""
    if len(ct) % 16:
        raise ValueError("ciphertext is not a multiple of the block size")
    return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)





EXTENSIONS = {"sh_script": ".sh", "bin": ".bin", "fs": ".img", "img": ".img"}


def section_filename(manifest, index):
    """Output filename for a section, using manifest names when available."""
    if index == 0:
        return "manifest.json"
    if manifest and 0 < index <= len(manifest.get("sections", [])):
        ms = manifest["sections"][index - 1]
        return ms.get("name", "section_%d" % index) + EXTENSIONS.get(ms.get("type", ""), ".bin")
    return "section_%d.bin" % index


def load_manifest(sections, data, model):
    """Decrypt section 0 in memory and parse it as the JSON manifest."""
    sec = sections[0]
    ct = data[sec.data_offset:sec.data_offset + sec.size]
    key, iv = derive_key_iv(sec.section_type, sec.size, model)
    manifest, ok = pkcs7_unpad(decrypt_section(ct, key, iv))
    if not ok:
        return None
    try:
        return json.loads(manifest.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Ecovacs OTA firmware decryptor (CVE-2024-52331, AES-128-CBC)")
    ap.add_argument("image", help="OTA firmware image file")
    ap.add_argument("--model", default="px30",
                    help="firmware model/platform string fed to the key template (default: px30)")
    ap.add_argument("--list", action="store_true", help="list the section table and exit")
    ap.add_argument("--verify", action="store_true",
                    help="decrypt in memory and sanity-check (padding, entropy, checksums)")
    ap.add_argument("-o", "--outdir", default=None,
                    help="output directory for decrypted sections (default: <image>_decrypted)")
    args = ap.parse_args()

    with open(args.image, "rb") as f:
        data = f.read()
    print(f"[i] loaded firmware: {args.image} ({len(data)} bytes)")

    sections = find_sections(data)
    if not sections:
        sys.exit("[!] no sections found -- wrong file, or wrong --model/type heuristic")
    print(f"[i] found {len(sections)} section(s)")

    hdr = f"{'#':>2} {'type':>6} {'name':<20} {'size':>10} {'offset':>10} {'checksum'}"
    print(hdr)
    for i, s in enumerate(sections):
        print(f"{i:>2} {s.section_type:>6} {s.type_name():<20} {s.size:>10} {s.offset:>10} {(s.checksum or '')[:16]}...")

    if args.list:
        return

    manifest = load_manifest(sections, data, args.model)
    if manifest:
        print(f"[i] manifest: {manifest.get('product', '?')} {manifest.get('fw_ver', '?')} "
              f"({manifest.get('release_date', '?')})")

    failures = 0
    outdir = args.outdir or "{}_decrypted".format(os.path.splitext(args.image)[0])
    if not args.verify:
        os.makedirs(outdir, exist_ok=True)

    for i, sec in enumerate(sections):
        ct = data[sec.data_offset:sec.data_offset + sec.size]
        try:
            key, iv = derive_key_iv(sec.section_type, sec.size, args.model)
            pt, pad_ok = pkcs7_unpad(decrypt_section(ct, key, iv))
        except ValueError as e:
            print(f"[!] section {i}: derive/decrypt failed: {e}")
            failures += 1
            continue

        cks_ok = bool(sec.checksum) and (
            hashlib.sha256(data[sec.offset:sec.checksum_offset]).hexdigest() == sec.checksum)
        name = section_filename(manifest, i)
        ec, ep = entropy(ct), entropy(pt)
        pr = printable_ratio(pt)

        if args.verify:
            status = "OK" if pad_ok else "BAD"
            print(f"[v] section {i} ({name}): size={sec.size} pad={status} "
                  f"entropy {ec:.2f}->{ep:.2f} printable={pr:.0%} checksum={'ok' if cks_ok else 'MISMATCH'}")
            if not pad_ok or not cks_ok:
                failures += 1
        else:
            out = os.path.join(outdir, name)
            payload = (json.dumps(manifest, indent=2) + "\n").encode() if i == 0 and manifest else pt
            with open(out, "wb") as f:
                f.write(payload)
            print(f"[+] section {i} -> {out} ({len(pt)} bytes, pad={'ok' if pad_ok else 'BAD'})")

    if failures:
        sys.exit(f"[!] {failures} section(s) failed verification")
    if args.verify:
        print("[v] all sections verified")


if __name__ == "__main__":
    main()