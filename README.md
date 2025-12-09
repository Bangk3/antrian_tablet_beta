# 📱 Sistem Antrian Tablet

> **Stand-alone Queue Management System** dengan Tablet Android, ESP32 P10 Display, dan Audio TTS Indonesia

[![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Android-green)]()
[![Node](https://img.shields.io/badge/Node.js-18%2B-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![Audio](https://img.shields.io/badge/Audio-48kHz%2024bit-red)]()

---

## ✨ Fitur Utama

- 🌐 **Stand-alone System** - Tablet sebagai WiFi hotspot & server
- 🎨 **Web Interface** - Kontrol antrian via browser
- 📟 **ESP32 P10 Display** - Tampilan LED real-time
- 🔊 **Audio TTS** - Panggilan suara otomatis bahasa Indonesia
- 🎵 **High Quality** - Audio 48kHz 24-bit WAV format
- 🔢 **Simple Format** - Nomor 001-999 (tanpa prefix)
- ⚡ **Real-time** - WebSocket communication

---

## 🚀 Quick Start

### Instalasi Otomatis (Termux)

```bash
# 1. Clone project
git clone <repo-url>
cd antrian_tablet_beta

# 2. Run installer
chmod +x setup.sh
./setup.sh

# 3. Start server
node server.js

# 4. Akses browser: http://localhost:8080
```

### Manual Installation

```bash
# Install dependencies
pkg install nodejs python sox ffmpeg
npm install
pip install gtts pydub

# Generate audio files
python generate_audio.py

# Start server
node server.js
```

---

## 📦 Komponen Sistem

```
┌─────────────────────────────────────┐
│ Tablet Android (Termux)             │
│                                     │
│  • WiFi Hotspot                     │
│  • Node.js Server (WebSocket)       │
│  • mDNS Service (antrian-server)    │
│  • UDP Discovery (Port 9999)        │
│  • Web Interface (Port 8080)        │
│  • Audio Player (Sox)               │
└──────────┬──────────────────────────┘
           │ WiFi Network
           │ (Auto-Discovery)
           │
    ┌──────┴────────┐
    │ ESP32 + P10   │
    │               │
    │  1. mDNS      │ ← antrian-server.local
    │  2. UDP       │ ← Broadcast discovery
    │  3. WebSocket │ ← Real-time updates
    └───────────────┘
```

### Hardware Requirements

- **Tablet Android** 7.0+ (2GB RAM)
- **ESP32 DevKit** v1
- **P10 LED Panel** (32x16 atau 64x32)
- **Power Supply** 5V 3A

---

## 🎮 Penggunaan

### Web Interface

**Kontrol:**
- ✅ **PANGGIL** - Panggil nomor berikutnya
- 🔄 **PANGGIL ULANG** - Ulangi panggilan
- 🖨️ **CETAK NOMOR** - Print tiket

### Auto-Discovery

ESP32 otomatis menemukan server dengan 2 metode:
1. **mDNS** (Primary): `antrian-server.local` - Zero configuration
2. **UDP Broadcast** (Fallback): Port 9999 - Network discovery

**Tidak perlu hardcode IP!** ✨

### Audio Output

Format: `Ding-dong → "Nomor antrian [XXX], silakan ke loket"`

Contoh:
- **001**: "Nomor antrian nol nol satu, silakan ke loket"
- **023**: "Nomor antrian dua puluh tiga, silakan ke loket"
- **156**: "Nomor antrian seratus lima puluh enam, silakan ke loket"

---

## 🔌 ESP32 Wiring

```
ESP32 Pin  →  P10 Pin
─────────────────────
GPIO 16    →  LAT
GPIO 19    →  A
GPIO 23    →  B
GPIO 18    →  C
GPIO 5     →  D
GPIO 2     →  OE
GND        →  GND
```

**Power:** P10 panel gunakan 5V 3A external supply

---

## ⚙️ Konfigurasi

### 1. Server (server.js)

```javascript
const PORT = 8080;
let nextQueue = 1;
const queuePrefix = "";  // Kosong = number only
```

### 2. ESP32 (main.cpp)

```cpp
const char* ssid = "YOUR_HOTSPOT_SSID";
const char* password = "YOUR_PASSWORD";

// Auto-discovery enabled - no need to hardcode IP!
const char* mdns_hostname = "antrian-server";  // Will resolve to antrian-server.local
const int udp_discovery_port = 9999;            // Fallback UDP discovery
```

### 3. Audio (generate_audio.py)

```python
LANG = "id"              # Indonesian
# Format: 48kHz stereo 24-bit PCM
# Volume: -3dB optimal clarity
```

---

## 📚 Dokumentasi

**📖 Dokumentasi lengkap:** [`DOCUMENTATION.md`](./DOCUMENTATION.md)

Berisi:
- ✅ Instalasi step-by-step detail
- ✅ Konfigurasi lengkap semua komponen
- ✅ ESP32 setup dengan wiring diagram
- ✅ Troubleshooting lengkap
- ✅ FAQ (Frequently Asked Questions)
- ✅ Spesifikasi teknis sistem

---

## 🛠️ Troubleshooting

### Audio tidak keluar (Termux)

```bash
# Install audio player
pkg install sox          # Recommended
# atau
pkg install x11-repo && pkg install ffmpeg

# Test audio
python audio_player.py 23
```

### ESP32 tidak connect

1. Cek SSID & password di kode
2. Pastikan hotspot tablet aktif
3. Pastikan Avahi daemon running: `sv status avahi-daemon`
4. Cek Serial Monitor untuk debug:
   - `[mDNS] Server found at: X.X.X.X` ✓
   - `[UDP] Server found at: X.X.X.X` ✓ (jika mDNS gagal)
   - `[WS] Connected!` ✓
5. Jika semua gagal, restart server & ESP32

### Browser tidak connect

```bash
# Restart server
pkill node
node server.js

# Akses: http://localhost:8080
```

**Lebih detail:** Lihat [Troubleshooting Section](./DOCUMENTATION.md#troubleshooting)

---

## 📊 Spesifikasi Teknis

### Audio System
- **Format:** WAV PCM
- **Sample Rate:** 48kHz
- **Bit Depth:** 24-bit
- **Channels:** Stereo
- **Files:** ~40 modular files
- **Range:** 001-999

### Network
- **WebSocket:** Port 8080 (Real-time communication)
- **mDNS:** antrian-server.local (Zero-config discovery)
- **UDP Discovery:** Port 9999 (Fallback method)
- **Transport:** JSON messages
- **Discovery Timeout:** mDNS 5s, UDP 10s

### Platform
- **Server:** Node.js 18+
- **TTS:** Python 3.10+ (gTTS)
- **Audio:** Sox
- **mDNS:** Avahi daemon
- **Client:** ESP32 (Arduino/PlatformIO)

---

## 📁 Struktur Project

```
antrian_tablet_beta/
├── setup.sh              # Auto installer (with Avahi)
├── DOCUMENTATION.md      # Dokumentasi lengkap
├── QUICKSTART.md         # Quick start guide (5 menit)
├── SETUP_MDNS_UDP.md     # mDNS + UDP setup guide
├── ESP32_FIXES.md        # ESP32 bug fixes guide
├── README.md             # File ini
├── server.js             # Node.js WebSocket server (mDNS + UDP)
├── index.html            # Web control interface
├── package.json          # Node dependencies
├── generate_audio.py     # Audio generator (gTTS)
├── audio_player.py       # Audio playback system (Sox)
├── chime.mp3             # Bell sound
└── audio/                # Generated audio files (WAV)
    ├── chime.wav
    ├── prefix.wav
    ├── suffix.wav
    ├── 0.wav - 20.wav
    ├── 30.wav - 90.wav
    └── 100.wav - 900.wav

ESP32 Project (separate folder):
└── src/
    └── main.cpp          # ESP32 firmware (with auto-discovery)
```

---

## 🤝 Contributing

Kontribusi welcome! Silakan:
1. Fork repository
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 TODO / Roadmap

- [ ] Database integration (MongoDB/SQLite)
- [ ] Multi-counter support (A001, B001, dst)
- [ ] Mobile app (React Native)
- [ ] Cloud TTS integration (premium voices)
- [ ] Web admin panel (statistics)
- [ ] Printer integration (thermal/bluetooth)
- [ ] Multi-language support

---

## 📄 License

Open source untuk penggunaan internal & pendidikan. Modifikasi bebas sesuai kebutuhan.

---

## 🙏 Credits

- **gTTS** - Google Text-to-Speech
- **PxMatrix** - P10 LED Display library
- **WebSocket (ws)** - Real-time communication
- **Node.js** - Server runtime
- **Termux** - Android Linux environment
- **ESP32** - Arduino WiFi microcontroller

---

## 📧 Support

Untuk pertanyaan dan bantuan:
1. Baca [DOCUMENTATION.md](./DOCUMENTATION.md)
2. Cek [FAQ Section](./DOCUMENTATION.md#faq)
3. Lihat [Troubleshooting](./DOCUMENTATION.md#troubleshooting)
4. Open issue di GitHub

---

<div align="center">

**⭐ Jangan lupa beri star jika project ini membantu! ⭐**

Made with ❤️ for easier queue management

</div>
