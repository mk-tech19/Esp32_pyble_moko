# Matriks uji sebelum mengembangkan write/erase
- [ ] Catat marking chip, ukuran flash aktual, versi ROM dan command list.
- [ ] Verifikasi erase command sesuai AN3155 untuk ROM target.
- [ ] Uji pada board yang dapat dipulihkan dengan ST-Link/SWD.
- [ ] Uji ukuran 255, 256, 257 byte dan file bukan kelipatan 4.
- [ ] Verifikasi read-back byte-for-byte atau metode CRC/hash yang sah.
- [ ] Pastikan BOOT0 LOW + reset menjalankan firmware yang benar.
- [ ] Jangan menyebut sukses penuh jika hanya ACK.
