import os, requests, time, asyncio, subprocess
from datetime import datetime, timedelta, timezone
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# --- UTILITY ---
def c(v): return str(v or "").strip().replace('*', '').replace(' ', '')

# --- CONFIGURAZIONE ---
API_ID = int(c(os.getenv('TG_API_ID')) or 0)
API_HASH = c(os.getenv('TG_API_HASH'))
SESSION_STR = c(os.getenv('TG_SESSION'))
IG_ID = c(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = c(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY')

# ID Geografico di Catania per Instagram
CATANIA_LOCATION_ID = "115421711794270"

SOURCES = {
    'phorig': 'original.ph_',
    'photogoldct': 'photo_goldsalsa',
    -1002422907785: 'elegancia_latina_catania',
    -1003220769402: 'latin__chic'
}

DAYS_LIMIT = 30 

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    # Caricamento Database
    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: 
        gia_postati = [line.strip() for line in f.read().splitlines() if line.strip()]

    limit_date = datetime.now(timezone.utc) - timedelta(days=DAYS_LIMIT)

    # --- FASE 1: PUBBLICAZIONE REEL PRECEDENTE ---
    if os.path.exists('ready.mp4'):
        caption = "Catania Latin Lovers 🌋"
        if os.path.exists('caption.txt'):
            with open('caption.txt', 'r', encoding='utf-8') as f: caption = f.read()

        # AGGIUNTO SLASH / dopo githubusercontent.com
        video_url = f"https://raw.githubusercontent.com/{REPO}/main/ready.mp4"
        print(f"🚀 [IG] Pubblicazione Reel con Geotag Catania: {video_url}")
        
        # AGGIUNTO SLASH / v21.0 / prima di IG_ID
        target_url = f"https://graph.facebook.com/{IG_ID}/media"
        r = requests.post(target_url, data={
            'media_type': 'REELS', 
            'video_url': video_url, 
            'caption': caption, 
            'location_id': CATANIA_LOCATION_ID,
            'access_token': IG_TOKEN
        }).json()
        
        if 'id' in r:
            print(f"✅ [IG] Container: {r['id']}. Attesa 90s...")
            time.sleep(90)
            publish_url = f"https://graph.facebook.com/{IG_ID}/media_publish"
            res = requests.post(publish_url, data={'creation_id': r['id'], 'access_token': IG_TOKEN}).json()
            
            if 'id' in res:
                print("🔥 [IG] REEL PUBBLICATO!")
                os.remove('ready.mp4')
                if os.path.exists('caption.txt'): os.remove('caption.txt')
            else:
                print(f"❌ [IG] Errore finale: {res}")
        else:
            print(f"❌ [IG] Errore container: {r}")
            if "already" in str(r).lower() or "100" in str(r):
                print("⚠️ [IG] Reset file locale.")
                if os.path.exists('ready.mp4'): os.remove('ready.mp4')

    # --- FASE 2: SCELTA NUOVO VIDEO (LOGICA BLOCCHI DA 3) ---
    last_source_str, count_consecutive = None, 0
    if gia_postati:
        for full_id in reversed(gia_postati):
            if "_" in full_id:
                parts = full_id.rsplit('_', 1)
                s_name = parts[0]
                if last_source_str is None:
                    last_source_str = s_name
                    count_consecutive = 1
                elif s_name == last_source_str:
                    count_consecutive += 1
                else: break
    
    print(f"📊 [LOG] Ultimo autore: {last_source_str} (Consecutivi: {count_consecutive})")

    winner = None
    # Se l'ultimo autore ha postato meno di 3 volte, cerchiamo ancora lui
    if last_source_str and count_consecutive < 3:
        # Gestisce sia username stringa che ID numerico
        try:
            target = int(last_source_str) if last_source_str.lstrip('-').isdigit() else last_source_str
            print(f"🔍 [TG] Scansione target: {target}")
            async for m in client.iter_messages(target, limit=50):
                m_id = f"{last_source_str}_{m.id}"
                if m.video and m_id not in gia_postati and m.date > limit_date:
                    winner = {'msg': m, 'tag': SOURCES.get(target, 'catanialatinlovers'), 'id': m_id, 'date': m.date}
                    break
        except Exception as e:
            print(f"Errore scansione consecutiva: {e}")

    # Se non c'è un vincitore consecutivo o abbiamo finito i 3 post, cerchiamo il più nuovo tra tutti
    if not winner:
        all_candidates = []
        for src, tag in SOURCES.items():
            try:
                print(f"🔍 [TG] Scansione: {src}...")
                async for m in client.iter_messages(src, limit=50):
                    m_id = f"{src}_{m.id}"
                    if m.video and m_id not in gia_postati and m.date > limit_date:
                        all_candidates.append({'date': m.date, 'msg': m, 'tag': tag, 'id': m_id})
                        break
            except: continue
        if all_candidates:
            all_candidates.sort(key=lambda x: x['date'], reverse=True)
            winner = all_candidates[0]

    # --- FASE 3: DOWNLOAD & PREPARAZIONE ---
    if winner:
        if not os.path.exists('ready.mp4'):
            print(f"🎬 [TG] Preparazione video di @{winner['tag']} ({winner['id']})")
            raw_path = await winner['msg'].download_media()
            subprocess.run([
                'ffmpeg', '-i', raw_path, '-vf', 'scale=-2:1080', 
                '-vcodec', 'libx264', '-crf', '22', '-preset', 'faster', 
                '-acodec', 'aac', '-b:a', '192k', '-y', 'ready.mp4'
            ])
            
            new_caption = (
                f"L'energia della serata a Catania! 🌋💃\n\n"
                f"🎥 Video by @{winner['tag']}\n\n"
                f"Segui @catanialatinlovers per non perderti i prossimi eventi 🕺✨\n\n"
                f"#CataniaLatinLovers #SalsaCatania #BachataCatania #Sicilia #SocialDance"
            )
            
            gia_postati.append(winner['id'])
            with open('pubblicati.txt', 'w') as f: f.write("\n".join(gia_postati[-100:]))
            with open('caption.txt', 'w', encoding='utf-8') as f: f.write(new_caption)
            if os.path.exists(raw_path): os.remove(raw_path)
            print(f"✅ [OK] Prossimo Reel pronto: {winner['id']}")
    else:
        print("ℹ️ [INFO] Nessun video nuovo trovato.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
