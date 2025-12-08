# Quick Start Guide - Sistem Antrian dengan Audio Profesional

## 🚀 Langkah-langkah Setup

### 1. Install Dependencies

```bash
# Install Node.js dependencies (untuk server)
npm install

# Install Python dependencies (untuk audio)
pip install gtts pygame
```

### 2. Generate Audio Files

```bash
python generate_audio.py
```

**Output yang diharapkan:**
```
0. Getting chime sound...
  ✓ Downloaded: chime.mp3

1. Generating prefix and suffix (slow mode for clarity)...
  ✓ Created: prefix.mp3 (slow) - 'Nomor antrian'
  ✓ Created: suffix.mp3 (slow) - 'silakan ke loket'

2. Generating 0-20 (clear pronunciation)...
  ✓ Created: 0.mp3 (slow) - 'nol'
  ✓ Created: 1.mp3 (slow) - 'satu'
  ...

Total: ~46 files for support A001-F999

Audio improvements:
✓ Slow mode enabled for clarity
✓ Chime sound for attention
✓ Professional timing and pauses
```

Folder `audio/` akan berisi ~46 file MP3.

### 3. Test Audio

```bash
python audio_player.py A22
```

**Output yang diharapkan:**
```
Checking dependencies...
  ✓ pygame available

Playing: A22 (Letter: A, Number: 22)
  Audio parts: [20, 2]
  Method: pygame (sequential)
  Playing 6 audio segments with professional timing...
  [1/6] chime.mp3
  [2/6] prefix.mp3
  [3/6] letter_A.mp3
  [4/6] 20.mp3
  [5/6] 2.mp3
  [6/6] suffix.mp3
  ✓ Finished playing A22
```

**Audio yang terdengar:**
```
*DING DONG* ... "Nomor antrian" ... "A" .. "dua puluh" . "dua" ... "silakan ke loket"
```

### 4. Jalankan Server

```bash
node server.js
```

**Output yang diharapkan:**
```
=====================================================
   SISTEM ANTRIAN - WEBSOCKET SERVER
=====================================================
Server running on port 8080
Web Interface: http://127.0.0.1:8080
WebSocket URL: ws://127.0.0.1:8080

CATATAN:
- Pastikan Tablet dalam mode Hotspot
- ESP32 connect ke: ws://[IP_HOTSPOT]:8080
- Browser access: http://127.0.0.1:8080
=====================================================
```

### 5. Buka Web Interface

Di browser (Chrome/Firefox):
```
http://127.0.0.1:8080
```

atau

```
http://localhost:8080
```

### 6. Test Sistem

1. **Klik tombol "CETAK NOMOR"** 
   - Nomor antrian bertambah (A001, A002, dst)
   
2. **Klik tombol "PANGGIL"**
   - Audio akan diputar dengan format:
     ```
     *DING DONG* → "Nomor antrian" → "A" → "satu" → "silakan ke loket"
     ```
   - Nomor tampil di status web
   - Jika ESP32 connect, akan tampil di P10 display

3. **Klik tombol "PANGGIL ULANG"**
   - Audio nomor terakhir diputar ulang

---

## 📊 Checklist

- [ ] **npm install** - Dependencies Node.js terinstall
- [ ] **pip install gtts pygame** - Python libraries terinstall
- [ ] **python generate_audio.py** - Audio files generated (~46 files)
- [ ] **python audio_player.py A22** - Audio test berhasil
- [ ] **node server.js** - Server running
- [ ] **http://127.0.0.1:8080** - Web interface terbuka
- [ ] **Klik PANGGIL** - Audio keluar dengan chime + slow mode

---

## 🎯 Flow Lengkap

```
USER ACTION                SERVER                   AUDIO PLAYER
───────────────────────────────────────────────────────────────
Klik "PANGGIL"    →    handleCommand('CALL')
                            ↓
                       Update state
                       currentCalled = A001
                            ↓
                       playAudio('A001')      →   python audio_player.py A001
                            ↓                            ↓
                       sendToESP32()                Load files:
                       {queue: "A001"}              - chime.mp3
                            ↓                        - prefix.mp3
                       sendStatusToBrowser()        - letter_A.mp3
                                                    - 1.mp3
                                                    - suffix.mp3
                                                        ↓
                                                    Play with timing:
                                                    *DING* (500ms)
                                                    "Nomor antrian" (300ms)
                                                    "A" (200ms)
                                                    "satu" (300ms)
                                                    "silakan ke loket"
```

---

## 🔊 Audio Features

### ✅ Yang Sudah Aktif:

1. **Chime Sound** 
   - Bunyi "ding" di awal
   - Auto-download atau manual

2. **Slow Mode gTTS**
   - Semua angka dan text lebih lambat
   - Lebih jelas dan mudah didengar

3. **Professional Timing**
   - Chime: 500ms pause
   - Prefix: 300ms pause
   - Letter: 200ms pause
   - Between numbers: 150ms
   - Before suffix: 300ms

4. **Sequential Playback**
   - File audio diputar satu per satu
   - Smooth dan natural

---

## 🐛 Troubleshooting

### Problem: Audio tidak keluar saat klik PANGGIL

**Solution:**
```bash
# 1. Cek audio files ada
dir audio\

# 2. Test manual
python audio_player.py A1

# 3. Cek console server
# Lihat output [AUDIO] di terminal server
```

### Problem: Error "pygame not found"

**Solution:**
```bash
pip install pygame
```

### Problem: Error "audio files not found"

**Solution:**
```bash
python generate_audio.py
```

### Problem: Chime tidak download otomatis

**Solution:**
Download manual:
1. Buka: https://pixabay.com/sound-effects/search/ding/
2. Download file "ding.mp3" atau "chime.mp3"
3. Simpan di `audio/chime.mp3`

### Problem: Server error saat play audio

**Solution:**
```bash
# Pastikan Python bisa dijalankan dari command line
python --version

# Pastikan audio_player.py di folder yang sama dengan server.js
dir audio_player.py
```

---

## 📱 Setup untuk Tablet Android (Termux)

### 1. Install Termux dari F-Droid

### 2. Setup di Termux

```bash
# Update packages
pkg update && pkg upgrade

# Install Node.js dan Python
pkg install nodejs python

# Install dependencies
npm install
pip install gtts pygame

# Generate audio (bisa di Windows dulu, lalu copy)
python generate_audio.py

# Setup hotspot di tablet

# Jalankan server
node server.js
```

### 3. Akses Web Interface

Di browser tablet:
```
http://127.0.0.1:8080
```

---

## ✅ Final Check

Pastikan semua ini sudah done:

```bash
# 1. Dependencies installed
npm list ws
pip list | grep gtts
pip list | grep pygame

# 2. Audio files generated
ls audio/ | wc -l
# Should show ~46 files

# 3. Test audio manually
python audio_player.py A1

# 4. Server running
node server.js
# Server should start without errors

# 5. Web interface accessible
# Open http://127.0.0.1:8080 in browser

# 6. Audio works from web
# Click "PANGGIL" button, audio should play
```

---

## 🎉 Success Criteria

Sistem berhasil jika:

✅ Server running tanpa error  
✅ Web interface terbuka  
✅ Audio keluar saat klik PANGGIL  
✅ Audio include: chime + slow speech + proper timing  
✅ Status nomor update di web  
✅ ESP32 (jika ada) menerima data  

---

**Selamat! Sistem antrian Anda siap digunakan!** 🚀
