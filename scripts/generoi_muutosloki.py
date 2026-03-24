import subprocess
import anthropic
import os
import json
from datetime import datetime

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def hae_git_historia():
    print("📜 Luetaan git-historiaa...")
    cmd = ['git', 'log', '-n', '20', '--pretty=format:%s|||%b']
    result = subprocess.run(cmd, capture_output=True, text=True)
    commits = []
    
    lines = result.stdout.strip().split('\n')
    print(f"📄 Löydettiin {len(lines)} riviä historiatierosta.")
    
    for line in lines:
        if not line: continue
        osat = line.split('|||')
        otsikko = osat[0].strip()
        body = osat[1].strip() if len(osat) > 1 else ""
        
        print(f"  - Tutkitaan: {otsikko}")
        
        # Lopetetaan historia vanhaan changelog-ajoon
        if "päivitetty muutosloki" in otsikko.lower() or "tekoälyn katsaus" in otsikko.lower():
            print("  🛑 Pysähdytään: Vanha muutosloki-commit löydetty.")
            break
        
        # Ohitetaan datapäivitysten automaattiset commitit
        if "Automaatio: Uudet suositukset" in otsikko:
            continue
            
        print(f"  ✅ Lisätään: {otsikko}")
        commits.append(otsikko + (" - " + body if body else ""))
        
    return commits

def muotoile_claudella(commits):
    if not commits:
        return None
        
    historia_str = "\n".join(f"- {c}" for c in commits)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Lokitetaan avaimen alku (turvallisesti) tyypin tunnistamiseksi
    key_prefix = ANTHROPIC_API_KEY[:10] if ANTHROPIC_API_KEY else "PUUTTUU"
    print(f"🔑 Käytetään avainta (alku): {key_prefix}...")

    prompt = f"""Olet "Uutisraportti suosittelee" -verkkosivuston rento ja nörttihuumoria viljelevä tiedottaja. 
Koodari on tehnyt taustalla teknisiä päivityksiä. Sinun tehtäväsi on tiivistää nämä ihmislukijalle YHTEEN TAI KAHTEEN LYHYEEN KAPPALEESEEN ymmärrettävästi ja humoristisesti, korostaen mitä siistiä "pellin alla" tapahtui verkkosivulle ja koko automaatiolle.
Kirjoita validia, semanttisesti puhdasta HTML:ää. Käytä rohkeasti <strong>-tageja tärkeissä kohdissa. ÄLÄ LAITA mitään muuta kuin pelkkää HTML-asennettua tekstiä (kuten <p>jotain uutta...</p>). Älä sido sitä ylimääräisten elementtien sisään.

Koodarin commitit:
{historia_str}
    """

    models_to_try = [
        "claude-3-5-sonnet-20240620",
        "claude-3-5-haiku-20241022",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-instant-1.2"
    ]
    
    for model_name in models_to_try:
        try:
            print(f"  - Yritetään mallia: {model_name}...")
            response = client.messages.create(
                model=model_name,
                max_tokens=800,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            tulos = response.content[0].text.strip()
            if tulos.startswith("```html"): tulos = tulos[7:]
            elif tulos.startswith("```"): tulos = tulos[3:]
            if tulos.endswith("```"): tulos = tulos[:-3]
            return tulos.strip()
        except Exception as e:
            print(f"  ⚠️ Malli {model_name} epäonnistui: {e}")
            continue
            
    return None

import re

def paivita_html(uusi_teksti):
    html_polku = "muutokset.html"
    if not os.path.exists(html_polku):
        print(f"❌ Virhe: Tiedostoa {html_polku} ei löydy.")
        return False
        
    with open(html_polku, 'r', encoding='utf-8') as f:
        sisalto = f.read()
        
    # Tarkistetaan, onko tälle päivälle jo tehty automaattipäivitys (vältetään tuplat)
    nykyinen_pvm = datetime.now().strftime("%d.%m.%Y")
    if f"{nykyinen_pvm} | Tekoälyn katsaus" in sisalto:
        print(f"⚠️ Muutosloki on jo päivitetty tänään ({nykyinen_pvm}). Hypätään yli.")
        return False

    uusi_html_lohkare = f'''
    <div class="change-item">
      <span class="version-tag">Automaattipäivitys</span>
      <div class="change-date">{nykyinen_pvm} | Tekoälyn katsaus pellin alle</div>
      {uusi_teksti}
    </div>
'''
    
    # Etsitään h1-tagi välittämättä välilyönneistä tai tarkasta sisällöstä
    pattern = r'(<h1[^>]*>.*?Muutosloki.*?</h1>)'
    match = re.search(pattern, sisalto, re.IGNORECASE | re.DOTALL)
    
    if match:
        print(f"✅ Löydettiin lisäyskohta: {match.group(1)[:50]}...")
        kohta = match.end()
        uusi_sisalto = sisalto[:kohta] + uusi_html_lohkare + sisalto[kohta:]
        
        with open(html_polku, 'w', encoding='utf-8') as f:
            f.write(uusi_sisalto)
        print("🚀 Muutosloki tallennettu onnistuneesti!")
        return True
    else:
        print("❌ Virhe: Ei löydetty h1-tagia, jossa luki 'Muutosloki'.")
        print("Tiedoston alkuosa viitteeksi:")
        print(sisalto[:300])
        return False

def main():
    if not ANTHROPIC_API_KEY:
        print("❌ Virhe: ANTHROPIC_API_KEY puuttuu.")
        return
        
    commits = hae_git_historia()
    print(f"🔍 Löydettiin {len(commits)} huomioitavaa commitia.")
    
    if not commits:
        print("ℹ️ Ei uusia teknisiä committeja listattavaksi.")
        return
        
    print("🤖 Pyydetään Claudelta tiivistystä...")
    html_teksti = muotoile_claudella(commits)
    
    if html_teksti:
        print("📝 Generoitu teksti:")
        print(html_teksti[:100] + "...")
        paivita_html(html_teksti)
    else:
        print("❌ Virhe: Claude ei palauttanut tekstiä.")

if __name__ == "__main__":
    main()
