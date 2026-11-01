#!/usr/bin/env python3
"""Ecovacs eco_passwd root-password calculator.

Derives the per-unit root password from the device serial + per-model constants.
The exact input string varies by model/firmware (37C3 vs HITCON 2024 vs PX30 notes
all differ), so this exposes the knobs. ALWAYS verify output against the reference
calculator at builder.dontvacuum.me/ecopassword.php before trusting it.

Known PX30 (DEEBOT T8 AIVI) variant:
    product = "AI_px30", serial_slice = last 8 chars, hex-text base64.

Usage:
    python3 eco_passwd.py --serial <SERIAL> [--product AI_px30] [--serial-slice 8]
"""
import argparse
import base64
import hashlib

# From the dontvacuum.me slides. Fill in once read from the deck (see docs/00-prior-art.md).
MAGIC = ""  # TODO: fixed string from slides; leave "" and verify against calculator.


def eco_passwd(serial: str, product: str, magic: str, serial_slice: int | None) -> str:
    s = serial[-serial_slice:] if serial_slice else serial
    payload = f"{product}{magic}{s}\n".encode()
    hex_text = hashlib.sha256(payload).hexdigest()
    # Device does the equivalent of: printf '%s  -\n' "<sha256 hex>" | base64
    blob = f"{hex_text}  -\n".encode()
    return base64.b64encode(blob).decode()[:8]


def main() -> None:
    ap = argparse.ArgumentParser(description="Ecovacs eco_passwd calculator")
    ap.add_argument("--serial", required=True, help="device serial (from label / sys partition)")
    ap.add_argument("--product", default="AI_px30", help="product string from /etc/fw.manifest")
    ap.add_argument("--magic", default=MAGIC, help="fixed MAGIC string from the slides")
    ap.add_argument("--serial-slice", type=int, default=8,
                    help="use last N chars of serial (0 = full serial)")
    args = ap.parse_args()
    if not args.magic:
        print("WARNING: MAGIC is empty — output will NOT match the real password. "
              "Fill MAGIC from the slides (docs/00-prior-art.md).")
    sl = args.serial_slice or None
    print(eco_passwd(args.serial, args.product, args.magic, sl))


if __name__ == "__main__":
    main()
