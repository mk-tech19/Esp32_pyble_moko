# Test UART sync (non-destructive)
- [ ] TX ESP32 GPIO17 → PA10 STM32.
- [ ] RX ESP32 GPIO16 ← PA9 STM32.
- [ ] GND disatukan; jangan masukkan 5 V ke GPIO ESP32.
- [ ] BOOT0 HIGH lalu reset target.
- [ ] Uji sync melalui REPL dengan `STM32ROM().sync()` hanya jika aman.
- [ ] Jika timeout/NACK, jangan mencoba erase; periksa wiring, parity, boot mode, dan chip.
