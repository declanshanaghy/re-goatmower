# UART console

- Adapter: 3.3 V USB-UART. **Never 5 V.**
- Settings: start 115200 8N1 (use logic analyzer to auto-detect; U-Boot may be 1500000).
- `bootdelay=0` expected → spam Ctrl-C from power-on to catch U-Boot.

## Boot log
Paste full capture (U-Boot env, kernel cmdline, init) below / attach a file.

## U-Boot environment
`printenv` output, boot sequence, partition mapping.
