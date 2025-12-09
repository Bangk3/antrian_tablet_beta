# Quick Start - mDNS + UDP Discovery

## 🚀 Setup Cepat (5 Menit)

### 1️⃣ Di Termux (Tablet Android)

```bash
# Install dependencies (tanpa Avahi - UDP Discovery lebih reliable!)
pkg install nodejs sox python -y

# Masuk ke folder project
cd ~/antrian_tablet_beta

# Install NPM packages
npm install

# Generate audio files (jika belum)
python generate_audio.py

# Jalankan server
npm start
```

**💡 REKOMENDASI: Skip Avahi!**
- ✅ **UDP Discovery lebih reliable** di Termux
- ✅ Tidak ada dependency issues
- ✅ Tidak ada daemon errors
- ✅ Production-ready without mDNS

**Jika tetap ingin coba Avahi (optional):**
```bash
pkg install root-repo
pkg install avahi runit
npm run setup-avahi
```
⚠️ Sering error: "unable to change to service directory" - **lebih baik skip!**

### 2️⃣ Di Arduino IDE (ESP32)

1. Install libraries:
   - WebSocketsClient (by Markus Sattler)
   - ArduinoJson (by Benoit Blanchon)

2. Buka file: `esp32_client_example.ino`

3. Edit WiFi credentials:
```cpp
const char* WIFI_SSID = "NamaHotspotTablet";
const char* WIFI_PASSWORD = "Password123";
```

4. Upload ke ESP32

5. Buka Serial Monitor (115200 baud)

### 3️⃣ Test

1. Buka browser di tablet: `http://127.0.0.1:8080`
2. Tekan tombol **PANGGIL**
3. ✅ Audio diputar di tablet
4. ✅ Nomor muncul di Serial Monitor ESP32

## 📡 Metode Discovery

ESP32 akan otomatis mencoba 2 metode:

### Method 1: mDNS (Recommended)
```
ESP32 → resolve "antrian-server.local" → Server IP
```
✅ Zero-configuration
✅ Hostname tetap (IP boleh berubah)
✅ Reliable

### Method 2: UDP Discovery (Fallback)
```
ESP32 → broadcast "ANTRIAN_DISCOVERY" → Server reply IP
```
✅ Backup jika mDNS diblock
✅ Fast discovery
✅ Works on any network

## 🔍 Verifikasi

### Server (Termux)
Output harus menunjukkan:
```
[mDNS] ✓ Service published: antrian-server.local
[UDP] ✓ Discovery server listening on port 9999
```

### ESP32 (Serial Monitor)
Output harus menunjukkan:
```
[mDNS] ✓ Server found at: 192.168.43.1
[WebSocket] ✓ Connected!
```

ATAU (jika mDNS gagal):
```
[mDNS] ❌ Could not resolve hostname
[UDP] ✓ Server found at: 192.168.43.1
[WebSocket] ✓ Connected!
```

## ⚠️ Troubleshooting

### Server tidak start
```bash
# Cek apakah port 8080 sudah dipakai
lsof -i :8080

# Kill process jika ada
kill -9 $(lsof -t -i:8080)
```

### Avahi error / tidak bisa install
```bash
# Install root-repo terlebih dahulu
pkg install root-repo

# Kemudian install avahi
pkg install avahi runit

# Check status
sv status avahi-daemon

# Restart
sv restart avahi-daemon

# Enable auto-start
sv-enable avahi-daemon
```

**Jika tetap gagal:**
- ✅ Sistem tetap berfungsi dengan UDP Discovery
- ✅ Tidak perlu mDNS untuk production
- ℹ️ UDP Discovery lebih reliable di beberapa Android devices

### ESP32 tidak connect
1. Pastikan SSID & password benar
2. Cek IP tablet: `ifconfig` atau `ip addr`
3. Pastikan ESP32 dapat IP di subnet yang sama
4. Test ping dari ESP32 ke tablet

## 📚 Dokumentasi Lengkap

Lihat file: `SETUP_MDNS_UDP.md` untuk dokumentasi detail.

## 🎯 Architecture

```
┌──────────────────┐
│     TABLET       │
│   (Hotspot ON)   │
│                  │
│  ┌────────────┐  │
│  │  Node.js   │  │
│  │  Server    │  │
│  │            │  │
│  │  • mDNS    │  │ ← antrian-server.local
│  │  • UDP     │  │ ← Port 9999
│  │  • WS      │  │ ← Port 8080
│  └────────────┘  │
└────────┬─────────┘
         │ WiFi Hotspot
         │
         ▼
┌──────────────────┐
│      ESP32       │
│   (Display)      │
│                  │
│  1. mDNS query   │
│  2. UDP discover │ (fallback)
│  3. WS connect   │
│  4. Show queue   │
└──────────────────┘
```

## ✅ Keuntungan Metode Ini

| Feature | mDNS | UDP | Direct IP |
|---------|------|-----|-----------|
| Zero-config | ✅ | ✅ | ❌ |
| IP berubah OK | ✅ | ✅ | ❌ |
| Works everywhere | ⚠️ | ✅ | ✅ |
| Fast | ✅ | ✅ | ✅ |
| Reliable | ✅ | ✅ | ✅ |

**Kombinasi mDNS + UDP = Best of both worlds!** 🎉
