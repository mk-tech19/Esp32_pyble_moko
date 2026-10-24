# Optional active buzzer. Set pin only after checking the actual wiring.
def beep(pin_number=25, duration_ms=120):
    try:
        from machine import Pin
        import time
        p = Pin(pin_number, Pin.OUT)
        p.on()
        time.sleep_ms(duration_ms)
        p.off()
    except Exception as exc:
        print("Buzzer nonaktif:", exc)
