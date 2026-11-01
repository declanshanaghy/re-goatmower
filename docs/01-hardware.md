# Hardware map — GOAT A3000

Identified from the FCC internal-photos exhibits (no disassembly needed):
`dumps/fcc/2A64BMR2507C/Internal-Photos.pdf` (the A3000 host) and
`dumps/fcc/2A64BGPL11/Internal-Photos-8211184.pdf` (a GOAT radio board).
Grab others with the trick that beats Cloudflare: append `.pdf` to the fccid.io
exhibit URL and curl with a browser UA (the index pages 403, the direct PDF does not).

## Identification
- **FCC ID: 2A64B-MR2507C** · IC: 28593-MR2507C (the A3000 host device).
- Label (GPL11 radio unit): "ECOVACS GOAT", Lawn Mowing Robot, 21V 4.3A charge, 15 kg,
  Ø22 cm, Class 1 Laser, IPX6, Bluetooth, MADE IN CHINA 07/24. Model field redacted.
- Main compute board silkscreen: **`MR2337_X5_C8_V1.0_20240814`**.

## Main board (MR2337_X5) — the brain
| Ref | Part (as marked) | Role |
|-----|------------------|------|
| **U1** | **"Sunrise-5" = Horizon Robotics Sunrise 5 (旭日5 / X5)** BGA | **Main SoC** (AI vision; ARM + BPU). Board suffix `_X5` confirms. |
| U2 | **CXMT** `CXD...` (CXDB5CCBM-class) | LPDDR DRAM |
| U3 | **BIWIN `8WCMA0011G16G`** (marked "NAND") | **Main flash** (managed NAND / eMMC-class) |
| U4 | ~48-pin QFP MCU (by camera connectors) | sensor/IO co-MCU (GD32-class likely) |
| — | "MsC H1551CG 250RE" SOIC-20 (x2) | motor/driver support |
| — | Realtek **RTL8733BS** + **Fn-Link** module | Wi-Fi + BT combo (seen on GPL11 radio board; module present here too) |
| J7 / J5 / J9 | silk **TOF / 鱼眼 (fisheye) / 全景 (panorama)** | camera FPC connectors |

Right edge carries dense castellated pad arrays + white JST headers (board-to-board /
expansion / likely debug). A second board `CORHO-1646K_V1.5` carries the Wi-Fi/BT module,
a blue USB-type connector and power/signal JSTs.

## ⚠️ Implications vs. the Goat G1 (which is Rockchip RK3588)
- The A3000 SoC is **Horizon Sunrise 5, NOT Rockchip** → Rockchip tooling
  (`rkdeveloptool`, U-Boot `ums 0 rknand 0`) does **not** apply. Expect Horizon's own
  boot ROM / USB-download + U-Boot. Good news: Giese rooted a **Horizon X3**-based
  Ecovacs vacuum via **UART** at 37c3, and `eco_passwd` is OS-level (SoC-independent),
  so the UART-root path still holds.
- Flash is **BIWIN managed NAND/eMMC**, not SPI-NOR → the **CH341A/SPI clip cannot read
  it**. Non-destructive dump = Horizon USB-download / U-Boot console; chip-off would need
  an eMMC/NAND reader, not the SPI programmer.

## Debug interfaces — TO LOCATE on teardown
- Expected (Giese, "similar for all models since 2019"): a header with **UART + 3.3V +
  SWD + USB**. Candidates: the right-edge castellated pads / white JSTs on MR2337_X5, or a
  header on the CORHO-1646K board. Use the logic analyzer to find TX; **3.3 V only**;
  verify GND first; some units are 180° rotated.
- Capture into `docs/02-uart-console.md`.

## Still needed from the physical unit
- [ ] 20-char serial (label) + firmware `model` string (`/etc/fw.manifest`) for eco_passwd.
- [ ] Which physical header is the UART/debug console.
