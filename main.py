import os, requests, time, asyncio, subprocess
from datetime import datetime, timedelta, timezone
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Configurazione variabili d'ambiente
API_ID = int(os.getenv('TG_API_ID') or 0)
API_HASH = os.getenv('TG_API_HASH')
SESSION_STRING = os.getenv('TG_SESSION')
INSTAGRAM_ACCOUNT_ID = os.getenv('IG_BUSINESS_ID')
ACCESS_TOKEN = os.getenv('IG_PAGE_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPOSITORY')

# Parametri di filtraggio
DAYS_LIMIT = 90 # Limite a 3 mesi per recuperare video recenti senza andare troppo indietro

# Mappatura Canali Telegram -> Tag Instagram
VIDEO_SOURCES = {
    'phorig': 'original.ph_',
    'photogoldct': 'photo_goldsalsa',
    -1002422907785: 'elegancia_latina_catania',
    -1003220769402: 'latin__chic'
}

async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.connect()

    # Caricamento database ID pubblicati
    db_file = 'pubblicati.txt'
    if not os.path.exists(db_file): open(db_file, 'w').close()
    with open(db_file, 'r') as f: 
        published_ids = [line.strip() for line in f.read().splitlines() if line.strip()]

    date_threshold = datetime.now(timezone.utc) - timedelta(days=DAYS_LIMIT)

    # --- FASE 1: PUBBLICAZIONE REEL PREPARATO ---
    if os.path.exists('ready.mp4'):
        caption = "Catania Latin Lovers 🌋"
        if os.path.exists('caption.txt'):
            with open('caption.txt', 'r', encoding='utf-8') as f: caption = f.read()

        # Link formattati esattamente come richiesto
        video_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/ready.mp4"
        container_url = f"https://graph.facebook.com/{INSTAGRAM_ACCOUNT_ID}/media"
        
        print(f"🚀 [IG] Publishing Reel: {video_url}")
        
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'access_token': ACCESS_TOKEN
        }
        
        response = requests.post(container_url, data=payload).json()
        creation_id = response.get('id')
        
        if creation_id:
            print(f"✅ [IG] Container created: {creation_id}. Waiting 90s...")
            time.sleep(90)
            publish_url = f"https://graph.facebook.com/{INSTAGRAM_ACCOUNT_ID}/media_publish"
            pub_res = requests.post(publish_url, data={'creation_id': creation_id, 'access_token': ACCESS_TOKEN}).json()
            if 'id' in pub_res:
                print("🔥 [IG] REEL PUBBLICATO!")
                os.remove('ready.mp4')
                if os.path.exists('caption.txt'): os.remove('caption.txt')
        else:
            print(f"❌ [IG] Container failed: {response}")
            # Reset in caso di errore per permettere la rotazione dei video
            if os.path.exists('ready.mp4'): os.remove('ready.mp4')

    # --- FASE 2: SCELTA NUOVO VIDEO (LOGICA BLOCCHI DA 3) ---
    last_author, consecutive_count = None, 0
    if published_ids:
        for full_id in reversed(published_ids):
            if "_" in full_id:
                author_name = full_id.rsplit('_', 1)[0]
                if last_author is None:
                    last_author, consecutive_count = author_name, 1
                elif author_name == last_author:
                    consecutive_count += 1
                else: break
    
    print(f"\n📊 [STATUS] Last Author: {last_author} ({consecutive_count}/3 consecutive)")

    candidates = []
    for source_id, ig_handle in VIDEO_SOURCES.items():
        print(f"\n🔍 [SCAN] Analyzing: {source_id} (@{ig_handle})")
        try:
            found_count = 0
            # Scansione dei messaggi (include video nativi e documenti video come .mov)
            async for msg in client.iter_messages(source_id, limit=20):
                # Verifica se il messaggio contiene un video o un documento di tipo video
                is_video = msg.video or (msg.document and any(msg.document.mime_type.endswith(ext) for ext in ['mp4', 'mov', 'quicktime']))
                if not is_video: continue
                
                found_count += 1
                current_id = f"{source_id}_{msg.id}"
                
                status = "✅ VALID"
                is_valid = True
                
                if current_id in published_ids:
                    status = "❌ ALREADY PUBLISHED"
                    is_valid = False
                elif msg.date < date_threshold:
                    status = f"❌ OUTDATED ({msg.date.strftime('%Y-%m-%d')})"
                    is_valid = False
                
                print(f"   [{found_count}] ID: {msg.id} | Date: {msg.date.strftime('%d/%m %H:%M')} | {status}")
                
                if is_valid and not any(c['source'] == str(source_id) for c in candidates):
                    candidates.append({'date': msg.date, 'msg': msg, 'handle': ig_handle, 'id': current_id, 'source': str(source_id)})
                
                if found_count >= 5: break
        except Exception as e:
            print(f"   ⚠️ Access Error: {e}")

    # Logica di selezione vincitore
    selected_video = None
    if last_author and consecutive_count < 3:
        for cand in candidates:
            if cand['source'] == last_author:
                selected_video = cand
                print(f"\n🎯 [DECISION] Continuing block for {last_author}")
                break

    if not selected_video and candidates:
        valid_options = [c for c in candidates if c['source'] != last_author or consecutive_count >= 3]
        if not valid_options: valid_options = candidates
        valid_options.sort(key=lambda x: x['date'], reverse=True)
        selected_video = valid_options[0]
        print(f"\n🎯 [DECISION] Swapping turn. Selected @{selected_video['handle']}")

    # --- FASE 3: DOWNLOAD E COMPRESSIONE ---
    if selected_video and not os.path.exists('ready.mp4'):
        print(f"🎬 [TG] Preparing video from @{selected_video['handle']} ({selected_video['id']})")
        raw_path = await selected_video['msg'].download_media()
        
        # Conversione HQ 1080p
        subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:1080', '-vcodec', 'libx264', '-crf', '22', '-preset', 'faster', '-acodec', 'aac', '-b:a', '192k', '-y', 'ready.mp4'])
        
        caption_text = (
            f"L'energia della serata a Catania! 🌋💃\n\n"
            f"🎥 Video by @{selected_video['handle']}\n\n"
            f"Segui @catanialatinlovers 🕺✨\n\n"
            f"#CataniaLatinLovers #SalsaCatania #BachataCatania #Sicilia #SocialDance"
        )
        
        published_ids.append(selected_video['id'])
        with open(db_file, 'w') as f:
            f.write("\n".join(published_ids[-100:]))
            
        with open('caption.txt', 'w', encoding='utf-8') as f: 
            f.write(caption_text)
            
        if os.path.exists(raw_path): os.remove(raw_path)
        print(f"✅ [OK] Next Reel ready: {selected_video['id']}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
