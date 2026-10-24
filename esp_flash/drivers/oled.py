# Optional placeholder. Install ssd1306.py separately if using SSD1306.
# Example wiring from project notes: SDA=GPIO21, SCL=GPIO22.
def show_status(message):
    try:
        from machine import Pin, I2C
        import ssd1306
        i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
        display = ssd1306.SSD1306_I2C(128, 64, i2c)
        display.fill(0)
        display.text("STM32 Flasher", 0, 0)
        display.text(str(message)[:21], 0, 18)
        display.show()
    except Exception as exc:
        print("OLED nonaktif:", exc)
