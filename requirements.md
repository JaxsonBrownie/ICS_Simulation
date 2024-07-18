## HMI 1
- read solar panel power meter- Holding Register 20 (40021)
- read the current power input - Coil 10 (00011)

## PLC 1 & 2
Address space:
- Coil 10 (00011) - solar (ON) mains (OFF)
- Holding Register 20 (40021) - solar panel power meter (Float)

## Serial Port
`sudo socat -d pty,raw,echo=0,link=/dev/ttyS10 pty,raw,echo=0,link=/dev/ttyS11`