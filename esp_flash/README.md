# ESP32 → STM32 Blue Pill Flasher (MicroPython)

**Status: prototype / not hardware-validated.** Use only with a sacrificial STM32F103 board and a recoverable test image.

## Structure
```
esp32_stm32_flasher/
├── main.py
├── config.py
├── apps/
│   ├── __init__.py
│   └── stm32_flasher.py
├── protocol/
│   ├── __init__.py
│   └── stm32_rom.py
├── web/
│   ├── __init__.py
│   └── page.py
├── drivers/
│   ├── __init__.py
│   ├── oled.py
│   └── buzzer.py
└── tests/
    ├── test_http_upload.md
    ├── test_uart_sync.md
    └── test_flash_matrix.md
```

## Install
1. Back up files already on the ESP32. Do not overwrite an existing `main.py` on a device used for another project.
2. Copy the folder contents to the ESP32 filesystem using Thonny. Keep the folders and `__init__.py` files.
3. Edit `config.py`: set a unique Wi-Fi password of at least 8 characters.
4. Initially leave `ENABLE_DESTRUCTIVE_FLASH = False`. This allows the web UI and UART sync test, but refuses erase/write.
5. Connect ESP32 GPIO17 (TX) -> STM32 PA10 (USART1_RX), ESP32 GPIO16 (RX) <- STM32 PA9 (USART1_TX), and GND -> GND. Do not connect 5 V to ESP32 GPIO.
6. Set STM32 BOOT0 HIGH and reset/power-cycle it for ROM bootloader mode.
7. In Thonny REPL run:
   ```python
   from apps.stm32_flasher import run
   run()
   ```
8. Join the phone to the ESP32 AP and open `http://192.168.4.1/`.
9. First test the page and UART sync only. A successful sync is not proof of correct erase/write compatibility.

## Before enabling erase/write
- Verify the exact target and its ROM bootloader command set against ST AN2606 and AN3155.
- Confirm actual flash size, image link address, erase behavior and write granularity for the specific chip.
- Test recovery using ST-Link/SWD or a known-good programmer.
- This prototype deliberately has no read-back verification. The browser will report that limitation.
- HTTP is unencrypted; use only a trusted, isolated local Wi-Fi connection.
