# Flash layout & dump provenance

## Dumps (record SHA-256 of every raw image)
| File | Source method | Date | SHA-256 |
|------|---------------|------|---------|
| _TODO_ | rkdeveloptool / ums / chip-off | | |

## Partition table
Capture the GPT here. PX30 cousin layout (confirm, don't assume):
uboot 0x4000 · trust 0x6000 · mx/my (calib, DO NOT TOUCH) · sys (serial) ·
boot1 · rootfs1 (RO squashfs) · boot2 · rootfs2 · data (RW ext4).
