import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Pulizia dei Secret
def c(v): return str(v or "").strip().replace('*', '').replace(' ', '')

API_ID = int(c(os.getenv('TG_API_ID')) or 0)
API_HASH = c(os.getenv('TG_API_HASH'))
SESSION_STR = c(os.getenv('TG_SESSION'))
IG_ID = c(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = c(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY')

# CONFIGURAZIONE SORGENTI (ID Telegram : Tag Instagram)
# Per i canali privati t.me/c/XXXXXXXXXX/YYY, l'ID è -100XXXXXXXXXX
SOURCES = {
    'phorig': 'original.ph_',
    'photogoldct': 'photo_goldsalsa',
    -1002422907785: 'elegancia_latina_catania',
    -1003220769402: 'latin__chic'
}

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    # Database ID pubblicati
    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: 
        gia_postati = [line.strip() for line in f.read().splitlines() if line.strip()]

    # 1. PUBBLICAZIONE (Video pronto dal giro precedente)
    if os.path.exists('ready.mp4'):
        caption = "Catania Latin Lovers 🌋"
        if os.path.exists('caption.txt'):
            with open('caption.txt', 'r', encoding='utf-8') as f: caption = f.read()

        video_url = f"https://raw.githubusercontent.com/{REPO}/main/ready.mp4"
        print(f"🚀 Pubblicazione Reel. Tagging: {caption}")
        
        r = requests.post(f"https://graph.facebook.com/{IG_ID}/media", data={
            'media_type': 'REELS', 'video_url': video_url, 
            'caption': caption, 'access_token': IG_TOKEN
        }).json()
        
        if 'id' in r:
            print(f"✅ Container OK. Attesa 90s...")
            time.sleep(90)
            requests.post(f"https://graph.facebook.com/{IG_ID}/media_publish", 
                          data={'creation_id': r['id'], 'access_token': IG_TOKEN})
            for f_rem in ['ready.mp4', 'caption.txt']:
                if os.path.exists(f_rem): os.remove(f_rem)
            print("🔥 REEL PUBBLICATO!")
        else:
            print(f"Errore IG: {r}")

    # 2. PREPARAZIONE PROSSIMO VIDEO (Round Robin tra i canali)
    video_prepared = False
    for source, ig_tag in SOURCES.items():
        try:
            print(f"Controllo sorgente: {source}...")
            async for m in client.iter_messages(source, limit=15):
                msg_id = f"{source}_{m.id}"
                if m.video and msg_id not in gia_postati:
                    print(f"🎬 Preparazione nuovo video da @{ig_tag}...")
                    raw_path = await m.download_media()
                    
                    # Compressione HQ 1080p
                    subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:1080', '-vcodec', 'libx264', '-crf', '22', '-preset', 'faster', '-acodec', 'aac', '-b:a', '192k', '-y', 'ready.mp4'])
                    
                    # Didascalia strategica per follower e tag
                    new_caption = (
                        f"L'energia della serata a Catania! 🌋💃\n\n"
                        f"🎥 Video by @{ig_tag}\n\n"
                        f"Segui @catanialatinlovers per restare aggiornato sulle migliori serate di Salsa e Bachata in Sicilia! 🕺✨\n\n"
                        f"#CataniaLatinLovers #SalsaCatania #BachataCatania #SocialDance #CataniaNight #SalsaDancing"
                    )
                    
                    # Salva ID e Caption
                    gia_postati.append(msg_id)
                    with open('pubblicati.txt', 'w') as f: f.write("\n".join(gia_postati[-100:]))
                    with open('caption.txt', 'w', encoding='utf-8') as f: f.write(new_caption)
                    
                    if os.path.exists(raw_path): os.remove(raw_path)
                    print(f"✅ Prossimo video (da {ig_tag}) in coda.")
                    video_prepared = True
                    break
            if video_prepared: break
        except Exception as e:
            print(f"Errore accesso sorgente {source}: {e}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
