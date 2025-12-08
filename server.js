const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// =====================================================
// KONFIGURASI SERVER
// =====================================================
const PORT = 8080;

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
    
    // Jalankan Python script untuk play audio
    // Audio sudah include: chime sound, slow mode gTTS, dan timing profesional
    exec(`python audio_player.py ${queueNumber}`, (error, stdout, stderr) => {
        if (error) {
            console.error('[AUDIO] Error:', error.message);
            console.error('[AUDIO] Make sure: 1) audio/ folder exists, 2) pygame installed');
            return;
        }
        if (stderr && stderr.trim() !== '') {
            console.error('[AUDIO] Stderr:', stderr);
        }
        if (stdout && stdout.trim() !== '') {
            console.log('[AUDIO] Output:', stdout.trim());
        }
    });
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
// START SERVER
// =====================================================
server.listen(PORT, () => {
    console.log('=====================================================');
    console.log('   SISTEM ANTRIAN - WEBSOCKET SERVER');
    console.log('=====================================================');
    console.log(`Server running on port ${PORT}`);
    console.log(`Web Interface: http://127.0.0.1:${PORT}`);
    console.log(`WebSocket URL: ws://127.0.0.1:${PORT}`);
    console.log('');
    console.log('CATATAN:');
    console.log('- Pastikan Tablet dalam mode Hotspot');
    console.log('- ESP32 connect ke: ws://[IP_HOTSPOT]:8080');
    console.log('- Browser access: http://127.0.0.1:8080');
    console.log('=====================================================');
});

// =====================================================
// GRACEFUL SHUTDOWN
// =====================================================
process.on('SIGINT', () => {
    console.log('\n[SHUTDOWN] Closing server...');
    wss.clients.forEach((client) => {
        client.close();
    });
    server.close(() => {
        console.log('[SHUTDOWN] Server closed');
        process.exit(0);
    });
});
