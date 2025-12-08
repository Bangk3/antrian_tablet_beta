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

# Import for chime generation
try:
    from pydub import AudioSegment
    from pydub.generators import Sine
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

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

def generate_chime_sound():
    """Generate professional ding-dong chime untuk sistem antrian"""
    chime_path = os.path.join(AUDIO_DIR, "chime.mp3")
    
    if os.path.exists(chime_path):
        print(f"✓ Chime sound already exists: chime.mp3")
        return True
    
    print("Generating professional chime sound (ding-dong)...")
    
    try:
        from pydub.generators import Sine
        
        # DING - Nada tinggi (800 Hz)
        ding = Sine(800).to_audio_segment(duration=200)
        ding = ding.fade_in(20).fade_out(50)
        
        # Pause
        pause = AudioSegment.silent(duration=100)
        
        # DONG - Nada rendah (600 Hz)
        dong = Sine(600).to_audio_segment(duration=250)
        dong = dong.fade_in(20).fade_out(80)
        
        # Combine
        chime = ding + pause + dong
        chime = chime + 3  # +3 dB volume
        
        # Export
        chime.export(chime_path, format="mp3")
        print(f"✓ Created: chime.mp3 (professional ding-dong)")
        return True
        
    except Exception as e:
        print(f"✗ Could not generate chime: {e}")
        print(f"  Alternative: Run 'python generate_chime.py' for more options")
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
    print("\n0. Generating chime sound...")
    if PYDUB_AVAILABLE:
        generate_chime_sound()
    else:
        print("✗ pydub not available, skipping chime generation")
        print("  Install with: pip install pydub")
        print("  Or run: python generate_chime.py")
    
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
    
    # 5. SKIP letter prefixes (tidak digunakan lagi - hanya angka)
    print("\n5. Letter prefixes skipped (number-only system)")
    
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
    print(f"\nTotal: ~40 files for support 001-999 (number only)")
    print("\nAudio improvements:")
    print("✓ Slow mode enabled for clarity")
    print("✓ Chime sound for attention")
    print("✓ Professional timing and pauses")
    print("✓ Number-only system (no letter prefix)")

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
