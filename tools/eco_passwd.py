#!/usr/bin/env python3
"""Ecovacs eco_passwd root-password calculator.

Derives the per-unit UART root password. The device computes this at every boot via
an obfuscated "eco_passwd" program and applies it with `busybox chpasswd`.

Source: Dennis Giese & braelynn, DEF CON 32 (2024), slide 75:
    base64( sha256( {model} + MAGIC + {sn} + "\n" ) )
    MAGIC = "d4:3d:7e:fa:12:5d:C8:02:8F:0A:E2:F5"
Reference tool: https://builder.dontvacuum.me/ecopassword.php

The slide notation `base64(sha256(...))` is ambiguous about whether the base64 is of
the raw 32-byte digest or of the textual `sha256sum` output. The device-verified
DEEBOT T8 AIVI (PX30) notes use the *textual* form -- i.e. the device effectively does:
    printf '%s%s%s\n' MODEL MAGIC SN | sha256sum        # -> "<64 hex>  -\n"
    printf '%s' "<64 hex>  -\n"       | base64           # -> base64 text
    password = <that base64>[:8]
So this script defaults to --digest-mode sha256sum and --truncate 8. If that does not
match your device / the reference calculator, try --digest-mode raw and/or --truncate 0.

ALWAYS verify the output against the reference calculator or the device before trusting.
`model` here is the firmware model/product string from /etc/fw.manifest (e.g. on PX30 it
is "AI_px30"); pass yours with --model. Serial comes from the device label / sys partition.
"""
import argparse
import base64
import hashlib

MAGIC = "d4:3d:7e:fa:12:5d:C8:02:8F:0A:E2:F5"  # DEF CON 32 slide 75


def eco_passwd(model: str, serial: str, magic: str = MAGIC,
               digest_mode: str = "sha256sum", truncate: int = 8) -> str:
    payload = f"{model}{magic}{serial}\n".encode()
    digest = hashlib.sha256(payload)
    if digest_mode == "sha256sum":
        # emulate the `sha256sum` CLI on stdin: "<hex>  -\n", then base64 that text
        blob = f"{digest.hexdigest()}  -\n".encode()
    elif digest_mode == "raw":
        blob = digest.digest()
    else:
        raise ValueError("digest_mode must be 'sha256sum' or 'raw'")
    pw = base64.b64encode(blob).decode()
    return pw[:truncate] if truncate else pw


def main() -> None:
    ap = argparse.ArgumentParser(description="Ecovacs eco_passwd root-password calculator")
    ap.add_argument("--serial", required=True, help="device serial (from label / sys partition)")
    ap.add_argument("--model", required=True,
                    help="firmware model/product string from /etc/fw.manifest (e.g. AI_px30)")
    ap.add_argument("--magic", default=MAGIC, help="MAGIC constant (default = DEF CON 32 value)")
    ap.add_argument("--digest-mode", choices=["sha256sum", "raw"], default="sha256sum",
                    help="how the digest is fed to base64 (default: sha256sum text form)")
    ap.add_argument("--truncate", type=int, default=8,
                    help="keep first N chars of the base64 (0 = full). Default 8.")
    ap.add_argument("--all", action="store_true",
                    help="print all variant combinations to compare against the reference tool")
    args = ap.parse_args()

    if args.all:
        for dm in ("sha256sum", "raw"):
            for tr in (8, 0):
                pw = eco_passwd(args.model, args.serial, args.magic, dm, tr)
                print(f"digest={dm:9s} truncate={tr or 'full':4} -> {pw}")
        return
    print(eco_passwd(args.model, args.serial, args.magic, args.digest_mode, args.truncate))


if __name__ == "__main__":
    main()
