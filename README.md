# 🌋 Catania Latin Lovers - Reel Automator

Questo progetto è un sistema di automazione intelligente che preleva i migliori video di Salsa e Bachata dai canali Telegram dei principali videomaker siciliani e li pubblica come **Reels in Alta Qualità (1080p)** sul profilo Instagram di **Catania Latin Lovers**.

## 🚀 Come Funziona
Il sistema opera in modalità **"Staffetta"** tramite GitHub Actions per garantire la massima stabilità:
1.  **Giro A (Preparazione):** Il bot scansiona le sorgenti Telegram, sceglie il video più recente, lo comprime in HD (1080p) e lo carica nel repository.
2.  **Giro B (Pubblicazione):** Al turno successivo, il video caricato viene inviato alle API di Instagram con i relativi crediti (tag) del videomaker e Geotag di Catania.

## 🛠 Caratteristiche Tecniche
- **HQ Video Processing:** Utilizza `FFmpeg` con parametri `CRF 22` per mantenere una qualità visiva eccellente sotto i 100MB.
- **Smart Rotation:** Logica di pubblicazione a "blocchi da 3" per mantenere l'estetica della griglia Instagram ordinata per autore.
- **Auto-Cleanup:** Il database `pubblicati.txt` si auto-pulisce mantenendo solo gli ultimi 100 ID per non appesantire il repository.
- **Geotagging:** Ogni post viene localizzato automaticamente a Catania per massimizzare la visibilità locale.

## 📡 Sorgenti Monitorate
Il bot monitora costantemente i seguenti creator:
- [@original.ph_](https://www.instagram.com)
- [@photo_goldsalsa](https://www.instagram.com)
- [@bachata_social_sicilia](https://www.instagram.com)
- [@elegancia_latina_catania](https://www.instagram.com)
- [@latin__chic](https://www.instagram.com)

## ⏰ Programmazione Post
L'automazione scatta **6 volte al giorno** per garantire una copertura costante negli orari di maggior traffico (Mattina, Pausa Pranzo, Prime Time).

## 🔒 Requisiti & Secrets
Per funzionare, il progetto richiede i seguenti **GitHub Secrets**:
- `TG_API_ID` / `TG_API_HASH`: Credenziali Telegram API.
- `TG_SESSION`: String Session di Telethon (generata via script).
- `IG_BUSINESS_ID`: ID dell'account Instagram Business.
- `IG_PAGE_TOKEN`: Token di accesso alla pagina Facebook (con scadenza "Never").

---
*Creato con ❤️ per la community latina di Catania.*
