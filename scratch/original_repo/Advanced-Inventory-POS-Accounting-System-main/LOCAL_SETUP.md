# 🏠 Local Network Hosting Guide (Dukaanka Dhexdiisa)

Haddii aad rabto in computers-ka iyo tablets-ka dukaankaaga ay hal meel ku xirmaan, raac hagahan:

---

## 🏗 Tillaabada 1: Hel Server-kaaga (Master PC)
Computer-ka aad rabto in xogtu ku kaydsanto ka dhig mid IP-kiisu uusan isbeddelin (Static IP).

1.  **Find the IP:**
    *   Open **Command Prompt (cmd)**.
    *   Type `ipconfig`.
    *   Look for **IPv4 Address** (e.g., `192.168.1.100`).
    
---

## 🔓 Tillaabada 2: Open Firewall (Windows)
Windows wuxuu xiraa "Ports" aan la aqoon. Waa inaad "Port 5000" furtaa:

1.  Search for **"Windows Defender Firewall with Advanced Security"**.
2.  Click **Inbound Rules** -> **New Rule**.
3.  Choose **Port** -> **TCP** -> Specific local ports: `5000`.
4.  **Allow the connection** -> **Finish**. (Magaca u bixi: `POS_SYSTEM`).

---

## 🚀 Tillaabada 3: Run the System
Hubi in Server-ku uu shaqaynayo:
```bash
python run.py
```

---

## 📱 Tillaabada 4: Connect from Tablets/Other PCs
Hadda, qof kasta oo ku jira isla Wi-Fi-ga ama shabakadda (Network-ka) wuxuu soo geli karaa nidaamka isagoo isticmaalaya IP-ga server-ka:

*   **URL:** `http://192.168.1.100:5000`

---

## 💡 Pro Tips for Local Hosting:
*   **Static IP:** Hubi in router-kaaga aad ka dhigtid IP-ga computer-ka "Static" si uusan maalin kasta isku beddelin.
*   **Auto-Start:** Waxaad u samayn kartaa "Shortcut" nidaamka markii computer-ka la shido inuu si toos ah u kaco.
*   **Backup:** Mar kasta ka qaado xogta (Database) "Backup" adigoo isticmaalaya MySQL Workbench.

**Hadda dukaankaagu wuxuu leeyahay nidaam isku xiran! 🛒🏪**
