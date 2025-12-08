"""
=====================================================
GENERATOR AUDIO UNTUK SISTEM ANTRIAN
Menggunakan gTTS (Google Text-to-Speech)
=====================================================

Script ini akan generate file audio minimal:
- 0.mp3 sampai 20.mp3 (21 file)
- 30.mp3, 40.mp3, 50.mp3, dst (8 file)
- prefix.mp3("Nomor antrian")
- suffix.mp3 ("silakan ke loket")

Total: ~35 file untuk support 1-999

Cara kerja:
- Nomor 22 = prefix + "20" + "2" + suffix
- Nomor 156 = prefix + "100" + "50" + "6" + suffix
"""

from gtts import gTTS
import os
import urllib.request

# Konfigurasi
AUDIO_DIR = "audio"
LANG = "id"  # Bahasa Indonesia

def create_audio_file(text, filename, slow=False):
    """Generate file audio dari text menggunakan gTTS"""
    try:
        # Gunakan slow=True untuk kejelasan yang lebih baik
        tts = gTTS(text=text, lang=LANG, slow=slow)
        filepath = os.path.join(AUDIO_DIR, filename)
        tts.save(filepath)
        speed_info = " (slow)" if slow else ""
        print(f"✓ Created: {filename}{speed_info} - '{text}'")
        return True
    except Exception as e:
        print(f"✗ Error creating {filename}: {e}")
        return False

def download_chime_sound():
    """Download chime sound dari internet (jika tidak ada)"""
    chime_path = os.path.join(AUDIO_DIR, "chime.mp3")
    
    if os.path.exists(chime_path):
        print(f"✓ Chime sound already exists: chime.mp3")
        return True
    
    print("Downloading chime sound...")
    
    # URL chime sound gratis dari freesound.org
    # Alternatif: bisa ganti dengan URL lain atau skip
    chime_urls = [
        "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3",
        "https://www.soundjay.com/misc/sounds/bell-ringing-01.mp3"
    ]
    
    for url in chime_urls:
        try:
            print(f"  Trying: {url}")
            urllib.request.urlretrieve(url, chime_path)
            print(f"✓ Downloaded: chime.mp3")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    print("✗ Could not download chime sound automatically")
    print(f"  Please download manually and save as: {chime_path}")
    print("  Recommended sites:")
    print("  - https://pixabay.com/sound-effects/search/ding/")
    print("  - https://www.zapsplat.com/")
    return False

def generate_audio_files():
    """Generate semua file audio yang diperlukan"""
    
    # Buat folder audio jika belum ada
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
        print(f"✓ Created directory: {AUDIO_DIR}/")
    
    print("\n" + "="*60)
    print("GENERATING AUDIO FILES WITH IMPROVED CLARITY")
    print("="*60)
    
    # 0. CHIME SOUND
    print("\n0. Getting chime sound...")
    download_chime_sound()
    
    # 1. PREFIX dan SUFFIX (dengan slow=True untuk kejelasan)
    print("\n1. Generating prefix and suffix (slow mode for clarity)...")
    create_audio_file("Nomor antrian", "prefix.mp3", slow=True)
    create_audio_file("silakan ke loket", "suffix.mp3", slow=True)
    
    # 2. Angka 0-20 (harus lengkap karena penyebutan khusus)
    print("\n2. Generating 0-20 (clear pronunciation)...")
    numbers_0_20 = [
        "nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", 
        "delapan", "sembilan", "sepuluh", "sebelas", "dua belas", 
        "tiga belas", "empat belas", "lima belas", "enam belas", 
        "tujuh belas", "delapan belas", "sembilan belas", "dua puluh"
    ]
    
    for i, text in enumerate(numbers_0_20):
        # Gunakan slow=True untuk angka agar lebih jelas
        create_audio_file(text, f"{i}.mp3", slow=True)
    
    # 3. Kelipatan 10 (30, 40, 50, ..., 90)
    print("\n3. Generating tens (30-90)...")
    tens = {
        30: "tiga puluh",
        40: "empat puluh",
        50: "lima puluh",
        60: "enam puluh",
        70: "tujuh puluh",
        80: "delapan puluh",
        90: "sembilan puluh"
    }
    
    for num, text in tens.items():
        create_audio_file(text, f"{num}.mp3", slow=True)
    
    # 4. Ratusan (100, 200, 300, ..., 900)
    print("\n4. Generating hundreds (100-900)...")
    hundreds = {
        100: "seratus",
        200: "dua ratus",
        300: "tiga ratus",
        400: "empat ratus",
        500: "lima ratus",
        600: "enam ratus",
        700: "tujuh ratus",
        800: "delapan ratus",
        900: "sembilan ratus"
    }
    
    for num, text in hundreds.items():
        create_audio_file(text, f"{num}.mp3", slow=True)
    
    # 5. Prefix huruf (A, B, C, dst)
    print("\n5. Generating letter prefixes...")
    letters = ['A', 'B', 'C', 'D', 'E', 'F']
    for letter in letters:
        create_audio_file(letter, f"letter_{letter}.mp3", slow=False)
    
    print("\n" + "="*60)
    print("AUDIO GENERATION COMPLETE!")
    print("="*60)
    print(f"\nTotal files created in '{AUDIO_DIR}/' directory")
    print("\nFiles generated:")
    print("- chime.mp3 (attention sound)")
    print("- prefix.mp3, suffix.mp3 (slow mode)")
    print("- 0.mp3 to 20.mp3 (21 files, slow mode)")
    print("- 30.mp3, 40.mp3, ..., 90.mp3 (7 files, slow mode)")
    print("- 100.mp3, 200.mp3, ..., 900.mp3 (9 files, slow mode)")
    print("- letter_A.mp3 to letter_F.mp3 (6 files)")
    print(f"\nTotal: ~46 files for support A001-F999")
    print("\nAudio improvements:")
    print("✓ Slow mode enabled for clarity")
    print("✓ Chime sound for attention")
    print("✓ Professional timing and pauses")

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════╗
    ║   AUDIO GENERATOR - SISTEM ANTRIAN                ║
    ║   Using gTTS (Google Text-to-Speech)              ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    # Check if gTTS is installed
    try:
        import gtts
    except ImportError:
        print("ERROR: gTTS not installed!")
        print("Please install: pip install gtts")
        exit(1)
    
    # Generate files
    generate_audio_files()
    
    print("\n✓ Done! You can now use audio_player.py to play queue numbers.")
