import feedparser
import requests
import os
import re
import json
from pydub import AudioSegment
from dotenv import load_dotenv
import anthropic

load_dotenv(override=True)

# --- ASETUKSET ---
RSS_URL = "https://feeds.captivate.fm/uutisraportti-podcast/"
LATAA_MÄÄRÄ = 421
LEIKKAUS_SEKUNTIA = 600  # Viimeiset 10 min
TULOS_TIEDOSTO = "suositukset.json"
HISTORIA_TIEDOSTO = "historia_json.txt"

# --- API AVAIMET ---
# Nämä pitää lisätä .env-tiedostoon!
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def transkriboi_deepgram(audio_path):
    print("Lähetetään ääni Deepgramille transkriptioon (tämä kestää vain pari sekuntia)...")
    url = "https://api.deepgram.com/v1/listen?model=nova-2&language=fi&smart_format=true"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/mp3"
    }
    with open(audio_path, "rb") as audio:
        response = requests.post(url, headers=headers, data=audio)
    
    if response.status_code == 200:
        data = response.json()
        try:
            teksti = data['results']['channels'][0]['alternatives'][0]['transcript']
            return teksti
        except KeyError:
            return ""
    else:
        print(f"Deepgram virhe: {response.status_code} - {response.text}")
        return ""

