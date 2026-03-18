# 🌋 Catania Latin Lovers | Reel Automator
[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org)
[![Automation](https://img.shields.io/github/workflow/status/dmnplv/cll-reel-bot/CI)](https://github.com/dmnplv/cll-reel-bot/actions)
[![License](https://img.shields.io/github/license/dmnplv/cll-reel-bot)](LICENSE)

> **L'automazione intelligente che connette la community latina di Catania.**  
> Preleva, elabora e pubblica i migliori momenti di Salsa e Bachata dai canali Telegram dei top videomaker siciliani direttamente su Instagram.

---

## 🛠 Tech Stack
[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org)
[![GitHub Actions](https://img.shields.io/github/workflow/status/dmnplv/cll-reel-bot/CI)](https://github.com/dmnplv/cll-reel-bot/actions)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://telegram.org)
[![Instagram](https://img.shields.io/badge/Instagram-API-purple?logo=instagram)](https://developers.facebook.com/docs/instagram)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-4.4-orange?logo=ffmpeg)](https://ffmpeg.org)

---

## 💡 Il Problema & La Soluzione
I contenuti video di alta qualità (200-500MB in formato `.mov`) sono difficili da gestire manualmente tra diverse piattaforme. 
Questo bot risolve il problema attraverso:
- **Cloud Processing:** Utilizzo di server GitHub per scaricare e processare file pesanti.
- **FFmpeg Encoding:** Compressione dinamica a **1080p (CRF 22)** per bilanciare qualità visiva e limiti API di Meta.
- **Relay Architecture:** Un sistema a "staffetta" che bypassa i blocchi di sicurezza degli hosting gratuiti sfruttando la velocità dei server GitHub.

## 🚀 Caratteristiche Principali
*   **Smart Source Rotation:** Logica di pubblicazione a "blocchi da 3" per mantenere l'estetica della griglia Instagram coerente per autore.
*   **Catania Geotagging:** Inserimento automatico della posizione geografica per massimizzare il reach locale.
*   **Auto-Cleanup Database:** Gestione efficiente degli ID pubblicati per evitare duplicati senza appesantire il repository.
*   **Never-Expiring Access:** Integrazione con token di lunga durata (Meta Graph API) per un'operatività 24/7 senza interventi manuali.

## 📡 Sorgenti & Partner
Il bot valorizza il lavoro dei creator locali taggandoli automaticamente:
- [@original.ph_](https://www.instagram.com) 🎥
- [@photo_goldsalsa](https://www.instagram.com) 📸
- [@bachata_social_sicilia](https://www.instagram.com) 🌴
- [@elegancia_latina_catania](https://www.instagram.com) ✨
- [@latin__chic](https://www.instagram.com) 🔥

## ⚙️ Configurazione
Il progetto è configurato tramite **GitHub Secrets** per proteggere le credenziali:
- `TG_SESSION`: String Session persistente per Telethon.
- `IG_PAGE_TOKEN`: Token di accesso "Never-Expire" (Page Access Token).
- `IG_BUSINESS_ID`: Instagram Business Account ID.

---
*Sviluppato per potenziare la scena caraibica catanese.*  
**Catania Latin Lovers** 🌋
