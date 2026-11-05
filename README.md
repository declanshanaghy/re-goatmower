# re-goatmower

Reverse-engineering the firmware of an **Ecovacs GOAT A3000 LiDAR** robot mower —
analysis of my own hardware, for interoperability (local control, decoupling from the
Ecovacs cloud) and security research.

## Quickstart

**Requirements:** Python 3.8+, git

```bash
git clone https://github.com/declanshanaghy/re-goatmower.git
cd re-goatmower
```

Calculate the UART root password for your device (model string from `/etc/fw.manifest`,
serial from the device label):

```bash
python3 tools/eco_passwd.py --model AI_px30 --serial YOUR_SERIAL_HERE
```

Pass `--all` to print every digest/truncation variant for comparison against the
[reference calculator](https://builder.dontvacuum.me/ecopassword.php):

```bash
python3 tools/eco_passwd.py --model AI_px30 --serial YOUR_SERIAL_HERE --all
```

To carve a flash image once you have a dump (requires `binwalk`):

```bash
tools/extract.sh dumps/flash.img
```

Start reading the lab notebook at `docs/00-prior-art.md`.

## Why

The A3000 is a 2025 model with no public teardown. Sibling Ecovacs devices (GOAT G1,
DEEBOT T8 AIVI on Rockchip) are already root-able over UART using Dennis Giese's
research. This project applies that proven methodology to an undocumented target and
documents what it finds.

## Goals

1. Root + a persistent shell, then local control independent of the Ecovacs cloud.
2. Validate the known Ecovacs weakness classes on this specific model and disclose
   anything new responsibly to Ecovacs.

## How it's organised

- `docs/` — the lab notebook. Start at `docs/00-prior-art.md`; the numbered files
  track each phase (hardware → UART → flash → root → analysis → local control).
- `tools/` — `eco_passwd.py` (root-password calculator) and `extract.sh` (firmware carving).
- `dumps/` — raw flash images (gitignored; large and unit-specific). Hashes go in `docs/03`.
- `findings/` — vulnerability write-ups prepared for coordinated disclosure.

The approach, phase plan, and verification criteria live in the approved plan:
`~/.claude/plans/make-a-plan-for-quirky-mitten.md`.

## Legal / ethics

This is my own device. Work is for interoperability and security research — lawful
activity. Vulnerabilities are handled via coordinated disclosure to Ecovacs. Note:
**do not OTA-update the mower once rooting is intended** — updates patch these holes.