def analysoi_claudella(teksti):
    print("Pyydetään Anthropic Claude 3.5 Sonnet -mallia poimimaan suositukset JSON-muodossa...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    system_prompt = """Olet ammattimainen suomalainen toimitussihteeri. Tehtäväsi on poimia Uutisraportti-podcastin raakatekstistä VAIN todelliset kulttuuri- ja kulutussuositukset.
Paluuta TISMALLEEN JA AINOASTAAN validia JSON-rakennetta, ei mitään muuta tekstiä.

SÄÄNNÖT:
1. KORJAA VIRHEET JA KÄÄNNÄ: Korjaa teosten nimet (esim. "weathering heights" -> "Humiseva harju"). Käännä yleiskieliset asiat suomeksi (esim. "pistachio spread" -> "pistaasilevite").
2. SUOSITTELIJA: Saat tekstin, jossa on sekä jakson alkuesittelyt että lopun suositukset. Päättele puhuja. Vaihtoehdot: Tuomas Peltomäki, Salla Vuorikoski, Marko Junkkari, Jussi Niemeläinen, Anna-Sofia Berner, Anni Keski-Heikki.
3. KATEGORIAT: Määritä AINA jokaiselle suositukselle ylätason "paakategoria", jonka on TISMALLEEN YKSI SEURAAVISTA: "kirja", "elokuva", "tv-sarja", "podcast", "artikkeli", "musiikki", "ruoka", "kulttuuri", "urheilu", tai "muu" (jos mikään edeltävistä ei sovi). Keksi lisäksi 1-3 tarkempaa, vapaamuotoista tägiä "kategoriat"-listaan (esim. "teatteri", "historia", "viini").
4. LINKIT: Lisää Goodreads-linkki (`https://www.goodreads.com/search?q=Nimi`) kirjoille ja IMDb-linkki (`https://www.imdb.com/find/?q=Nimi`) elokuville/sarjoille. Musiikille ja podcasteille lisää suoratoistolinkki "lisatieto_linkki" -kenttään (esim. `https://open.spotify.com/search/Nimi` tai vastaava haku Apple Musiciin, Tidaliin tai Suplaan). Kaikille "google_linkki" -kenttään hakulinkki `https://www.google.com/search?q=Nimi`.

VASTAUKSEN RAKENNE (palauta taulukko):
[
  {
    "teos": "Oikea Nimi",
    "paakategoria": "kirja",
    "google_linkki": "https://www.google.com/...",
    "lisatieto_linkki": "https://www.goodreads.com/...",
    "kuvaus": "1-2 lausetta...",
    "suosittelija": "Tuomas Peltomäki",
    "kategoriat": ["historia", "elämäkerrat"]
  }
]
Palauta pelkkä suora lista `[]`. Älä käytä markdown-koodiblokkeja (```json ... ```). Jos suosituksia ei ole, palauta `[]`.
"""

    models_to_try = [
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
        "claude-opus-4-6"
    ]

    tulos = None
    for model_name in models_to_try:
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=1500,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Analysoi tämä teksti ja palauta JSON:\n\n{teksti}"}
                ]
            )
            tulos = response.content[0].text.strip()
            print(f"Käytettiin mallia: {model_name}")
            break
        except Exception as e:
            print(f"⚠️ Malli {model_name} epäonnistui: {e}")
            continue
                
    if not tulos:
        print("Virhe: Yksikään Anthropic-malli ei ollut käytettävissä omalla API-avaimellasi.")
        return []
        
    # Puhdistetaan mahdolliset markdown-blokit
    if tulos.startswith("```json"):
        tulos = tulos[7:]
    if tulos.endswith("```"):
        tulos = tulos[:-3]
        
    try:
        return json.loads(tulos.strip())
    except Exception as e:
        print(f"Virhe JSON:n luomisessa: {e}\nRAAKATULOS:\n{tulos}")
        return []

def aja_prosessi():
    if not DEEPGRAM_API_KEY or not ANTHROPIC_API_KEY:
        print("VIRHE: Deepgram tai Anthropic API-avain puuttuu .env-tiedostosta!")
        return

    kasitellyt = []
    if os.path.exists(HISTORIA_TIEDOSTO):
        with open(HISTORIA_TIEDOSTO, "r", encoding="utf-8") as h:
            kasitellyt = h.read().splitlines()

    kaikki_data = []
    if os.path.exists(TULOS_TIEDOSTO):
        with open(TULOS_TIEDOSTO, "r", encoding="utf-8") as f:
            try:
                kaikki_data = json.load(f)
            except:
                kaikki_data = []

    feed = feedparser.parse(RSS_URL)

    for entry in reversed(feed.entries[:LATAA_MÄÄRÄ]):
        jakson_tunniste = entry.id
        otsikko = entry.title
        
        pvm_teksti = ""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            tm = entry.published_parsed
            pvm_teksti = f"{tm.tm_mday}.{tm.tm_mon}.{tm.tm_year}"
            
        if jakson_tunniste in kasitellyt:
            print(f"⏩ Skippataan: '{otsikko}' (Löytyy jo historiasta)")
            continue

        audio_url = next((l.href for l in entry.links if 'audio' in l.type), None)
        if audio_url:
            print(f"\n--- ALOITETAAN UUSI JAKSO: {otsikko} ---")
            mp3_temp = "temp_full_dg.mp3"
            clip_temp = "temp_clip_dg.mp3"
            
            print("Ladataan audiota...")
            r = requests.get(audio_url)
            with open(mp3_temp, 'wb') as f:
                f.write(r.content)
            
            print(f"Leikataan alun esittelyt ja loppuosa ({LEIKKAUS_SEKUNTIA // 60} min)...")
            audio = AudioSegment.from_file(mp3_temp)
            kesto_ms = len(audio)
            
            # Otetaan ensimmäiset 2 min ja varsinainen loppuosa
            alku_osa = audio[:120000]
            loppu_osa_alku_ms = max(0, kesto_ms - (LEIKKAUS_SEKUNTIA * 1000))
            loppu_osa = audio[loppu_osa_alku_ms:]
            
            yhdistetty_audio = alku_osa + loppu_osa
            yhdistetty_audio.export(clip_temp, format="mp3")
            
            # 1. Ääni tekstiksi Deepgramilla
            raakateksti = transkriboi_deepgram(clip_temp)
            
            if raakateksti:
                # 2. Tekstistä JSONiks Claudella
                suositukset_json = analysoi_claudella(raakateksti)
                
                # Vaikka olisi tyhjä lista ([]), tallennetaan silti että jakso on käsitelty
                jakso_data = {
                    "id": jakson_tunniste,
                    "jakso_otsikko": otsikko,
                    "paivamaara": pvm_teksti,
                    "suositukset": suositukset_json
                }
                
                # Työnnetään lista alkuun, koska reversed() käy jaksot vanhimmasta uusimpaan
                kaikki_data.insert(0, jakso_data)
                
                with open(TULOS_TIEDOSTO, "w", encoding="utf-8") as f_out:
                    json.dump(kaikki_data, f_out, ensure_ascii=False, indent=2)
                
                with open(HISTORIA_TIEDOSTO, "a", encoding="utf-8") as h:
                    h.write(jakson_tunniste + "\n")
                    
                # Tallennetaan tilapäistieto sähköposti-ilmoitusta varten
                tulos_data = {
                    "jakso_otsikko": otsikko,
                    "suosituksia_kpl": len(suositukset_json),
                    "jakson_id": jakson_tunniste
                }
                with open("ajon_tulos.json", "w", encoding="utf-8") as ft:
                    json.dump(tulos_data, ft, ensure_ascii=False)
                    
                print(f"✅ Jakso valmis ja tallennettu suositukset.json -tiedostoon!")
            else:
                print("❌ Tekstitys epäonnistui, ohitetaan JSON-analyysi.")
            
            if os.path.exists(mp3_temp): os.remove(mp3_temp)
            if os.path.exists(clip_temp): os.remove(clip_temp)

if __name__ == "__main__":
    aja_prosessi()
