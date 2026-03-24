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
    
    prompt = f"""Olet "Uutisraportti suosittelee" -verkkosivuston rento tiedottaja. 
Koodari on tehnyt taustalla teknisiä päivityksiä. Sinun tehtäväsi on tiivistää nämä tavalliselle käyttäjälle ymmärrettävästi.

TYYLI JA MUOTO:
1. Käytä RANSKALAISIA VIIVOJA (HTML: <ul class="change-list"> ja <li>).
2. Pidä teksti LYHYENÄ ja ytimekkäänä.
3. ÄLÄ paljasta tarkkaa arkkitehtuuria, mallinimiä (kuten Claude 4) tai kirjastojen versioita.
4. Kuvaile tekniset muutokset abstraktisti (esim. "Parannettu automaatiota", "Päivitetty tekoälyä", "Varmistettu sovelluksen vakaus").
5. Korosta käyttäjälle näkyvää hyötyä (jos sellaista on).
6. Palauta VAIN validia HTML-koodia (pelkkä <ul>...</ul>), ei markdownia tai muuta tekstiä.

Koodarin tekniset commitit:
{historia_str}
    """

    models_to_try = [
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001"
    ]
    
    for model_name in models_to_try:
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=800,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            tulos = response.content[0].text.strip()
            # Puhdistus
            tulos = re.sub(r'^```html\s*', '', tulos)
            tulos = re.sub(r'^```\s*', '', tulos)
            tulos = re.sub(r'\s*```$', '', tulos)
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
        
    # Etsi viimeisin versionumero diagnostiikkaa tai automaatiota varten
    versio_match = re.search(r'<span class="version-tag">v(\d+)\.(\d+)\.(\d+)</span>', sisalto)
    uusi_versio = "v1.2.0" # Oletus jos ei löydy
    if versio_match:
        major, minor, patch = map(int, versio_match.groups())
        uusi_versio = f"v{major}.{minor + 1}.0"
        
    # Tarkistetaan, onko tälle päivälle jo tehty automaattipäivitys (vältetään tuplat)
    nykyinen_pvm = datetime.now().strftime("%d.%m.%Y")
    if f"{nykyinen_pvm} | Automaattinen päivitys" in sisalto:
        print(f"⚠️ Muutosloki on jo päivitetty tänään ({nykyinen_pvm}). Hypätään yli.")
        return False

    uusi_html_lohkare = f'''
    <div class="change-item">
      <span class="version-tag">{uusi_versio}</span>
      <div class="change-date">{nykyinen_pvm} | Automaattinen päivitys</div>
      {uusi_teksti}
    </div>
'''
    
    # Etsitään h1-tagi välittämättä välilyönneistä tai tarkasta sisällöstä
    pattern = r'(<h1[^>]*>.*?Muutosloki.*?</h1>)'
    match = re.search(pattern, sisalto, re.IGNORECASE | re.DOTALL)
    
    if match:
        kohta = match.end()
        uusi_sisalto = sisalto[:kohta] + uusi_html_lohkare + sisalto[kohta:]
        
        with open(html_polku, 'w', encoding='utf-8') as f:
            f.write(uusi_sisalto)
        print(f"🚀 Muutosloki {uusi_versio} tallennettu onnistuneesti!")
        return True
    else:
        print("❌ Virhe: Ei löydetty h1-tagia, jossa luki 'Muutosloki'.")
        return False

def main():
    if not ANTHROPIC_API_KEY:
        print("❌ Virhe: ANTHROPIC_API_KEY puuttuu.")
        return
        
    commits = hae_git_historia()
    if not commits:
        print("ℹ️ Ei uusia teknisiä committeja listattavaksi.")
        return
        
    print("🤖 Pyydetään Claudelta tiivistystä (käyttäjäystävällinen muoto)...")
    html_teksti = muotoile_claudella(commits)
    
    if html_teksti:
        paivita_html(html_teksti)
    else:
        print("❌ Virhe: Claude ei palauttanut tekstiä.")

if __name__ == "__main__":
    main()
