# Setup Audio System dengan gTTS

Panduan lengkap untuk setup sistem audio menggunakan gTTS (Google Text-to-Speech) dengan file audio yang minimal dan efisien.

---

## 🎯 Konsep

Alih-alih membuat 999 file audio (A001 - A999), kita hanya membuat **~45 file audio** yang bisa digabungkan untuk membuat semua kombinasi nomor.

### Contoh:
- **A22** = `letter_A.mp3` + `20.mp3` + `2.mp3`
- **B156** = `letter_B.mp3` + `100.mp3` + `50.mp3` + `6.mp3`
- **C7** = `letter_C.mp3` + `7.mp3`

---

## 📦 Install Dependencies

### Di Windows (untuk generate audio):
```bash
pip install gtts pydub
```

### Di Termux/Android (untuk jalankan server):
```bash
pkg install python
pip install pydub
pkg install ffmpeg
```

---

## 🔧 Generate Audio Files

### 1. Jalankan Generator
```bash
python generate_audio.py
```

Output:
```
✓ Created: prefix.mp3 - 'Nomor antrian'
✓ Created: suffix.mp3 - 'silakan ke loket'
✓ Created: 0.mp3 - 'nol'
✓ Created: 1.mp3 - 'satu'
...
✓ Created: 20.mp3 - 'dua puluh'
✓ Created: 30.mp3 - 'tiga puluh'
...
✓ Created: 900.mp3 - 'sembilan ratus'
✓ Created: letter_A.mp3 - 'A'
...

Total: ~45 files created
```

### 2. File Audio yang Dihasilkan

```
audio/
├── prefix.mp3          # "Nomor antrian"
├── suffix.mp3          # "silakan ke loket"
├── 0.mp3               # "nol"
├── 1.mp3               # "satu"
├── 2.mp3               # "dua"
...
├── 20.mp3              # "dua puluh"
├── 30.mp3              # "tiga puluh"
├── 40.mp3              # "empat puluh"
...
├── 90.mp3              # "sembilan puluh"
├── 100.mp3             # "seratus"
├── 200.mp3             # "dua ratus"
...
├── 900.mp3             # "sembilan ratus"
├── letter_A.mp3        # "A"
├── letter_B.mp3        # "B"
...
└── letter_F.mp3        # "F"
```

Total: **45 files** untuk support **A001 - F999** (6000 kombinasi)

---

## 🎵 Test Audio Player

### Test tanpa play (lihat struktur):
```bash
python audio_player.py
```

Output:
```
Test: A1
  Letter: A, Number: 1
  Audio parts: [1]
  Files needed: letter_A.mp3, 1.mp3

Test: A22
  Letter: A, Number: 22
  Audio parts: [20, 2]
  Files needed: letter_A.mp3, 20.mp3, 2.mp3

Test: A156
  Letter: A, Number: 156
  Audio parts: [100, 50, 6]
  Files needed: letter_A.mp3, 100.mp3, 50.mp3, 6.mp3
```

### Play audio untuk nomor tertentu:
```bash
python audio_player.py A22
```

Output audio: **"Nomor antrian A dua puluh dua silakan ke loket"**

```bash
python audio_player.py B156
```

Output audio: **"Nomor antrian B seratus lima puluh enam silakan ke loket"**

---

## 🚀 Integrasi dengan Server

Server Node.js sudah di-update untuk memanggil Python script otomatis.

### File: server.js
```javascript
function playAudio(queueNumber) {
    console.log(`[AUDIO] Playing: ${queueNumber}`);
    
    const { exec } = require('child_process');
    
    exec(`python audio_player.py ${queueNumber}`, (error, stdout, stderr) => {
        if (error) {
            console.error('[AUDIO] Error:', error.message);
            return;
        }
        console.log('[AUDIO] Output:', stdout);
    });
}
```

---

## 📋 Cara Penggunaan

### 1. Setup Awal (Hanya Sekali)

**Di Windows/Laptop:**
```bash
# Install dependencies
pip install gtts pydub

# Generate audio files
python generate_audio.py

# Test audio
python audio_player.py A22
```

### 2. Copy ke Tablet

Copy folder `audio/` ke tablet:
```
/storage/emulated/0/Download/antrian_tablet_beta/audio/
```

### 3. Install Dependencies di Termux

```bash
pkg install python ffmpeg
pip install pydub
```

### 4. Jalankan Server

```bash
cd ~/storage/downloads/antrian_tablet_beta
node server.js
```

