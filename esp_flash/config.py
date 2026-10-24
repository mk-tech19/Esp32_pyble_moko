# Edit these settings before running.
AP_SSID = "STM32-Flasher"
AP_PASSWORD = "GANTI_PASSWORD_MINIMAL_8"

UART_ID = 2
UART_TX_PIN = 17
UART_RX_PIN = 16
UART_BAUD = 115200
UART_TIMEOUT_MS = 1200

FLASH_BASE = 0x08000000
# Conservative limit for nominal 64 KiB C8 targets; verify the actual chip.
MAX_IMAGE_SIZE = 64 * 1024
BLOCK_SIZE = 256

ACK = 0x79
NACK = 0x1F

# SAFETY LOCK: remains False until target ROM/erase behavior has been verified.
# Do not enable merely because UART sync returns ACK.
ENABLE_DESTRUCTIVE_FLASH = False

# OLED/buzzer are optional and disabled by default.
OLED_ENABLED = False
BUZZER_ENABLED = False
