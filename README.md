# 🌋 Catania Latin Lovers - Auto Reel Bot

Questo bot automatizza il prelievo di video da un canale Telegram specifico (`phorig`), li processa (compressione 720p) e li pubblica come **Instagram Reels** sul profilo ufficiale di Catania Latin Lovers.

## 🚀 Come Funziona
1. **Trigger**: GitHub Actions avvia lo script ogni ora (`cron`).
2. **Download**: Lo script controlla gli ultimi 10 messaggi su Telegram alla ricerca di nuovi video.
3. **Processing**: FFmpeg comprime il video per ottimizzarlo agli standard di Instagram.
4. **Hosting**: Il video viene caricato temporaneamente su questo repository (pubblico).
5. **Publish**: Tramite le API Graph di Meta, il video viene inviato e pubblicato come Reel.

## 🛠 Setup & Requisiti

### 1. Secrets di GitHub
Per far funzionare il bot, devono essere impostati i seguenti **Actions Secrets** in `Settings > Secrets and variables > Actions`:


| Secret | Descrizione |
| :--- | :--- |
| `TG_API_ID` | API ID ottenuto da my.telegram.org |
| `TG_API_HASH` | API Hash ottenuto da my.telegram.org |
| `TG_SESSION` | String Session di Telethon (per evitare il login manuale) |
| `IG_BUSINESS_ID` | ID dell'account Instagram Business (non della pagina FB) |
| `IG_PAGE_TOKEN` | Access Token Permanente (System User o Long-Lived) |

### 2. File di Database
*   `pubblicati.txt`: Registro degli ID dei messaggi Telegram già postati per evitare duplicati.
*   `ready.mp4`: L'ultimo video elaborato pronto per il download da parte di Instagram.

## 📦 Tecnologie utilizzate
- **Python 3.9**
- **Telethon**: Per l'interazione con l'API di Telegram.
- **Requests**: Per le chiamate alle API Graph di Facebook/Instagram.
- **FFmpeg**: Per la manipolazione e compressione video.
- **GitHub Actions**: Per l'automazione e l'hosting temporaneo dei media.

## ⚠️ Note sulla Sicurezza
Il repository è **pubblico**, ma tutti i token e le sessioni sensibili sono gestiti tramite **GitHub Secrets**. Non includere mai token in chiaro nel file `main.py`.

---
*Sviluppato per Catania Latin Lovers 🌋*
