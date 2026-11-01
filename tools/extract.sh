#!/usr/bin/env bash
# Carve an Ecovacs firmware / flash image. Usage: tools/extract.sh <image> [outdir]
set -euo pipefail
img="${1:?usage: extract.sh <image> [outdir]}"
out="${2:-${img%.*}_extracted}"
mkdir -p "$out"
echo "[*] sha256: $(shasum -a 256 "$img")"
echo "[*] binwalk -> $out"
binwalk --run-as=root -eM --directory "$out" "$img" || binwalk -eM -C "$out" "$img"
echo "[*] look for squashfs/ubi/ext images under $out, then:"
echo "    unsquashfs -d <dir> <rootfs.squashfs>    # RO rootfs"
echo "    file <img> ; 7z l <img>                   # inspect carved parts"
