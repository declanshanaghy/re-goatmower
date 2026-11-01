# Existing open-source firmware / tooling survey (2026-10-31)

Question: is there a ready-made A3000 firmware dump or decompiled source to start from?
**Answer: no.** No extracted image, rootfs, or source for the GOAT A3000 (Horizon
Sunrise 5) exists publicly. robotinfo.dev's device index lists only the **Goat G1** among
mowers — the A3000 is not tracked yet — and all Ecovacs firmware is marked **encrypted**.

## What does NOT exist
- No A3000 firmware image, rootfs dump, or decompiled source anywhere (GitHub or else).
- No one has published a decrypted Ecovacs mower rootfs; images are AES-encrypted
  (CVE-2024-52331 key needed even for an OTA download).

## What DOES exist (and what it actually is)
| Project | Stars | What it gives | Relation to firmware |
|---|---|---|---|
| **robotinfo.dev** (Giese) | — | Firmware **version tracking** (MD5/size) + **filesystem diffs** between versions | Metadata only; images not hosted; Goat **G1** listed, not A3000 |
| **itsjfx/ecovacs-hacking** | ~24 | Toolkit: `bin/uart`, `capture-mitm`, `patch-rootfs`, `repack_rootfs.txt`, dropbear, MQTT broker, `valetudo.md`, `cloud-reversing.md`, `x1_omni.md` | Method + scripts; a few rootfs files (dropbear) — from **vacuums**, not A3000 |
| **Alpha162/deebot-t8-aivi-px30-notes** | — | Full worked root example (T8 AIVI = `ecovacs.x5d34r`, PX30) | Notes, not an image |
| **bumper** | ~400 | Self-hosted **Ecovacs cloud server** reimplementation | Clean-room, cloud side — NOT from firmware |
| DeebotUniverse/client.py, mrbungle64/ecovacs-deebot.js, wpietri/sucks | 130–290 | Ecovacs **cloud protocol** clients | Interop; no firmware |
| Valetudo | — | Cloud-free robot control | **Does not support Ecovacs mowers** |

## Consequence for this project
- You **cannot skip the device** — there is no A3000 dump to start from; you'd be the first.
- Two legitimate "start now" shortcuts that need no firmware:
  1. **Local control via the cloud protocol today** — `bumper` + the deebot client libs
     already speak Ecovacs' cloud/MQTT. Good for decoupling/automation before any root.
  2. **Grab + decrypt the A3000 OTA yourself** (Phase 1) using the CVE-2024-52331 key —
     yields a filesystem to analyze without opening the mower.
- The **Goat G1** userland is the closest analog (same medusa/ROS stack, same `eco_passwd`,
  same `/data/autostart`) even though its SoC differs (RK3588 vs Sunrise 5) — useful for
  knowing what the A3000 rootfs will look like once dumped.
