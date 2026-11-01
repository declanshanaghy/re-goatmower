# Flash layout & dump provenance

## Dumps (record SHA-256 of every raw image)
| File | Source method | Date | SHA-256 |
|------|---------------|------|---------|
| _TODO flash dump_ | rkdeveloptool / ums / chip-off | | |

### Reference docs downloaded (slides, not flash dumps)
| File (dumps/dontvacuum/) | SHA-256 |
|---|---|
| DEFCON32_ecovacs.pdf | 08d266d432d2b62c1ee3da8b6ea48ff297c77f386216a8f06f843e0350fb6e1d |
| HITCON2024.pdf | 0d9c2aa0d2f031b4073d13a434be818a29a534595c984dc40adba85515434d54 |
| 37c3_mowing.pdf | 12645db9ac2290089c943014b0c9f16d80f82f55034fbbe5cad9f1e84f129fb9 |

## Partition table
Capture the GPT here. PX30 cousin layout (confirm, don't assume):
uboot 0x4000 · trust 0x6000 · mx/my (calib, DO NOT TOUCH) · sys (serial) ·
boot1 · rootfs1 (RO squashfs) · boot2 · rootfs2 · data (RW ext4).
