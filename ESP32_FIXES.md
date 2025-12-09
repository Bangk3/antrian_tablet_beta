# Perbaikan Kode ESP32 main.cpp

## 🐛 Bug Fixes yang Perlu Diterapkan

### 1. Fix mDNS Discovery (CRITICAL)

**Location:** Function `discoverServerByMDNS()`

**Replace this:**
```cpp
boolean discoverServerByMDNS() {
  Serial.println("[mDNS] Resolving hostname: " + String(mdns_hostname) + ".local");
  
  // Coba resolve hostname dengan timeout
  unsigned long startTime = millis();
  IPAddress serverIP;
  
  while (millis() - startTime < 5000) { // 5 detik timeout
    serverIP = MDNS.queryHost(mdns_hostname);
    
    if (serverIP.toString() != "0.0.0.0") {
      discovered_server_ip = serverIP.toString();
      Serial.print("[mDNS] Server found at: ");
      Serial.println(discovered_server_ip);
      return true;
    }
    
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("[mDNS] Timeout - Server not found");
  return false;
}
```

**With this:**
```cpp
boolean discoverServerByMDNS() {
  Serial.println("[mDNS] Resolving hostname: " + String(mdns_hostname) + ".local");
  
  // Initialize mDNS client first (PENTING!)
  if (!MDNS.begin("esp32-antrian-display")) {
    Serial.println("[mDNS] Failed to start mDNS client");
    return false;
  }
  
  // Query hostname dengan timeout
  unsigned long startTime = millis();
  IPAddress serverIP;
  
  while (millis() - startTime < 5000) { // 5 detik timeout
    serverIP = MDNS.queryHost(mdns_hostname);
    
    // Check jika IP valid (bukan 0.0.0.0)
    if (serverIP != IPAddress(0, 0, 0, 0)) {
      discovered_server_ip = serverIP.toString();
      Serial.print("[mDNS] Server found at: ");
      Serial.println(discovered_server_ip);
      return true;
    }
    
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("[mDNS] Timeout - Server not found");
  return false;
}
```

**Why:** `MDNS.queryHost()` tidak akan bekerja tanpa `MDNS.begin()` terlebih dahulu!

---

### 2. Fix UDP Response Validation (RECOMMENDED)

**Location:** Function `discoverServerByUDP()` - bagian parsing JSON

**Replace this:**
```cpp
if (!error && doc.containsKey("ip")) {
  discovered_server_ip = doc["ip"].as<String>();
  Serial.print("[UDP] Server IP extracted: ");
  Serial.println(discovered_server_ip);
  udp.stop();
  return true;
}
```

**With this:**
```cpp
if (!error) {
  // Validasi response dari antrian server (lebih aman)
  if (doc["type"] == "ANTRIAN_SERVER" && doc.containsKey("ip")) {
    discovered_server_ip = doc["ip"].as<String>();
    Serial.print("[UDP] Server IP extracted: ");
    Serial.println(discovered_server_ip);
    udp.stop();
    return true;
  } else {
    Serial.println("[UDP] Invalid response format");
  }
}
```

**Why:** Memastikan response benar-benar dari antrian server, bukan dari broadcast reply lain di network.

---

### 3. Fix WiFi Reconnection Loop (CRITICAL)

**Location:** Function `loop()`

**Replace entire loop() function with:**
```cpp
void loop() {
  if (wifiConnected) {
    webSocket.loop();
    
    // Periodic check WiFi status (setiap 5 detik)
    static unsigned long lastWiFiCheck = 0;
    unsigned long currentMillis = millis();
    
    if (currentMillis - lastWiFiCheck >= 5000) {
      lastWiFiCheck = currentMillis;
      
      if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[WiFi] Connection lost!");
        wifiConnected = false;
        wsConnected = false;
        displayMessage("WIFI ER");
      }
    }
  } else {
    // Reconnect WiFi dengan delay yang proper
    static unsigned long lastReconnectAttempt = 0;
    unsigned long currentMillis = millis();
    
    // Coba reconnect setiap 10 detik (bukan setiap loop!)
    if (currentMillis - lastReconnectAttempt >= 10000) {
      lastReconnectAttempt = currentMillis;
      
      Serial.println("[RECONNECT] Attempting to reconnect WiFi...");
      displayMessage("RECON");
      delay(1000);
      
      // Nonaktifkan timer sebelum reconnect
      timerAlarmDisable(timer);
      delay(100);
      
      connectWiFi();
      
      // Aktifkan timer kembali
      delay(100);
      timerAlarmEnable(timer);
      
      if (wifiConnected) {
        // Re-discover server setelah reconnect
        displayMessage("DISC..");
        
        if (discoverServerByMDNS()) {
          Serial.println("[DISCOVERY] mDNS Success after reconnect!");
          serverDiscovered = true;
        } else if (discoverServerByUDP()) {
          Serial.println("[DISCOVERY] UDP Success after reconnect!");
          serverDiscovered = true;
        } else {
          Serial.println("[DISCOVERY] All discovery methods failed!");
          displayMessage("NO SVR");
          serverDiscovered = false;
        }
        
        if (serverDiscovered) {
          connectWebSocket();
        }
      } else {
        displayMessage("NO WIFI");
      }
    }
  }
  
  // Delay kecil untuk stability
  delay(10);
}
```

**Why:** Mencegah ESP32 terus-menerus mencoba reconnect yang bisa bikin hang/unstable.

---

## ✅ Summary Perbaikan

| Issue | Severity | Impact | Status |
|-------|----------|--------|--------|
| mDNS tidak ada `MDNS.begin()` | 🔴 CRITICAL | mDNS tidak akan pernah bekerja | Must Fix |
| UDP response validation | 🟡 MEDIUM | Bisa dapat IP salah dari device lain | Should Fix |
| WiFi reconnect loop | 🔴 CRITICAL | ESP32 bisa hang/unstable | Must Fix |

---

## 🧪 Testing Checklist

Setelah apply fixes, test:

1. **mDNS Discovery:**
   ```
   [mDNS] Resolving hostname: antrian-server.local
   ......
   [mDNS] Server found at: 192.168.43.1
   ```

2. **UDP Fallback:**
   ```
   [mDNS] Timeout - Server not found
   [UDP] Starting broadcast discovery...
   [UDP] Broadcast attempt 1/3
   [UDP] Received reply: {"type":"ANTRIAN_SERVER","ip":"192.168.43.1",...}
   [UDP] Server found at: 192.168.43.1
   ```

3. **WiFi Reconnection:**
   - Matikan WiFi hotspot
   - ESP32 harus tampil "WIFI ER"
   - Nyalakan kembali hotspot
   - Setelah 10 detik, ESP32 akan coba reconnect
   - Display "RECON" → "DISC.." → "READY" atau nomor antrian

4. **Normal Operation:**
   - Tekan tombol PANGGIL di web interface
   - Nomor harus muncul di display P10
   - Serial log: `[DISPLAY] Updating to: 001`

---

## 📋 Compatibility Check

Kode ESP32 Anda sudah **95% compatible** dengan server Node.js yang baru!

Yang perlu:
- ✅ Port sama (8080, 9999) 
- ✅ Hostname sama (antrian-server)
- ✅ Message sama (ANTRIAN_DISCOVERY)
- ✅ JSON structure sama
- ❌ Need 3 bug fixes di atas

Setelah apply 3 fixes → **100% compatible!** 🎉
