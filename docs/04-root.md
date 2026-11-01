# Root

## eco_passwd
- Serial (20-char, off device label): _TODO_
- Calculator result (builder.dontvacuum.me/ecopassword.php): _TODO_
- Local tools/eco_passwd.py result: _TODO_ — must match calculator.
- MAGIC = `d4:3d:7e:fa:12:5d:C8:02:8F:0A:E2:F5` (CONFIRMED, DEF CON 32 p75 / HITCON 2024 p74).
- Formula: `base64(sha256({model}+MAGIC+{sn}+"\n"))`. `tools/eco_passwd.py --all` prints all
  digest/truncation variants — run with your `{model}` (from /etc/fw.manifest) and serial,
  then pick the one that matches the reference calculator or the device's real password.

## Shell
- Method (UART login / U-Boot init override): _TODO_
- `id` output confirming uid 0: _TODO_

## Persistence (low brick risk)
- Script dropped at /data/autostart/*.sh starting dropbear/telnetd. **Do not repack RO rootfs.**
