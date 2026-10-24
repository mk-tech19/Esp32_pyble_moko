import network
import socket
import time
import gc
import config
from protocol.stm32_rom import STM32ROM, BootloaderError
from web.page import HTML

_busy = False


def _send(conn, code, message, content_type="text/plain; charset=utf-8"):
    body = message.encode() if isinstance(message, str) else message
    reason = "OK" if code == 200 else "Bad Request" if code == 400 else "Conflict" if code == 409 else "Internal Server Error"
    head = ("HTTP/1.1 %d %s\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n" %
            (code, reason, content_type, len(body))).encode()
    conn.send(head)
    conn.send(body)


def _read_headers(conn):
    buf = bytearray()
    marker = b"\r\n\r\n"
    while marker not in buf:
        part = conn.recv(512)
        if not part:
            raise ValueError("Header HTTP tidak lengkap")
        buf.extend(part)
        if len(buf) > 4096:
            raise ValueError("Header HTTP terlalu besar")
    i = buf.find(marker)
    lines = bytes(buf[:i]).decode().split("\r\n")
    request = lines[0].split()
    if len(request) < 2:
        raise ValueError("Baris request tidak valid")
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return request[0].upper(), request[1], headers, bytes(buf[i + 4:])


def _recv_exactly(conn, first, expected, callback):
    received = 0
    if first:
        take = min(len(first), expected)
        callback(first[:take])
        received += take
    while received < expected:
        part = conn.recv(min(512, expected - received))
        if not part:
            raise OSError("Koneksi putus saat upload (%d/%d byte)" % (received, expected))
        callback(part)
        received += len(part)
    return received


def _flash_stream(conn, headers, first_body):
    global _busy
    if "content-length" not in headers:
        raise ValueError("Content-Length wajib ada")
    try:
        size = int(headers["content-length"])
    except Exception:
        raise ValueError("Content-Length tidak valid")
    if size <= 0:
        raise ValueError("File kosong ditolak")
    if size > config.MAX_IMAGE_SIZE:
        raise ValueError("File terlalu besar untuk batas konfigurasi")
    if not config.ENABLE_DESTRUCTIVE_FLASH:
        raise PermissionError("Safety lock aktif: ENABLE_DESTRUCTIVE_FLASH=False. Upload tidak diprogram.")

    # Do not erase until target sync and Get command probe have succeeded.
    rom = STM32ROM()
    pending = bytearray()
    written = 0
    try:
        rom.sync()
        supported = rom.get_commands()
        commands = supported[1:] if len(supported) > 1 else b""
        if 0x43 not in commands:
            raise BootloaderError("ROM tidak melaporkan command Erase Memory 0x43; berhenti sebelum erase")
        _send(conn, 200, "Target sinkron. Command erase terdeteksi; mulai erase lalu tulis.\\n",
              "text/plain; charset=utf-8")
        # Response is sent before body consumed; browser may close upload depending on implementation.
        # Therefore this prototype intentionally blocks real flashing until a reviewed transport
        # implementation is installed. Prevent accidental use of an unvalidated streaming sequence.
        raise BootloaderError("Penulisan otomatis sengaja dinonaktifkan pada rilis aman: validasi HTTP streaming dan erase perlu uji hardware.")
    finally:
        rom.close()


def _handle(conn):
    global _busy
    method, path, headers, first = _read_headers(conn)
    if method == "GET" and path in ("/", "/index.html"):
        _send(conn, 200, HTML, "text/html; charset=utf-8")
        return
    if method == "GET" and path == "/status":
        _send(conn, 200, "ready; destructive_flash=%s" % config.ENABLE_DESTRUCTIVE_FLASH)
        return
    if method == "POST" and path == "/flash":
        if _busy:
            _send(conn, 409, "Proses lain sedang berjalan.")
            return
        _busy = True
        try:
            _flash_stream(conn, headers, first)
        except PermissionError as e:
            _send(conn, 409, str(e))
        except (ValueError, BootloaderError, OSError) as e:
            try:
                _send(conn, 400, "Flashing dihentikan: %s" % e)
            except Exception:
                pass
        except Exception as e:
            try:
                _send(conn, 500, "Kesalahan internal: %s" % e)
            except Exception:
                pass
        finally:
            _busy = False
        return
    _send(conn, 400, "Endpoint tidak dikenal")


def run():
    if len(config.AP_PASSWORD) < 8 or config.AP_PASSWORD == "GANTI_PASSWORD_MINIMAL_8":
        raise ValueError("Edit AP_PASSWORD di config.py (minimal 8 karakter) sebelum menjalankan.")
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=config.AP_SSID, password=config.AP_PASSWORD)
    for _ in range(30):
        if ap.active():
            break
        time.sleep_ms(100)
    print("Wi-Fi AP:", config.AP_SSID)
    print("Alamat:", ap.ifconfig()[0])
    print("Safety lock destructive flash:", not config.ENABLE_DESTRUCTIVE_FLASH)
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen(1)
    server.settimeout(1)
    print("Buka http://%s/" % ap.ifconfig()[0])
    try:
        while True:
            try:
                conn, remote = server.accept()
            except OSError:
                gc.collect()
                continue
            conn.settimeout(8)
            try:
                _handle(conn)
            except Exception as e:
                print("HTTP error:", e)
                try:
                    _send(conn, 400, "Request gagal: %s" % e)
                except Exception:
                    pass
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
                gc.collect()
    finally:
        server.close()
