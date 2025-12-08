# 📱 SISTEM ANTRIAN TABLET - DOKUMENTASI LENGKAP

> **Sistem Antrian Terintegrasi dengan Tablet Android, ESP32 P10 Display, dan Audio TTS**

---

## 📋 DAFTAR ISI

1. [Gambaran Umum](#gambaran-umum)
2. [Arsitektur Sistem](#arsitektur-sistem)
3. [Instalasi Cepat](#instalasi-cepat)
4. [Instalasi Manual](#instalasi-manual)
5. [Konfigurasi](#konfigurasi)
6. [Penggunaan](#penggunaan)
7. [ESP32 Setup](#esp32-setup)
8. [Troubleshooting](#troubleshooting)
9. [Spesifikasi Teknis](#spesifikasi-teknis)
10. [FAQ](#faq)

---

## 🎯 GAMBARAN UMUM

### Fitur Utama

- ✅ **Stand-alone System** - Tablet sebagai WiFi hotspot dan server
- ✅ **Web Interface** - Kontrol antrian via browser
- ✅ **ESP32 P10 Display** - Tampilan nomor antrian di layar LED
- ✅ **Audio TTS** - Panggilan suara otomatis (gTTS Indonesian)
- ✅ **High Quality Audio** - 48kHz 24-bit WAV format
- ✅ **Number-Only System** - Format 001-999 (tanpa prefix huruf)
- ✅ **Real-time WebSocket** - Komunikasi instant antar komponen

### Komponen Sistem

1. **Tablet Android** (Termux)
   - Node.js WebSocket server
   - Web interface (HTML/JS)
   - Python audio system (gTTS)

2. **ESP32 + P10 Display**
   - WiFi client
   - LED matrix display (32x16 atau 64x32)

3. **Browser** (Chrome/Firefox)
   - Control panel untuk operator

---

## 🏗️ ARSITEKTUR SISTEM

```
┌─────────────────────────────────────────────────┐
│           TABLET ANDROID (TERMUX)               │
│                                                 │
│  ┌──────────────┐         ┌─────────────┐     │
│  │  Node.js     │◄───────►│   Browser   │     │
│  │  WebSocket   │         │  Interface  │     │
│  │   Server     │         └─────────────┘     │
│  └──────┬───────┘                              │
│         │                                       │
│         ├──► Python Audio Player (gTTS)        │
│         │                                       │
│  ┌──────▼───────┐                              │
│  │ WiFi Hotspot │ (192.168.43.1)              │
│  └──────────────┘                              │
└─────────────────────────────────────────────────┘
           │
           │ WebSocket
           │
           ▼
    ┌──────────────┐
    │    ESP32     │
    │   + P10      │
    │   Display    │
    └──────────────┘
```

### Alur Data

1. Operator klik **PANGGIL** di browser
2. Browser → WebSocket → Server
3. Server → Audio Player → Speaker (TTS)
4. Server → WebSocket → ESP32
5. ESP32 → P10 Display (LED)

---

## ⚡ INSTALASI CEPAT

### Untuk Termux/Android

```bash
# 1. Clone atau copy project
cd ~
# (copy project ke folder ini)

# 2. Jalankan installer otomatis
chmod +x setup.sh
./setup.sh

# 3. Start server
node server.js

# 4. Akses browser
# http://localhost:8080
```

### Untuk Windows (Development)

```powershell
# 1. Install Node.js & Python dari website resmi
# 2. Install dependencies
npm install
pip install gtts pydub pygame

# 3. Generate audio
python generate_audio.py

# 4. Start server
node server.js

# 5. Akses browser
# http://localhost:8080
```

---

## 📦 INSTALASI MANUAL

### A. TERMUX/ANDROID SETUP

#### 1. Install Termux
- Download dari **F-Droid** (https://f-droid.org)
- ⚠️ **JANGAN** dari Play Store (versi lama)

#### 2. Update & Install Base Packages
```bash
pkg update && pkg upgrade
pkg install nodejs python sox ffmpeg git
```

#### 3. Setup Storage Access
```bash
termux-setup-storage
```

#### 4. Copy Project
```bash
# Via Git
cd ~
git clone <repo-url>
cd antrian_tablet_beta

# Atau manual copy ke:
# /storage/emulated/0/Download/antrian_tablet_beta
# Lalu:
cd ~/storage/downloads/antrian_tablet_beta
```

#### 5. Install Dependencies
```bash
# Node.js packages
npm install

# Python packages
pip install gtts pydub
```

#### 6. Generate Audio Files
```bash
python generate_audio.py
```

Output: ~40 file WAV di folder `audio/`

#### 7. Test Audio
```bash
python audio_player.py 23
```

Harus terdengar: *"Ding-dong, Nomor antrian dua puluh tiga, silakan ke loket"*

#### 8. Setup WiFi Hotspot
- Settings → Network & Internet → Hotspot
- Enable hotspot
- **Catat SSID & Password**
- IP default: `192.168.43.1`

#### 9. Start Server
```bash
node server.js
```

Output:
```
=====================================================
   SISTEM ANTRIAN - WEBSOCKET SERVER
=====================================================
Server running on port 8080
Web Interface: http://127.0.0.1:8080
WebSocket Server ready on ws://127.0.0.1:8080
```

#### 10. Akses Web Interface
Browser → `http://localhost:8080`

---

### B. WINDOWS SETUP (DEVELOPMENT)

#### 1. Install Prerequisites
- **Node.js** (https://nodejs.org) - LTS version
- **Python 3.10+** (https://python.org)
- **FFmpeg** (https://ffmpeg.org) - tambahkan ke PATH

#### 2. Install Dependencies
```powershell
npm install
pip install gtts pydub pygame
```

#### 3. Generate Audio
```powershell
python generate_audio.py
```

#### 4. Test Audio
```powershell
python audio_player.py 23
```

#### 5. Start Server
```powershell
node server.js
```

#### 6. Access Browser
`http://localhost:8080`

---

## ⚙️ KONFIGURASI

### Server Configuration (server.js)

```javascript
const PORT = 8080;  // Port server
let currentCalled = "000";  // Nomor yang dipanggil
let nextQueue = 1;          // Nomor antrian berikutnya
const queuePrefix = "";     // Prefix (kosong = number-only)
```

### Audio Configuration (generate_audio.py)

```python
AUDIO_DIR = "audio"         # Folder output
LANG = "id"                 # Bahasa Indonesia
# Format: 48kHz stereo 24-bit PCM
# Volume: -3dB (optimal clarity)
```

### ESP32 Configuration (esp32_client.ino)

```cpp
const char* ssid = "YOUR_HOTSPOT_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverIP = "192.168.43.1";  // IP tablet hotspot
const int serverPort = 8080;
```

---

## 🎮 PENGGUNAAN

### Web Interface

![Interface](https://via.placeholder.com/600x300.png?text=Queue+System+Interface)

#### Tombol Kontrol

1. **PANGGIL (CALL)**
   - Panggil nomor antrian berikutnya
   - Audio TTS otomatis
   - Display P10 update
   - Nomor bertambah otomatis

2. **PANGGIL ULANG (RECALL)**
   - Ulangi panggilan nomor terakhir
   - Audio & display sama

3. **CETAK NOMOR (PRINT)**
   - Print tiket antrian (jika ada printer)

4. **RESET**
   - Reset nomor antrian ke 001

#### Status Display

```
┌─────────────────────────────┐
│ Status Server: 🟢 Connected │
│ Nomor Dipanggil: 023        │
│ Nomor Berikutnya: 024       │
└─────────────────────────────┘
```

### Command Line

#### Generate Audio
```bash
python generate_audio.py
```

#### Test Audio
```bash
python audio_player.py <nomor>
# Contoh:
python audio_player.py 123
```

#### Start Server
```bash
node server.js
```

#### Check System
```bash
# Cek Node.js
node --version

# Cek Python
python --version

# Cek audio player
which play       # sox
which ffplay     # ffmpeg
```

---

## 🔌 ESP32 SETUP

### Hardware Wiring

#### ESP32 → P10 Panel (32x16)

| ESP32 Pin | P10 Pin | Fungsi |
|-----------|---------|--------|
| GPIO 16   | LAT     | Latch  |
| GPIO 19   | A       | Row A  |
| GPIO 23   | B       | Row B  |
| GPIO 18   | C       | Row C  |
| GPIO 5    | D       | Row D  |
| GPIO 2    | OE      | Output Enable |
| GND       | GND     | Ground |

#### Power Supply

- **P10 Panel**: 5V 2-4A
- **ESP32**: Powered via USB atau dari 5V supply (dengan voltage regulator)
- ⚠️ **GND harus common** antara ESP32 dan P10

### Software Setup

#### 1. Install Arduino IDE
- Download: https://arduino.cc/en/software
- Install untuk OS Anda

#### 2. Setup ESP32 Board
- File → Preferences
- Additional Board Manager URLs:
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```
- Tools → Board → Boards Manager
- Cari "esp32" → Install

#### 3. Install Libraries
- Tools → Manage Libraries
- Install:
  - `PxMatrix` (untuk P10 display)
  - `WebSocketsClient` (untuk WebSocket)
  - `ArduinoJson` (untuk JSON parsing)

#### 4. Upload Code
- Buka `esp32_client.ino`
- Edit konfigurasi:
  ```cpp
  const char* ssid = "YourHotspotSSID";
  const char* password = "YourPassword";
  const char* serverIP = "192.168.43.1";
  ```
- Select Board: ESP32 Dev Module
- Upload

#### 5. Monitor Serial
- Tools → Serial Monitor (115200 baud)
- Check connection status

### Expected Output

```
Connecting to WiFi: YourHotspotSSID
WiFi connected
IP: 192.168.43.xxx
Connecting to WebSocket: ws://192.168.43.1:8080
WebSocket Connected!
Received: 001
Display updated: 001
```

---

## 🔧 TROUBLESHOOTING

### Masalah Audio

#### ❌ Audio tidak keluar di Termux

**Solusi:**
```bash
# Cek audio player installed
which play       # sox
which ffplay     # ffmpeg

# Install jika belum ada
pkg install sox          # Recommended
# atau
pkg install x11-repo && pkg install ffmpeg
```

#### ❌ "pygame not available" di Termux

**Solusi:**
- Normal! Pygame tidak perlu di Termux
- Sistem menggunakan sox/ffplay
- Abaikan pesan ini

#### ❌ Volume tidak seimbang

**Solusi:**
Edit `generate_audio.py`:
```python
# Chime volume
os.system(f'... -filter:a "volume=-6dB" ...')

# TTS volume
os.system(f'... -filter:a "volume=-3dB" ...')
```

### Masalah WebSocket

#### ❌ ESP32 tidak connect

**Cek:**
1. SSID & password benar?
2. IP server benar? (`192.168.43.1`)
3. Hotspot aktif?
4. Serial Monitor error apa?

**Debug:**
```cpp
Serial.println("WiFi status: " + String(WiFi.status()));
Serial.println("Server IP: " + String(serverIP));
```

#### ❌ Browser tidak connect

**Solusi:**
```bash
# Cek server running
ps aux | grep node

# Restart server
pkill node
node server.js

# Cek port
netstat -tuln | grep 8080
```

### Masalah P10 Display

#### ❌ Display blank

**Cek:**
1. Power supply 5V cukup (min 2A)
2. Wiring correct?
3. GND common ESP32 & P10?

#### ❌ Display berkedip

**Solusi:**
```cpp
// Tambahkan kapasitor 1000uF di power supply
// Atau kurangi brightness
display.setBrightness(50);
```

#### ❌ Huruf terpotong

**Solusi:**
```cpp
// Sesuaikan posisi text
display.setTextWrap(false);
display.setCursor(0, 0);  // Adjust X,Y
```

### Masalah Python

#### ❌ ModuleNotFoundError: gtts

```bash
pip install gtts pydub
```

#### ❌ ffmpeg not found

**Termux:**
```bash
pkg install ffmpeg
```

**Windows:**
- Download: https://ffmpeg.org/download.html
- Extract dan tambahkan ke PATH

#### ❌ Permission denied (audio folder)

```bash
chmod -R 755 audio/
```

---

## 📊 SPESIFIKASI TEKNIS

### Audio System

#### Format
- **Container**: WAV (PCM)
- **Sample Rate**: 48kHz
- **Bit Depth**: 24-bit
- **Channels**: Stereo (2)
- **Quality**: Broadcast/Professional

#### Volume Levels
- **Chime**: -6dB (balanced)
- **Voice TTS**: -3dB (clear)
- **0.3s silence**: Anti-clipping padding

#### File Structure
```
audio/
├── chime.wav           # Ding-dong bell
├── prefix.wav          # "Nomor antrian"
├── suffix.wav          # "Silakan ke loket"
├── 0.wav - 20.wav      # 0-20 (21 files)
├── 30.wav - 90.wav     # Tens (7 files)
└── 100.wav - 900.wav   # Hundreds (9 files)

Total: ~40 files for 001-999
```

#### TTS Configuration
```python
gTTS(text=text, lang='id', slow=False)
# Indonesian voice, normal speed
# Natural pronunciation
```

### Network

#### WebSocket Protocol
```javascript
// Browser → Server
{
  "command": "CALL" | "RECALL" | "PRINT" | "RESET"
}

// Server → ESP32
{
  "queue": "023"
}

// Server → Browser
{
  "currentCalled": "023",
  "nextQueue": "024"
}
```

#### Ports
- **WebSocket**: 8080
- **HTTP**: 8080 (same port)

### Hardware Requirements

#### Tablet/Server
- **RAM**: Min 2GB
- **Storage**: Min 500MB free
- **Android**: 7.0+ (Termux)
- **WiFi**: 2.4GHz hotspot capable

#### ESP32
- **Board**: ESP32 Dev Module
- **RAM**: 520KB
- **Flash**: 4MB
- **WiFi**: 802.11 b/g/n

#### P10 Display
- **Size**: 32x16 pixels (or 64x32)
- **Voltage**: 5V
- **Current**: 2-4A per panel
- **Interface**: HUB75

---

## ❓ FAQ

### Umum

**Q: Apakah bisa offline?**  
A: Ya, sistem full offline. Tablet jadi hotspot sendiri.

**Q: Berapa nomor maksimal?**  
A: 001-999 (999 nomor)

**Q: Bisa tambah printer?**  
A: Ya, via Bluetooth. Edit `server.js` untuk integrasi printer.

**Q: Bisa multi loket?**  
A: Perlu modifikasi. Tambah prefix huruf (A, B, C, dst).

### Audio

**Q: Suara terlalu robot?**  
A: Sudah dioptimasi dengan normal speed + Indonesian accent. Untuk lebih natural, gunakan cloud TTS premium.

**Q: Bisa ganti bahasa?**  
A: Edit `generate_audio.py`:
```python
LANG = "id"  # Ganti: en, ar, ms, dll
```

**Q: Bisa custom audio?**  
A: Ya, replace file WAV di folder `audio/` dengan recording sendiri.

### Hardware

**Q: ESP32 bisa diganti Arduino?**  
A: Tidak recommended. Arduino UNO tidak punya WiFi. Butuh modul tambahan.

**Q: P10 bisa diganti LCD/OLED?**  
A: Bisa. Edit `esp32_client.ino` sesuai library display.

**Q: Butuh power supply berapa Ampere?**  
A: 
- 1 panel P10: 2-3A
- 2 panel: 5A
- 3 panel: 10A (gunakan PSU industrial)

### Development

**Q: Bisa tambah database?**  
A: Ya. Install MongoDB/SQLite untuk log history.

**Q: Bisa web external?**  
A: Ya. Setup port forwarding atau deploy ke VPS.

**Q: Bisa mobile app?**  
A: Ya. Buat React Native app dengan WebSocket client.

---

## 📝 CATATAN AKHIR

### Credits
- **gTTS**: Google Text-to-Speech
- **PxMatrix**: P10 LED library
- **WebSocket**: Real-time communication
- **Node.js**: Server runtime
- **Termux**: Android Linux environment

### Version
- **System**: v1.0.0
- **Audio**: 48kHz 24-bit WAV
- **Format**: Number-only (001-999)
- **Platform**: Termux/Android + ESP32

### Support
Untuk bantuan lebih lanjut:
1. Cek troubleshooting section
2. Baca FAQ
3. Test dengan `audio_player.py` untuk isolasi masalah
4. Check Serial Monitor ESP32 untuk debug hardware

### License
Open source untuk penggunaan internal. Modifikasi bebas sesuai kebutuhan.

---

**🎉 Selamat menggunakan Sistem Antrian Tablet!**

*Dokumentasi ini dibuat dengan ❤️ untuk kemudahan setup dan maintenance*
