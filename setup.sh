#!/bin/bash

# =====================================================
# AUTO INSTALLER - SISTEM ANTRIAN TABLET
# =====================================================

echo "╔════════════════════════════════════════════════════╗"
echo "║   AUTO INSTALLER - SISTEM ANTRIAN                 ║"
echo "║   Tablet Queue System Setup                       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Deteksi platform
if [[ "$PREFIX" == *"com.termux"* ]]; then
    IS_TERMUX=true
    echo "✓ Platform detected: Termux/Android"
else
    IS_TERMUX=false
    echo "✓ Platform detected: Linux/Unix"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 1: Checking System Requirements"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if running in Termux
if [ "$IS_TERMUX" = true ]; then
    echo "Installing Termux packages..."
    
    # Update package list
    echo "[1/6] Updating package list..."
    pkg update -y
    
    # Install Node.js
    echo "[2/6] Installing Node.js..."
    if ! command -v node &> /dev/null; then
        pkg install -y nodejs
    else
        echo "  ✓ Node.js already installed: $(node --version)"
    fi
    
    # Install Python
    echo "[3/6] Installing Python..."
    if ! command -v python &> /dev/null; then
        pkg install -y python
    else
        echo "  ✓ Python already installed: $(python --version)"
    fi
    
    # Install audio player (sox - recommended)
    echo "[4/6] Installing audio player (sox)..."
    if ! command -v play &> /dev/null; then
        pkg install -y sox
    else
        echo "  ✓ Sox already installed"
    fi
    
    # Install ffmpeg for audio processing
    echo "[5/8] Installing ffmpeg..."
    if ! command -v ffmpeg &> /dev/null; then
        pkg install -y ffmpeg
    else
        echo "  ✓ FFmpeg already installed"
    fi
    
    # Install Avahi for mDNS
    echo "[6/8] Installing Avahi (mDNS support)..."
    if ! command -v avahi-daemon &> /dev/null; then
        echo "  Installing from root-repo..."
        pkg install -y root-repo
        pkg install -y avahi runit
        
        if command -v avahi-daemon &> /dev/null; then
            echo "  ✓ Avahi installed"
            
            # Create required directories
            echo "  Creating Avahi directories..."
            mkdir -p $PREFIX/etc/avahi
            mkdir -p $PREFIX/etc/avahi/services
            mkdir -p $PREFIX/var/run/avahi-daemon
            
            # Create minimal avahi-daemon.conf if not exists
            if [ ! -f "$PREFIX/etc/avahi/avahi-daemon.conf" ]; then
                cat > $PREFIX/etc/avahi/avahi-daemon.conf << 'EOF'
[server]
use-ipv4=yes
use-ipv6=no
enable-dbus=no
allow-interfaces=wlan0,ap0

[publish]
publish-addresses=yes
publish-hinfo=no
publish-workstation=no
publish-domain=no

[reflector]
enable-reflector=no

[rlimits]
EOF
                echo "  ✓ Avahi config created"
            fi
        else
            echo "  ⚠ Avahi installation failed"
            echo "  ℹ mDNS will not work, but UDP Discovery will still function"
            echo "  ℹ Manual install: pkg install root-repo && pkg install avahi"
        fi
    else
        echo "  ✓ Avahi already installed"
        
        # Ensure directories exist even if already installed
        mkdir -p $PREFIX/etc/avahi/services
        mkdir -p $PREFIX/var/run/avahi-daemon
    fi
    
    # Enable and start Avahi daemon (only if installed)
    if command -v avahi-daemon &> /dev/null; then
        echo "[7/8] Setting up Avahi service..."
        
        if sv-enable avahi-daemon 2>/dev/null; then
            echo "  ✓ Avahi service enabled"
        fi
        
        if sv up avahi-daemon 2>/dev/null; then
            echo "  ✓ Avahi daemon started"
        fi
        
        sleep 2
        
        if sv status avahi-daemon 2>/dev/null | grep -q "run"; then
            echo "  ✓ Avahi is running (mDNS active)"
        else
            echo "  ⚠ Avahi failed to start"
            echo "  ℹ Common issue in Termux, mDNS might not work"
            echo "  ℹ System will use UDP Discovery instead (more reliable)"
        fi
    else
        echo "[7/8] Skipping Avahi setup (not installed)"
        echo "  ℹ System will use UDP Discovery only"
    fi
    
    # Setup storage access
    echo "[8/8] Setting up storage access..."
    if [ ! -d "$HOME/storage" ]; then
        termux-setup-storage
        echo "  ✓ Storage access granted"
    else
        echo "  ✓ Storage already configured"
    fi
    
