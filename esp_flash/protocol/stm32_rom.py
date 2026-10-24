from machine import UART, Pin
import time
import config


class BootloaderError(Exception):
    pass


class STM32ROM:
    """Minimal STM32 USART ROM bootloader client. Hardware/ROM behavior must be validated."""

    def __init__(self):
        self.uart = UART(
            config.UART_ID,
            baudrate=config.UART_BAUD,
            bits=8,
            parity=0,       # MicroPython ESP32: parity=0 is commonly even parity; verify build.
            stop=1,
            tx=Pin(config.UART_TX_PIN),
            rx=Pin(config.UART_RX_PIN),
            timeout=config.UART_TIMEOUT_MS,
        )

    def drain(self):
        while self.uart.any():
            self.uart.read()

    def read_byte(self, label="response"):
        deadline = time.ticks_add(time.ticks_ms(), config.UART_TIMEOUT_MS)
        while time.ticks_diff(deadline, time.ticks_ms()) > 0:
            data = self.uart.read(1)
            if data:
                value = data[0]
                if value == config.ACK:
                    return value
                if value == config.NACK:
                    raise BootloaderError("%s: NACK (0x1F)" % label)
                raise BootloaderError("%s: respons tak dikenal 0x%02X" % (label, value))
            time.sleep_ms(5)
        raise BootloaderError("%s: timeout menunggu STM32" % label)

    def ack(self, label):
        return self.read_byte(label)

    def sync(self):
        self.drain()
        self.uart.write(b"\x7F")
        self.ack("sinkronisasi 0x7F")
        return "ACK sinkronisasi diterima"

    def command(self, cmd, label):
        self.uart.write(bytes((cmd, cmd ^ 0xFF)))
        self.ack(label)

    def get_commands(self):
        # Get command: 00 FF, ACK, N, bootloader version, N supported commands, command list, ACK.
        self.command(0x00, "Get command")
        n_data = self.uart.read(1)
        if not n_data:
            raise BootloaderError("Get: panjang respons timeout")
        n = n_data[0]
        payload = self._read_exact(n + 1, "Get payload")
        self.ack("Get akhir")
        return payload  # version byte followed by supported command bytes

    def _read_exact(self, n, label):
        out = bytearray()
        deadline = time.ticks_add(time.ticks_ms(), config.UART_TIMEOUT_MS)
        while len(out) < n and time.ticks_diff(deadline, time.ticks_ms()) > 0:
            part = self.uart.read(n - len(out))
            if part:
                out.extend(part)
            else:
                time.sleep_ms(3)
        if len(out) != n:
            raise BootloaderError("%s: data tidak lengkap (%d/%d)" % (label, len(out), n))
        return bytes(out)

    def erase_legacy(self):
        # Destructive; only call after target command support is confirmed.
        self.command(0x43, "Erase Memory command")
        self.uart.write(b"\xFF\x00")  # legacy global erase selector
        self.ack("Global erase")

    def write_block(self, address, data):
        if not data or len(data) > 256:
            raise BootloaderError("Panjang blok harus 1..256 byte")
        # Address packet: 4-byte big-endian + XOR.
        addr = bytes(((address >> 24) & 255, (address >> 16) & 255,
                      (address >> 8) & 255, address & 255))
        self.command(0x31, "Write Memory command")
        self.uart.write(addr + bytes((addr[0] ^ addr[1] ^ addr[2] ^ addr[3],)))
        self.ack("Alamat Write Memory")
        # N = length - 1; checksum XORs N and all data bytes.
        n = len(data) - 1
        checksum = n
        for b in data:
            checksum ^= b
        self.uart.write(bytes((n,)) + data + bytes((checksum,)))
        self.ack("Data Write Memory")

    def close(self):
        try:
            self.uart.deinit()
        except Exception:
            pass
