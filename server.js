const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const dgram = require('dgram');
const os = require('os');

// =====================================================
// KONFIGURASI SERVER
// =====================================================
const PORT = 8080;
const UDP_DISCOVERY_PORT = 9999;
const MDNS_HOSTNAME = 'antrian-server';

// =====================================================
// STATUS ANTRIAN (In-Memory State)
// =====================================================
let nextQueueNumber = 1;        // Nomor berikutnya untuk dicetak
let currentCalledNumber = null; // Nomor yang sedang dipanggil
const queuePrefix = '';         // Tanpa prefix huruf (001, 002, dst)

// =====================================================
// HTTP SERVER (untuk melayani Web Interface)
// =====================================================
const server = http.createServer((req, res) => {
    if (req.url === '/' || req.url === '/index.html') {
        fs.readFile(path.join(__dirname, 'index.html'), (err, data) => {
            if (err) {
                res.writeHead(500);
                res.end('Error loading index.html');
                return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
        });
    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

// =====================================================
// WEBSOCKET SERVER
// =====================================================
const wss = new WebSocket.Server({ server });

// Menyimpan referensi koneksi
let browserClient = null;
let esp32Client = null;

// =====================================================
// FUNGSI HELPER
// =====================================================

// Format nomor antrian dengan leading zeros (A001, A002, dst)
function formatQueueNumber(num) {
    return queuePrefix + String(num).padStart(3, '0');
}

// Kirim data ke ESP32
function sendToESP32(data) {
    if (esp32Client && esp32Client.readyState === WebSocket.OPEN) {
        esp32Client.send(JSON.stringify(data));
        console.log('[ESP32] Sent:', JSON.stringify(data));
        return true;
    } else {
        console.log('[ESP32] Not connected, cannot send data');
        return false;
    }
}

// Kirim status ke Browser
function sendStatusToBrowser() {
    if (browserClient && browserClient.readyState === WebSocket.OPEN) {
        const status = {
            type: 'status',
            nextQueue: formatQueueNumber(nextQueueNumber),
            currentCalled: currentCalledNumber || 'NONE',
            esp32Connected: esp32Client !== null && esp32Client.readyState === WebSocket.OPEN
        };
        browserClient.send(JSON.stringify(status));
        console.log('[BROWSER] Status sent:', JSON.stringify(status));
    }
}

// Putar suara (Text-to-Speech) - Menggunakan Python Script dengan audio yang ditingkatkan
function playAudio(queueNumber) {
    console.log(`[AUDIO] Playing: ${queueNumber}`);
    
    // Jalankan Python script untuk play audio (non-blocking untuk instant response)
    // Menggunakan spawn agar tidak blocking dan lebih cepat
    const audioProcess = spawn('python', ['audio_player.py', queueNumber], {
        detached: false,
        stdio: 'ignore'  // Ignore output untuk speed
    });
    
    audioProcess.on('error', (error) => {
        console.error('[AUDIO] Error:', error.message);
    });
    
    // Don't wait for process to finish - let it run in background
    audioProcess.unref();
}

// Cetak nomor antrian via Bluetooth
function printQueue(queueNumber) {
    console.log(`[PRINT] Printing queue number: ${queueNumber}`);
    
    // CATATAN: Untuk implementasi Bluetooth printing di Android/Termux:
    // 1. Install termux-api
    // 2. Gunakan library bluetooth seperti node-bluetooth atau custom script
    // 3. Kirim perintah ESC/POS ke printer thermal
    
    // Contoh perintah (uncomment dan sesuaikan jika di Android):
    // const { exec } = require('child_process');
    // exec(`./print-script.sh ${queueNumber}`, (error) => {
    //     if (error) console.error('[PRINT] Error:', error);
    // });
}

// =====================================================
// WEBSOCKET CONNECTION HANDLER
// =====================================================
wss.on('connection', (ws, req) => {
    const clientIP = req.socket.remoteAddress;
    console.log(`[CONNECTION] New client connected from: ${clientIP}`);

    // Identifikasi client (Browser lokal vs ESP32 remote)
    const isLocalhost = clientIP.includes('127.0.0.1') || clientIP.includes('::1') || clientIP.includes('::ffff:127.0.0.1');
    
    if (isLocalhost) {
        // Browser Client (dari localhost)
        browserClient = ws;
        console.log('[BROWSER] Browser client connected');
        sendStatusToBrowser(); // Kirim status awal
    } else {
        // ESP32 Client (dari IP hotspot)
        esp32Client = ws;
        console.log('[ESP32] ESP32 client connected');
        // Kirim status awal ke ESP32
        if (currentCalledNumber) {
            sendToESP32({ queue: currentCalledNumber });
        }
    }

    // =====================================================
    // MESSAGE HANDLER
    // =====================================================
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log(`[MESSAGE] Received from ${isLocalhost ? 'BROWSER' : 'ESP32'}:`, data);

            // Jika pesan dari Browser (Web Interface)
            if (isLocalhost && data.command) {
                handleBrowserCommand(data.command);
            }
            
            // Jika pesan dari ESP32 (status/acknowledgment)
            if (!isLocalhost) {
                console.log('[ESP32] Response:', data);
                sendStatusToBrowser(); // Update status di browser
            }

        } catch (err) {
            // Jika bukan JSON, anggap sebagai plain text
            console.log(`[MESSAGE] Plain text from ${isLocalhost ? 'BROWSER' : 'ESP32'}:`, message.toString());
        }
    });

    // =====================================================
    // DISCONNECT HANDLER
    // =====================================================
    ws.on('close', () => {
        console.log(`[DISCONNECT] Client disconnected: ${clientIP}`);
        if (ws === browserClient) {
            browserClient = null;
            console.log('[BROWSER] Browser client disconnected');
        }
        if (ws === esp32Client) {
            esp32Client = null;
            console.log('[ESP32] ESP32 client disconnected');
            sendStatusToBrowser(); // Update status di browser
        }
    });

    ws.on('error', (error) => {
        console.error('[ERROR] WebSocket error:', error);
    });
});

// =====================================================
// COMMAND HANDLER (dari Web Interface)
// =====================================================
function handleBrowserCommand(command) {
    console.log(`[COMMAND] Processing: ${command}`);

    switch (command) {
        case 'CALL':
            // Panggil nomor antrian berikutnya
            currentCalledNumber = formatQueueNumber(nextQueueNumber);
            
            console.log(`[CALL] Calling queue: ${currentCalledNumber}`);
            
            // 1. Putar audio
            playAudio(currentCalledNumber);
            
            // 2. Kirim ke ESP32
            sendToESP32({ queue: currentCalledNumber });
            
            // 3. Increment nomor antrian untuk panggilan selanjutnya
            nextQueueNumber++;
            
            // 4. Update status di browser
            sendStatusToBrowser();
            break;

        case 'RECALL':
            // Panggil ulang nomor yang terakhir dipanggil
            if (currentCalledNumber) {
                console.log(`[RECALL] Re-calling queue: ${currentCalledNumber}`);
                
                // 1. Putar audio ulang
                playAudio(currentCalledNumber);
                
                // 2. Kirim ulang ke ESP32
                sendToESP32({ queue: currentCalledNumber });
            } else {
                console.log('[RECALL] No queue to recall');
            }
            
            // 3. Update status di browser
            sendStatusToBrowser();
            break;

        case 'PRINT':
            // Cetak nomor antrian baru
            const queueToPrint = formatQueueNumber(nextQueueNumber);
            console.log(`[PRINT] Printing new queue: ${queueToPrint}`);
            
            // 1. Cetak via Bluetooth
            printQueue(queueToPrint);
            
            // 2. Increment nomor antrian
            nextQueueNumber++;
            
            // 3. Update status di browser
            sendStatusToBrowser();
            break;

        case 'RESET':
            // Reset sistem (optional - untuk debugging)
            console.log('[RESET] Resetting system');
            nextQueueNumber = 1;
            currentCalledNumber = null;
            sendStatusToBrowser();
            break;

        default:
            console.log(`[COMMAND] Unknown command: ${command}`);
    }
}

// =====================================================
// GET LOCAL IP ADDRESS
// =====================================================
function getLocalIP() {
    const interfaces = os.networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            // Skip internal (loopback) and non-IPv4 addresses
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    return '127.0.0.1';
}

// =====================================================
// mDNS SERVICE (via Avahi in Termux)
// =====================================================
function setupMDNS() {
    const localIP = getLocalIP();
    console.log('[mDNS] Setting up mDNS service...');
    
    // Di Termux, kita menggunakan avahi-daemon
    // Install: pkg install avahi
    // Service file akan dibuat di: $PREFIX/etc/avahi/services/
    
    const avahiServiceContent = `<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">Antrian Server on %h</name>
  <service>
    <type>_antrian._tcp</type>
    <port>${PORT}</port>
    <txt-record>path=/</txt-record>
  </service>
  <service>
    <type>_http._tcp</type>
    <port>${PORT}</port>
  </service>
</service-group>`;

    // Coba setup avahi service
    exec('which avahi-daemon', (error) => {
        if (error) {
            console.log('[mDNS] ⚠ Avahi not installed. Install with: pkg install avahi');
            console.log('[mDNS] ⚠ Using UDP Discovery only');
            return;
        }
        
        // Write avahi service file
        const serviceFile = '/data/data/com.termux/files/usr/etc/avahi/services/antrian.service';
        fs.writeFile(serviceFile, avahiServiceContent, (err) => {
            if (err) {
                console.log('[mDNS] ⚠ Could not write avahi service file:', err.message);
                console.log('[mDNS] ⚠ Using UDP Discovery only');
                return;
            }
            
            // Restart avahi daemon
            exec('sv restart avahi-daemon 2>/dev/null || true', (error) => {
                if (!error) {
                    console.log(`[mDNS] ✓ Service published: ${MDNS_HOSTNAME}.local`);
                    console.log(`[mDNS] ✓ ESP32 can connect to: ws://${MDNS_HOSTNAME}.local:${PORT}`);
                } else {
                    console.log('[mDNS] ⚠ Avahi daemon not running. Start with: sv-enable avahi-daemon && sv up avahi-daemon');
                }
            });
        });
    });
}

// =====================================================
// UDP DISCOVERY SERVER (Fallback)
// =====================================================
function setupUDPDiscovery() {
    const localIP = getLocalIP();
    const udpServer = dgram.createSocket('udp4');
    
    udpServer.on('error', (err) => {
        console.error(`[UDP] Server error: ${err.message}`);
        udpServer.close();
    });
    
    udpServer.on('message', (msg, rinfo) => {
        const message = msg.toString().trim();
        console.log(`[UDP] Discovery request from ${rinfo.address}:${rinfo.port} - "${message}"`);
        
        // Respond to discovery request
        if (message === 'ANTRIAN_DISCOVERY' || message === 'DISCOVER_ANTRIAN') {
            const response = JSON.stringify({
                type: 'ANTRIAN_SERVER',
                ip: localIP,
                port: PORT,
                hostname: MDNS_HOSTNAME,
                websocket: `ws://${localIP}:${PORT}`
            });
            
            udpServer.send(response, rinfo.port, rinfo.address, (err) => {
                if (err) {
                    console.error(`[UDP] Error sending response: ${err.message}`);
                } else {
                    console.log(`[UDP] ✓ Sent discovery response to ${rinfo.address}`);
                }
            });
        }
    });
    
    udpServer.on('listening', () => {
        const address = udpServer.address();
        console.log(`[UDP] ✓ Discovery server listening on port ${address.port}`);
        console.log(`[UDP] ✓ ESP32 can broadcast "ANTRIAN_DISCOVERY" to port ${address.port}`);
    });
    
    // Bind to UDP port
    udpServer.bind(UDP_DISCOVERY_PORT);
    
    return udpServer;
}

// =====================================================
// START SERVER
// =====================================================
let udpServer = null;

server.listen(PORT, () => {
    const localIP = getLocalIP();
    
    console.log('=====================================================');
    console.log('   SISTEM ANTRIAN - WEBSOCKET SERVER');
    console.log('=====================================================');
    console.log(`Server running on port ${PORT}`);
    console.log(`Local IP: ${localIP}`);
    console.log(`Web Interface: http://127.0.0.1:${PORT}`);
    console.log('');
    console.log('DISCOVERY METHODS:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    // Setup mDNS
    setupMDNS();
    
    // Setup UDP Discovery
    udpServer = setupUDPDiscovery();
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('');
    console.log('ESP32 CONNECTION OPTIONS:');
    console.log(`  1. mDNS: ws://${MDNS_HOSTNAME}.local:${PORT}`);
    console.log(`  2. Direct IP: ws://${localIP}:${PORT}`);
    console.log(`  3. UDP Discovery: Broadcast "ANTRIAN_DISCOVERY" to port ${UDP_DISCOVERY_PORT}`);
    console.log('');
    console.log('CATATAN:');
    console.log('- Pastikan Tablet dalam mode Hotspot');
    console.log('- ESP32 dan Tablet harus di network yang sama');
    console.log('- Browser access: http://127.0.0.1:8080');
    console.log('=====================================================');
});

// =====================================================
// GRACEFUL SHUTDOWN
// =====================================================
process.on('SIGINT', () => {
    console.log('\n[SHUTDOWN] Closing server...');
    
    // Close WebSocket clients
    wss.clients.forEach((client) => {
        client.close();
    });
    
    // Close UDP server
    if (udpServer) {
        udpServer.close();
    }
    
    // Close HTTP server
    server.close(() => {
        console.log('[SHUTDOWN] Server closed');
        process.exit(0);
    });
});
