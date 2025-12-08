"""
=====================================================
AUDIO PLAYER - SISTEM ANTRIAN
=====================================================

Module untuk memutar nomor antrian dengan menggabungkan
file audio yang sudah di-generate.

Contoh:
- A22  = letter_A.mp3 + 20.mp3 + 2.mp3
- B156 = letter_B.mp3 + 100.mp3 + 50.mp3 + 6.mp3
- C7   = letter_C.mp3 + 7.mp3
"""

import os
import sys
import re
import time

# Import conditional berdasarkan platform
try:
    from pydub import AudioSegment
    import tempfile
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Fallback: gunakan pygame untuk Windows
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

AUDIO_DIR = "audio"
TEMP_OUTPUT = os.path.join(AUDIO_DIR, "temp_combined.mp3")

def parse_queue_number(queue_str):
    """
    Parse nomor antrian (misal: 12, 22, 156, A22, dll)
    Return: (letter, number)
    """
    # Remove whitespace
    queue_str = str(queue_str).strip()
    
    # Coba parse dengan huruf (backward compatibility) atau tanpa huruf
    match = re.match(r'^([A-Z])?(\d+)$', queue_str.upper())
    if match:
        letter = match.group(1) if match.group(1) else None
        number = int(match.group(2))
        return letter, number
    
    # Fallback: coba parse sebagai angka murni
    try:
        number = int(queue_str)
        return None, number
    except ValueError:
        return None, None

