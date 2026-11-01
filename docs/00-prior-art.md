# Prior art & references

Annotated sources for rooting / reverse-engineering the Ecovacs GOAT A3000. The
Ecovacs-specific research below matters far more than any generic firmware-RE tutorial.

## Primary source: Dennis Giese & braelynn (dontvacuum.me)

Five years of Ecovacs reverse-engineering. Three talks cover the method:

- DEF CON 32 (2024): `dontvacuum.me/talks/DEFCON32/DEFCON32_reveng_hacking_ecovacs_robots.pdf`
- HITCON CMT 2024: `dontvacuum.me/talks/HITCON2024/HITCON-CMT-2024_Ecovacs.pdf`
- 37C3 (2023): `dontvacuum.me/talks/37c3-2023/37c3-vacuuming-and-mowing.pdf`

> Access note (2026-10-31): the live MIT-hosted site refused connections from the
> automation environment, and WebFetch is blocked from web.archive.org. A Wayback
> snapshot of the DEF CON 32 deck exists:
> `web.archive.org/web/20261019060636/https://dontvacuum.me/talks/DEFCON32/DEFCON32_reveng_hacking_ecovacs_robots.pdf`
> Open in a browser and transcribe A3000-relevant slides here.

### eco_passwd (deterministic root password)
- Per-unit, re-applied on every boot via `busybox chpasswd`.
- Online calculator: `builder.dontvacuum.me/ecopassword.php` — device-type selector
  **already lists GOAT models** (X1/X2/T20/T30/9x0/Airbot/Z1...). Enter the serial.
- Formula shape (varies by model/firmware — 37C3 vs HITCON differ):
  `base64( sha256_hex(product + MAGIC + serial + "\n") + "  -\n" )[:8]`
  - `product` from `/etc/fw.manifest`; `MAGIC` is a fixed string in the slides.
  - 37C3 slide-79 formula does NOT reproduce passwords on some newer models.
- **Action:** read serial off device → calculator = fast path; port algorithm into
  `tools/eco_passwd.py` and verify against calculator output.

### CVE-2024-52331 — OTA firmware deterministic key
- Ecovacs devices decrypt OTA firmware with a deterministic symmetric key derived from
  device/model identifiers → lets you decrypt downloaded firmware offline (non-invasive).
- Public exploit code; no vendor patch at time of research.

### Other known issue classes to validate on A3000
- Anti-theft PIN stored in cleartext on the filesystem.
- `:8888` GoAhead service, runs as root on all interfaces, default credential.

## Closest worked example: DEEBOT T8 AIVI (Rockchip PX30)

`github.com/Alpha162/deebot-t8-aivi-px30-notes` — a sibling device with a full,
concrete recipe. Key facts (confirm each against the A3000; do not assume identical):

- **Debug header:** 8-pin JST PHDR-08VS under a rubber plug near the lidar; carries
  UART + 3V3 + SWD. Micro-USB in same bay = Rockchip USB download path.
  Header may be rotated 180° on some units — check GND vs micro-USB shell first.
- **UART:** 3.3 V ONLY (never 5 V). 115200 8N1; U-Boot may run at 1500000.
  Board ID `evb_px30`. `bootdelay=0` → spam Ctrl-C from power-on for U-Boot.
- **eco_passwd here:** `product=AI_px30`, uses last 8 chars of serial, base64 of the
  hex text (differs from 37C3).
- **Flash (GPT, 512-byte LBAs):** uboot 0x4000 / trust 0x6000 / mx 0x8000 (calib,
  do not touch) / my 0xa000 (calib) / sys 0xc000 (serial at 1 MiB) / boot1 0xd000
  (Android boot img) / rootfs1 0x10000 (RO squashfs — eco_passwd lives here) /
  boot2 0x33000 / rootfs2 0x36000 / data 0x59000 (RW ext4).
- **Dump:** RO via `rkdeveloptool`/rockusb (IDB mode only below LBA 0x10000; above
  returns 0xCC filler). Full read/write via U-Boot `ums 0 rknand 0` (USB mass storage).
- **Persistence (low brick risk):** `/etc/rc.d/autostart.sh` runs every
  `/data/autostart/*.sh` as root at boot, AFTER eco_passwd. Drop a script there to
  start dropbear/telnetd + set a known pw. Avoid repacking RO squashfs (main brick risk).
- **Architecture:** medusa/ROS; `mdsctl <element> '<json>'` is the command CLI;
  `roscore` + `/usr/bin/deebot`.
- **Local control achieved:** camera (`/dev/video0`, rkisp1, 1280x960 YUYV; static
  aarch64 MJPEG streamer). Driving NOT solved — RemoteMove via mdsctl accepted by
  wifihandler but wheels don't actuate.

## Supporting sources
- `github.com/itsjfx/ecovacs-hacking` (x1_omni.md): 20-char serial, UART 115200, pw usage.
- `robotinfo.dev`: GOAT G1 root = UART / "easy"; warns "do not OTA-update if you plan
  to root." Baseline for A3000 expectations.
- `privacysmarthome.com` Valetudo rooting guide + Home Assistant `ecovacs` integration:
  cloud-decoupling / local-control patterns to aim for.
- `github.com/Janverhu/ecovacs-goat-g1`, `github.com/it00x32/ecovacs-goat-g1-ha`:
  cloud-based GOAT integrations (not rooting, but protocol insight).

## Generic method reference
- YouTube "Low Level" — *Reverse Engineering Proves What We Suspected All Along..*
  (`youtube.com/watch?v=7h7FYGF7tuQ`). Generic embedded workflow: console/flash dump →
  binwalk → Ghidra. Transcript not yet captured (mirrors bot-gated). TODO: transcribe
  any extra tool tips here.

## A3000-specific unknowns (fill in during execution)
- [ ] SoC (PX30? RK-series? other) — from FCC internal photos.
- [ ] Flash type (eMMC / NAND / SPI-NOR) and size.
- [ ] Debug-header location/pinout on the A3000 board.
- [ ] Serial length & which eco_passwd variant applies.
- [ ] FCC ID (search FCC OET for "Ecovacs" / the model).
