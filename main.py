import os, requests, time, asyncio, subprocess
from datetime import datetime, timedelta, timezone
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# --- CONFIGURAZIONE E PULIZIA DATI ---
def c(v): return str(v or "").strip().replace('*', '').replace(' ', '')

# Caricamento credenziali dai Secret di GitHub
API_ID = int(c(os.getenv('TG_API_ID')) or 0)
API_HASH = c(os.getenv('TG_API_HASH'))
SESSION_STR = c(os.getenv('TG_SESSION'))
IG_ID = c(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = c(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY')

# Mappa Sorgente Telegram -> Tag Instagram per i crediti
SOURCES = {
    'phorig': 'original.ph_',
    'photogoldct': 'photo_goldsalsa',
    -1002422907785: 'elegancia_latina_catania',
    -1003220769402: 'latin__chic'
}

DAYS_LIMIT = 30  # Ignora i video più vecchi di un mese

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    # --- CARICAMENTO DATABASE LOCALE ---
    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: 
        gia_postati = [line.strip() for line in f.read().splitlines() if line.strip()]

    limit_date = datetime.now(timezone.utc) - timedelta(days=DAYS_LIMIT)

    # --- FASE 1: PUBBLICAZIONE REEL (Logica Staffetta) ---
    # Se lo script trova un video pronto dal giro precedente, lo invia a Instagram
    if os.path.exists('ready.mp4'):
        caption = "Catania Latin Lovers 🌋"
        if os.path.exists('caption.txt'):
            with open('caption.txt', 'r', encoding='utf-8') as f: caption = f.read()

        video_url = f"https://raw.githubusercontent.com/{REPO}/main/ready.mp4"
        print(f"🚀 [IG] Tentativo pubblicazione Reel: {video_url}")
        
        target_url = f"https://graph.facebook.com/{IG_ID}/media"
        r = requests.post(target_url, data={
            'media_type': 'REELS', 'video_url': video_url, 
            'caption': caption, 'access_token': IG_TOKEN
        }).json()
        
        if 'id' in r:
            print(f"✅ [IG] Container creato. Attesa elaborazione (90s)...")
            time.sleep(90)
            publish_res = requests.post(f"https://graph.facebook.com/{IG_ID}/media_publish", 
                                        data={'creation_id': r['id'], 'access_token': IG_TOKEN}).json()
            if 'id' in publish_res:
                print(f"🔥 [IG] REEL PUBBLICATO CON SUCCESSO! ID: {publish_res['id']}")
            # Pulizia file temporanei
            for f_rem in ['ready.mp4', 'caption.txt']:
                if os.path.exists(f_rem): os.remove(f_rem)

    # --- FASE 2: SCELTA STRATEGICA NUOVO VIDEO (Blocchi da 3) ---
    last_source_str = None
    count_consecutive = 0
    if gia_postati:
        # Analizziamo gli ultimi post per vedere se dobbiamo finire il blocco da 3 dello stesso autore
        for full_id in reversed(gia_postati):
            s_name = full_id.rsplit('_', 1)[0]
            if last_source_str is None:
                last_source_str = s_name
                count_consecutive = 1
            elif s_name == last_source_str:
                count_consecutive += 1
            else: break
    
    print(f"📊 [LOG] Ultimo autore: {last_source_str} (Post consecutivi: {count_consecutive})")

    winner = None
    # Sotto-fase A: Prova a completare il blocco da 3 con lo stesso autore
    if last_source_str and count_consecutive < 3:
        target = int(last_source_str) if last_source_str.replace('-','').isdigit() else last_source_str
        async for m in client.iter_messages(target, limit=15):
            m_id = f"{last_source_str}_{m.id}"
            if m.video and m_id not in gia_postati and m.date > limit_date and (m.video.duration or 0) > 5:
                winner = {'msg': m, 'tag': SOURCES.get(target, 'catanialatinlovers'), 'id': m_id}
                break

    # Sotto-fase B: Se il blocco è finito o l'autore è "fermo", cerca il video più nuovo in assoluto
    if not winner:
        all_candidates = []
        for src, tag in SOURCES.items():
            try:
                async for m in client.iter_messages(src, limit=15):
                    m_id = f"{src}_{m.id}"
                    if m.video and m_id not in gia_postati and m.date > limit_date and (m.video.duration or 0) > 5:
                        all_candidates.append({'date': m.date, 'msg': m, 'tag': tag, 'id': m_id})
                        break 
            except: continue
        
        if all_candidates:
            all_candidates.sort(key=lambda x: x['date'], reverse=True)
            winner = all_candidates[0]

    # --- FASE 3: PREPARAZIONE VIDEO (Compressione HQ) ---
    if winner:
        print(f"🎬 [TG] Preparazione video di @{winner['tag']} (Data: {winner['date']})")
        raw_path = await winner['msg'].download_media()
        
        # Compressione Full HD 1080p ottimizzata
        subprocess.run([
            'ffmpeg', '-i', raw_path, 
            '-vf', 'scale=-2:1080', 
            '-vcodec', 'libx264', '-crf', '22', '-preset', 'faster', 
            '-acodec', 'aac', '-b:a', '192k', '-y', 'ready.mp4'
        ])
        
        # Generazione della didascalia strategica
        new_caption = (
            f"L'energia di Catania in un Reel! 🌋💃\n\n"
            f"🎥 Video by @{winner['tag']}\n\n"
            f"Segui @catanialatinlovers per le migliori serate di Salsa e Bachata in Sicilia! 🕺✨\n\n"
            f"#CataniaLatinLovers #SalsaCatania #BachataCatania #SocialDance"
        )
        
        # Aggiornamento Database (mantieni solo gli ultimi 100 ID)
        gia_postati.append(winner['id'])
        with open('pubblicati.txt', 'w') as f:
            f.write("\n".join(gia_postati[-100:]))
        with open('caption.txt', 'w', encoding='utf-8') as f:
            f.write(new_caption)
        
        if os.path.exists(raw_path): os.remove(raw_path)
        print(f"✅ [OK] Video pronto per il prossimo invio.")
    else:
        print("ℹ️ [INFO] Nessun nuovo contenuto trovato.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
