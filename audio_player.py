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
import subprocess

AUDIO_DIR = "audio"

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

def play_with_sox(queue_str, letter, number, parts):
    """Play audio menggunakan sox (play command) - simple and fast"""
    try:
        # List semua file yang akan diputar
        files_to_play = []
        
        # 0. CHIME (attention sound)
        chime_path = get_audio_path("chime.wav")
        if os.path.exists(chime_path):
            files_to_play.append(chime_path)
        
        # 1. PREFIX
        prefix_path = get_audio_path("prefix.wav")
        if os.path.exists(prefix_path):
            files_to_play.append(prefix_path)
        
        # 2. LETTER (skip jika tidak ada)
        if letter:
            letter_path = get_audio_path(f"letter_{letter}.wav")
            if os.path.exists(letter_path):
                files_to_play.append(letter_path)
        
        # 3. NUMBER PARTS
        for part in parts:
            part_path = get_audio_path(f"{part}.wav")
            if os.path.exists(part_path):
                files_to_play.append(part_path)
        
        # 4. SUFFIX
        suffix_path = get_audio_path("suffix.wav")
        if os.path.exists(suffix_path):
            files_to_play.append(suffix_path)
        
        # Play all files in one command with sox/play
        # Using -q for quiet mode (no output)
        subprocess.run(['play', '-q'] + files_to_play, check=True, capture_output=True)
        return True
        
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
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
        return False
    
    # Get audio parts
    parts = number_to_audio_parts(number)
    
    # Play using sox
    return play_with_sox(queue_str, letter, number, parts)

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
    ║   AUDIO PLAYER - SISTEM ANTRIAN (SOX)            ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    print("Checking dependencies...")
    print("  Platform: Termux/Android")
    
    # Check sox/play
    try:
        subprocess.run(['play', '--version'], check=True, capture_output=True)
        print("  ✓ sox (play command) available")
    except FileNotFoundError:
        print("  ✗ sox not installed!")
        print("  Install with: pkg install sox")
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
        print("Usage: python audio_player.py 22")
        print("       python audio_player.py 156")
        print("="*60)