def number_to_audio_parts(number):
    """
    Pecah angka menjadi parts untuk audio files
    
    Examples:
    - 7   -> [7]
    - 22  -> [20, 2]
    - 156 -> [100, 50, 6]
    - 300 -> [300]
    - 315 -> [300, 15]
    """
    parts = []
    
    # Handle 0
    if number == 0:
        return [0]
    
    # Ratusan
    hundreds = (number // 100) * 100
    if hundreds > 0:
        parts.append(hundreds)
    
    # Sisanya
    remainder = number % 100
    
    # 1-20: langsung
    if remainder <= 20:
        if remainder > 0:
            parts.append(remainder)
    else:
        # 21-99: pecah jadi puluhan + satuan
        tens = (remainder // 10) * 10
        ones = remainder % 10
        
        if tens > 0:
            parts.append(tens)
        if ones > 0:
            parts.append(ones)
    
    return parts

def get_audio_path(filename):
    """Get full path to audio file"""
    return os.path.join(AUDIO_DIR, filename)

def play_with_pydub(queue_str, letter, number, parts):
    """Play audio menggunakan pydub dengan timing profesional"""
    try:
        combined = AudioSegment.empty()
        
        # 0. CHIME (attention sound)
        chime_path = get_audio_path("chime.mp3")
        if os.path.exists(chime_path):
            combined += AudioSegment.from_mp3(chime_path)
            combined += AudioSegment.silent(duration=500)  # 500ms pause after chime
        
        # 1. PREFIX
        prefix_path = get_audio_path("prefix.mp3")
        if os.path.exists(prefix_path):
            combined += AudioSegment.from_mp3(prefix_path)
            combined += AudioSegment.silent(duration=300)  # 300ms pause
        
        # 2. LETTER (skip jika tidak ada)
        if letter:
            letter_path = get_audio_path(f"letter_{letter}.mp3")
            if os.path.exists(letter_path):
                combined += AudioSegment.from_mp3(letter_path)
                combined += AudioSegment.silent(duration=200)  # 200ms pause
        
        # 3. NUMBER PARTS
        for i, part in enumerate(parts):
            part_path = get_audio_path(f"{part}.mp3")
            if os.path.exists(part_path):
                combined += AudioSegment.from_mp3(part_path)
                # Pause lebih pendek antar digit, lebih lama di akhir
                if i < len(parts) - 1:
                    combined += AudioSegment.silent(duration=150)  # 150ms between numbers
                else:
                    combined += AudioSegment.silent(duration=300)  # 300ms before suffix
        
        # 4. SUFFIX
        suffix_path = get_audio_path("suffix.mp3")
        if os.path.exists(suffix_path):
            combined += AudioSegment.from_mp3(suffix_path)
        
        # Export ke file temporary di folder audio (bukan temp Windows)
        print(f"  Saving combined audio to: {TEMP_OUTPUT}")
        combined.export(TEMP_OUTPUT, format="mp3")
        
        # Play menggunakan pygame
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
            pygame.mixer.music.load(TEMP_OUTPUT)
            pygame.mixer.music.play()
            
            # Wait sampai selesai
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.quit()
            print(f"  ✓ Finished playing {queue_str}")
        else:
            # Fallback: buka dengan default media player
            print(f"  ✓ Audio saved to {TEMP_OUTPUT}")
            print(f"  Playing with default media player...")
            os.startfile(TEMP_OUTPUT)  # Windows only
        
        return True
        
    except Exception as e:
        print(f"Error with pydub: {e}")
        return False

def play_sequential(queue_str, letter, number, parts):
    """Play audio secara sequential (satu per satu) dengan timing profesional"""
    if not PYGAME_AVAILABLE:
        print("Error: pygame not installed for sequential playback")
        print("Install: pip install pygame")
        return False
    
    try:
        pygame.mixer.init()
        
        # List semua file yang akan diputar dengan pause duration
        files_to_play = []
        
        # 0. CHIME (attention sound) - pause lebih lama setelahnya
        chime_path = get_audio_path("chime.mp3")
        if os.path.exists(chime_path):
            files_to_play.append((chime_path, 0.5))  # 500ms pause after chime
        
        # 1. PREFIX - pause sedang setelahnya
        prefix_path = get_audio_path("prefix.mp3")
        if os.path.exists(prefix_path):
            files_to_play.append((prefix_path, 0.3))  # 300ms pause
        
        # 2. LETTER - pause pendek (skip jika tidak ada huruf)
        if letter:
            letter_path = get_audio_path(f"letter_{letter}.mp3")
            if os.path.exists(letter_path):
                files_to_play.append((letter_path, 0.2))  # 200ms pause
        
        # 3. NUMBER PARTS - pause minimal antar angka
        for i, part in enumerate(parts):
            part_path = get_audio_path(f"{part}.mp3")
            if os.path.exists(part_path):
                # Pause lebih pendek antar digit, lebih lama di akhir
                pause = 0.15 if i < len(parts) - 1 else 0.3
                files_to_play.append((part_path, pause))
        
        # 4. SUFFIX - no pause after (end)
        suffix_path = get_audio_path("suffix.mp3")
        if os.path.exists(suffix_path):
            files_to_play.append((suffix_path, 0))
        
        # Play satu per satu dengan timing profesional
        print(f"  Playing {len(files_to_play)} audio segments with professional timing...")
        for i, (filepath, pause_duration) in enumerate(files_to_play):
            filename = os.path.basename(filepath)
            print(f"  [{i+1}/{len(files_to_play)}] {filename}")
            
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            
            # Wait sampai selesai
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            
            # Pause sesuai timing yang ditentukan
            if pause_duration > 0:
                time.sleep(pause_duration)
        
        pygame.mixer.quit()
        print(f"  ✓ Finished playing {queue_str}")
        return True
        
    except Exception as e:
        print(f"Error with sequential play: {e}")
        return False

def play_queue_number(queue_str):
    """
    Play audio untuk nomor antrian
    
    Args:
        queue_str: Nomor antrian (misal: "22", "156", atau "A22")
    
    Returns:
        bool: True jika berhasil, False jika error
    """
    
    # Parse queue number
    letter, number = parse_queue_number(queue_str)
    
    if number is None:
        print(f"Error: Invalid queue format '{queue_str}'")
        return False
    
    if letter:
        print(f"\nPlaying: {queue_str} (Letter: {letter}, Number: {number})")
    else:
        print(f"\nPlaying: {queue_str} (Number: {number})")
    
    # Get audio parts
    parts = number_to_audio_parts(number)
    print(f"  Audio parts: {parts}")
    
    # Try pydub method first (combine then play)
    if PYDUB_AVAILABLE:
        print(f"  Method: pydub (combine audio)")
        return play_with_pydub(queue_str, letter, number, parts)
    
    # Fallback: sequential playback
    elif PYGAME_AVAILABLE:
        print(f"  Method: pygame (sequential)")
        return play_sequential(queue_str, letter, number, parts)
    
    else:
        print("Error: No audio library available!")
        print("Install either:")
        print("  - pip install pydub pygame")
        print("  - pip install pygame (simpler)")
        return False

def test_audio_system():
    """Test beberapa nomor antrian"""
    print("\n" + "="*60)
    print("TESTING AUDIO SYSTEM")
    print("="*60)
    
    test_numbers = ["1", "7", "15", "22", "100", "156", "300", "999"]
    
    for queue in test_numbers:
        print(f"\nTest: {queue}")
        letter, num = parse_queue_number(queue)
        parts = number_to_audio_parts(num)
        print(f"  Number: {num}")
        print(f"  Audio parts: {parts}")
        files = [f'{p}.mp3' for p in parts]
        if letter:
            print(f"  Files needed: letter_{letter}.mp3, {', '.join(files)}")
        else:
            print(f"  Files needed: {', '.join(files)}")

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════╗
    ║   AUDIO PLAYER - SISTEM ANTRIAN                   ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    print("Checking dependencies...")
    if PYDUB_AVAILABLE:
        print("  ✓ pydub available")
    else:
        print("  ✗ pydub not available")
    
    if PYGAME_AVAILABLE:
        print("  ✓ pygame available")
    else:
        print("  ✗ pygame not available")
    
    if not PYDUB_AVAILABLE and not PYGAME_AVAILABLE:
        print("\nERROR: No audio library installed!")
        print("Please install at least one:")
        print("  pip install pygame           (Recommended for Windows)")
        print("  pip install pydub            (Alternative)")
        exit(1)
    
    # Check if audio files exist
    if not os.path.exists(AUDIO_DIR):
        print(f"\nERROR: Audio directory '{AUDIO_DIR}/' not found!")
        print("Please run 'python generate_audio.py' first")
        exit(1)
    
    print()
    
    # Run test or play specific number
    if len(sys.argv) > 1:
        queue_number = sys.argv[1].upper()
        success = play_queue_number(queue_number)
        exit(0 if success else 1)
    else:
        # Show test
        test_audio_system()
        print("\n" + "="*60)
        print("Usage: python audio_player.py A22")
        print("       python audio_player.py B156")
        print("="*60)