### 5. Test dari Web Interface

- Buka http://127.0.0.1:8080
- Klik tombol **PANGGIL**
- Audio akan otomatis diputar!

---

## 🔢 Contoh Kombinasi Audio

| Nomor | Files yang Digabungkan | Audio Output |
|-------|------------------------|--------------|
| A1 | prefix + letter_A + 1 + suffix | "Nomor antrian A satu silakan ke loket" |
| A7 | prefix + letter_A + 7 + suffix | "Nomor antrian A tujuh silakan ke loket" |
| A15 | prefix + letter_A + 15 + suffix | "Nomor antrian A lima belas silakan ke loket" |
| A22 | prefix + letter_A + 20 + 2 + suffix | "Nomor antrian A dua puluh dua silakan ke loket" |
| A100 | prefix + letter_A + 100 + suffix | "Nomor antrian A seratus silakan ke loket" |
| A156 | prefix + letter_A + 100 + 50 + 6 + suffix | "Nomor antrian A seratus lima puluh enam silakan ke loket" |
| B300 | prefix + letter_B + 300 + suffix | "Nomor antrian B tiga ratus silakan ke loket" |
| C999 | prefix + letter_C + 900 + 90 + 9 + suffix | "Nomor antrian C sembilan ratus sembilan puluh sembilan silakan ke loket" |

---

## ⚙️ Konfigurasi

### Ganti Bahasa (jika perlu)

Edit `generate_audio.py`:
```python
LANG = "id"  # Indonesia
# LANG = "en"  # English
```

### Tambah Prefix Letter

Edit `generate_audio.py`:
```python
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # Tambah G, H
```

### Ubah Text Prefix/Suffix

Edit `generate_audio.py`:
```python
create_audio_file("Nomor antrian", "prefix.mp3")
create_audio_file("silakan ke loket satu", "suffix.mp3")  # Tambah "satu"
```

---

## 🐛 Troubleshooting

### Error: "gTTS not installed"
```bash
pip install gtts
```

### Error: "pydub not installed"
```bash
pip install pydub
```

### Error: "ffmpeg not found"

**Windows:**
- Download ffmpeg: https://ffmpeg.org/download.html
- Extract dan add to PATH

**Termux:**
```bash
pkg install ffmpeg
```

### Audio tidak keluar

1. **Cek file audio ada:**
   ```bash
   ls audio/
   ```

2. **Test manual:**
   ```bash
   python audio_player.py A22
   ```

3. **Cek volume tablet**

4. **Cek log server:**
   ```bash
   node server.js
   # Lihat output [AUDIO]
   ```

### Audio patah-patah

Edit `audio_player.py`, ubah pause duration:
```python
combined += AudioSegment.silent(duration=200)  # Naikkan jadi 300-500
```

---

## 📊 Efisiensi Storage

| Method | Files Needed | Total Size (est.) |
|--------|--------------|-------------------|
| **File per nomor** | 999 files | ~30 MB |
| **Sistem modular (ini)** | 45 files | **~1.5 MB** |

**Penghematan: ~95%** 🎉

---

## 🎯 Keuntungan Sistem Ini

✅ **Minimal file audio** (~45 vs 999)  
✅ **Fleksibel** (mudah ubah prefix/suffix)  
✅ **Natural sounding** (gTTS Google quality)  
✅ **Efisien storage** (~1.5 MB total)  
✅ **Mudah maintain** (cukup edit 1 file generator)  
✅ **Support 1-999** dengan kombinasi  
✅ **Multi-prefix** (A, B, C, dst)  

---

## 🚀 Quick Start Commands

```bash
# 1. Install
pip install gtts pydub

# 2. Generate audio files
python generate_audio.py

# 3. Test audio
python audio_player.py A22

# 4. Start server
node server.js

# 5. Access web interface
# http://127.0.0.1:8080
```

**SELESAI!** Audio siap digunakan! 🎉

---

## 📝 Notes

- Audio files hanya perlu di-generate **sekali**
- Bisa di-generate di Windows/Mac, lalu copy ke tablet
- Tidak perlu internet saat running (audio sudah tersimpan)
- Kualitas audio tergantung gTTS Google
- Bisa custom text sesuai kebutuhan

---

Jika ada pertanyaan atau error, cek:
1. Apakah folder `audio/` sudah ada dan berisi file?
2. Apakah Python dan dependencies sudah terinstall?
3. Apakah ffmpeg sudah terinstall?
4. Cek log output saat menjalankan script
