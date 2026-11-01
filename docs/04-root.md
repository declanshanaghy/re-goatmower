# Root

## eco_passwd
- Serial (20-char, off device label): _TODO_
- Calculator result (builder.dontvacuum.me/ecopassword.php): _TODO_
- Local tools/eco_passwd.py result: _TODO_ — must match calculator.
- Confirmed product string / MAGIC / serial-slice variant: _TODO_

## Shell
- Method (UART login / U-Boot init override): _TODO_
- `id` output confirming uid 0: _TODO_

## Persistence (low brick risk)
- Script dropped at /data/autostart/*.sh starting dropbear/telnetd. **Do not repack RO rootfs.**