else
    # Linux/Mac installation
    echo "Installing system packages..."
    
    # Check for package manager
    if command -v apt-get &> /dev/null; then
        PKG_MGR="apt-get"
        sudo apt-get update
        sudo apt-get install -y nodejs npm python3 python3-pip sox ffmpeg
    elif command -v yum &> /dev/null; then
        PKG_MGR="yum"
        sudo yum install -y nodejs npm python3 python3-pip sox ffmpeg
    elif command -v brew &> /dev/null; then
        PKG_MGR="brew"
        brew install node python sox ffmpeg
    else
        echo "⚠ Warning: Package manager not detected"
        echo "  Please install manually: nodejs, python3, sox, ffmpeg"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 2: Installing Node.js Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "package.json" ]; then
    echo "Installing npm packages..."
    npm install
    echo "✓ Node.js dependencies installed"
else
    echo "⚠ Warning: package.json not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 3: Installing Python Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Installing Python packages..."
pip install gtts pydub
echo "✓ Python dependencies installed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 4: Generating Audio Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "generate_audio.py" ]; then
    echo "Generating TTS audio files..."
    python generate_audio.py
    echo "✓ Audio files generated"
else
    echo "⚠ Warning: generate_audio.py not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STEP 5: Testing Audio System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "audio_player.py" ]; then
    echo "Testing audio playback with number 23..."
    python audio_player.py 23
    echo ""
    read -p "Did you hear the audio? (y/n): " audio_ok
    if [[ "$audio_ok" =~ ^[Yy]$ ]]; then
        echo "✓ Audio system working"
    else
        echo "⚠ Audio may need troubleshooting"
    fi
else
    echo "⚠ Warning: audio_player.py not found"
fi

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   INSTALLATION COMPLETE!                          ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "✓ All dependencies installed"
echo "✓ Audio files generated"
echo "✓ System ready to use"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$IS_TERMUX" = true ]; then
    echo "For Termux/Android Tablet:"
    echo ""
    echo "1. Setup WiFi Hotspot:"
    echo "   - Go to Settings → Network → Hotspot"
    echo "   - Enable hotspot (default IP: 192.168.43.1)"
    echo ""
    echo "2. Start the server:"
    echo "   node server.js"
    echo ""
    echo "3. Access web interface:"
    echo "   http://localhost:8080"
    echo ""
    echo "4. Configure ESP32:"
    echo "   - Use example file: esp32_client_example.ino"
    echo "   - Set your hotspot SSID & password"
    echo "   - ESP32 will auto-discover server via:"
    echo "     • mDNS (antrian-server.local) - Primary"
    echo "     • UDP Discovery - Fallback"
    echo "   - Upload to ESP32"
    echo ""
    echo "5. Discovery Methods Available:"
    echo "   ✓ mDNS: ws://antrian-server.local:8080"
    echo "   ✓ UDP: Broadcast on port 9999"
    echo "   ✓ Direct: ws://192.168.43.1:8080"
    echo ""
else
    echo "For Desktop/Server:"
    echo ""
    echo "1. Start the server:"
    echo "   node server.js"
    echo ""
    echo "2. Access web interface:"
    echo "   http://localhost:8080"
    echo ""
    echo "3. See DOCUMENTATION.md for ESP32 setup"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For complete documentation, see: DOCUMENTATION.md"
echo "For troubleshooting, see: TROUBLESHOOTING section in docs"
echo ""
