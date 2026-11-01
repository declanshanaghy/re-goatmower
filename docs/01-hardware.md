# Hardware map — GOAT A3000

Fill from FCC internal photos first (no disassembly), then confirm on teardown.

## Identification
- Manufacturer model code: **MR2507D** (per Coolblue listing) — use to match the FCC filing.
- Variants exist: "A3000 LiDAR" and "A3000 LiDAR PRO" — FCC ID may differ; check which you have.
- FCC ID: _TODO — read off the label in the battery bay / underside; then look up on fccid.io
  (grantee lookup; fccid.io 403s automated fetches, so browse it manually). Internal photos in
  the test-report exhibits give SoC/flash/debug-header without opening the case._
- SoC: _TODO_ — Goat G1 proxy = **Rockchip RK3588**; expect Rockchip-class.
- RAM / flash (type + size): _TODO_ — Goat G1 = 4 GB DDR4 + **16 GB eMMC**.
  ⚠️ If eMMC, the CH341A/SPI clip CANNOT read main flash — use `rkdeveloptool`/maskrom
  or U-Boot `ums`; chip-off needs an eMMC reader, not the SPI programmer.
- Lidar / sensors of interest: _TODO_

## Debug interfaces
- UART header location: _TODO_  (PX30 cousin: 8-pin JST near lidar, under rubber plug)
- Pinout: _TODO_ — debug port is UART + 3.3V + SWD + USB, "similar for all models since 2019" (HITCON p38). 3.3 V ONLY; verify GND first; some units 180° rotated.
- USB download path (Rockchip maskrom): _TODO_

## Teardown photos
Store here or link; annotate pads/headers.
