# Firmware analysis

- Extraction: `tools/extract.sh <image>` (binwalk + unsquashfs).
- Targets in Ghidra: deebot, mdsctl, wifihandler, GoAhead (:8888).
- Findings log below.

## OTA/firmware decryption (CVE-2024-52331) — Phase 1 target
Firmware is AES-128-CBC encrypted, NOT signed. Key+IV derived from a format string
(DEF CON 32 p76, RE'd with tihmstar):
    fmt  = "vX2Z3X3RhcmdldCA%s1jdSAt%sbyBtYW4%dy5iaW4%s%x825xx%s"
    args = ("ECO-PT", model, section_type, "", section_len, "jeff-hk@126.com")
Transcribe the exact format string from the slide image before coding a decryptor
(text extraction may be imperfect). See docs/00-prior-art.md for full context.
