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
    """Generate file audio dari text menggunakan gTTS dengan kualitas natural dan konversi ke WAV"""
    try:
        # Gunakan normal speed untuk suara lebih natural
        tts = gTTS(text=text, lang=LANG, slow=False)
        
        # Generate MP3 temporary file
        mp3_filename = filename.replace('.mp3', '_temp.mp3')
        wav_filename = filename.replace('.mp3', '.wav')
        
        mp3_path = os.path.join(AUDIO_DIR, mp3_filename)
        wav_path = os.path.join(AUDIO_DIR, wav_filename)
        tmp_wav_path = os.path.join(AUDIO_DIR, f"_tmp_{wav_filename}")
        
        tts.save(mp3_path)
        
        # Convert to 48kHz stereo 24-bit signed PCM for professional humanis quality
        os.system(f'ffmpeg -y -loglevel quiet -i "{mp3_path}" -ar 48000 -ac 2 -c:a pcm_s24le -filter:a "volume=-3dB" "{tmp_wav_path}"')
        
        # Append 0.3s silence to avoid GTTS trimming/abrupt cutoff
        os.system(f'ffmpeg -y -loglevel quiet -i "{tmp_wav_path}" -f lavfi -t 0.3 -i anullsrc=channel_layout=stereo:sample_rate=48000 -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1[out]" -map "[out]" -c:a pcm_s24le "{wav_path}"')
        
        # Cleanup temporary files
        if os.path.exists(tmp_wav_path):
            os.remove(tmp_wav_path)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        
        print(f"✓ Created: {wav_filename} - '{text}'")
        return True
    except Exception as e:
        print(f"✗ Error creating {filename}: {e}")
        return False

def generate_chime_sound():
    """Convert chime.mp3 dari root folder ke WAV format dengan volume normalisasi"""
    chime_mp3_root = "chime.mp3"  # File di root folder
    chime_wav_path = os.path.join(AUDIO_DIR, "chime.wav")
    
    if os.path.exists(chime_wav_path):
        print(f"✓ Chime sound already exists: chime.wav")
        return True
    
    # Check if chime.mp3 exists in root
    if not os.path.exists(chime_mp3_root):
        print(f"✗ chime.mp3 not found in root folder")
        return False
    
    print("Converting chime.mp3 to WAV format (48kHz 24-bit) dengan volume normalisasi...")
    
    try:
        # Convert chime.mp3 to WAV dengan volume dikurangi agar seimbang dengan suara lain
        os.system(f'ffmpeg -y -loglevel quiet -i "{chime_mp3_root}" -ar 48000 -ac 2 -c:a pcm_s24le -filter:a "volume=-6dB" "{chime_wav_path}"')
        print(f"✓ Converted: chime.mp3 -> chime.wav (volume balanced)")
        return True
        
    except Exception as e:
        print(f"✗ Could not convert chime: {e}")
        return False

def generate_audio_files():
    """Generate semua file audio yang diperlukan"""
    
    # Hapus folder audio lama jika ada
    if os.path.exists(AUDIO_DIR):
        import shutil
        print(f"🗑️  Removing old audio files from {AUDIO_DIR}/...")
        shutil.rmtree(AUDIO_DIR)
        print(f"✓ Old audio files removed")
    
    # Buat folder audio baru
    os.makedirs(AUDIO_DIR)
    print(f"✓ Created fresh directory: {AUDIO_DIR}/")
    
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
    
    # 1. PREFIX dan SUFFIX (natural speed untuk lebih enak didengar)
    print("\n1. Generating prefix and suffix (natural voice)...")
    create_audio_file("Nomor antrian", "prefix.mp3")
    create_audio_file("silakan ke loket", "suffix.mp3")
    
    # 2. Angka 0-20 (harus lengkap karena penyebutan khusus)
    print("\n2. Generating 0-20 (natural pronunciation)...")
    numbers_0_20 = [
        "nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", 
        "delapan", "sembilan", "sepuluh", "sebelas", "dua belas", 
        "tiga belas", "empat belas", "lima belas", "enam belas", 
        "tujuh belas", "delapan belas", "sembilan belas", "dua puluh"
    ]
    
    for i, text in enumerate(numbers_0_20):
        create_audio_file(text, f"{i}.mp3")
    
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
        create_audio_file(text, f"{num}.mp3")
    
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
        create_audio_file(text, f"{num}.mp3")
    
    # 5. SKIP letter prefixes (tidak digunakan lagi - hanya angka)
    print("\n5. Letter prefixes skipped (number-only system)")
    
    print("\n" + "="*60)
    print("AUDIO GENERATION COMPLETE!")
    print("="*60)
    print(f"\nTotal files created in '{AUDIO_DIR}/' directory")
    print("\nFiles generated:")
    print("- chime.wav (ding-dong attention sound)")
    print("- prefix.wav, suffix.wav (natural voice)")
    print("- 0.wav to 20.wav (21 files)")
    print("- 30.wav, 40.wav, ..., 90.wav (7 files)")
    print("- 100.wav, 200.wav, ..., 900.wav (9 files)")
    print(f"\nTotal: ~40 WAV files for support 001-999 (number only)")
    print("\nAudio configuration:")
    print("✓ Format: WAV 48kHz stereo 24-bit PCM (Professional/Broadcast Quality)")
    print("✓ Volume: -3dB (optimal clarity)")
    print("✓ Natural humanis voice with Indonesian accent")
    print("✓ 0.3s silence appended (prevent abrupt cutoff)")
    print("✓ Custom chime from chime.mp3")
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
