import subprocess
import anthropic
import os
import json
from datetime import datetime

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def hae_git_historia():
    cmd = ['git', 'log', '-n', '20', '--pretty=format:%s|||%b']
    result = subprocess.run(cmd, capture_output=True, text=True)
    commits = []
    
    for line in result.stdout.strip().split('\n'):
        if not line: continue
        osat = line.split('|||')
        otsikko = osat[0].strip()
        body = osat[1].strip() if len(osat) > 1 else ""
        
        # Lopetetaan historia vanhaan changelog-ajoon (tai itse tähän skriptiin)
        if "Tekoälyn kirjoittama muutosloki" in otsikko or "päivitetty muutosloki" in otsikko.lower():
            break
        
        # Ohitetaan datapäivitysten automaattiset commitit
        if "Automaatio: Uudet suositukset ja validointidata" in otsikko:
            continue
            
        commits.append(otsikko + (" - " + body if body else ""))
        
    return commits

def muotoile_claudella(commits):
    if not commits:
        return None
        
    historia_str = "\n".join(f"- {c}" for c in commits)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""Olet "Uutisraportti suosittelee" -verkkosivuston rento ja nörttihuumoria viljelevä tiedottaja. 
Koodari on tehnyt taustalla teknisiä päivityksiä. Sinun tehtäväsi on tiivistää nämä ihmislukijalle YHTEEN TAI KAHTEEN LYHYEEN KAPPALEESEEN ymmärrettävästi ja humoristisesti, korostaen mitä siistiä "pellin alla" tapahtui verkkosivulle ja koko automaatiolle.
Kirjoita validia, semanttisesti puhdasta HTML:ää. Käytä rohkeasti <strong>-tageja tärkeissä kohdissa. ÄLÄ LAITA mitään muuta kuin pelkkää HTML-asennettua tekstiä (kuten <p>jotain uutta...</p>). Älä sido sitä ylimääräisten elementtien sisään.

Koodarin commitit:
{historia_str}
    """
    
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
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
        print(f"Claude-virhe (muutosloki): {e}")
        return None

def paivita_html(uusi_teksti):
    html_polku = "muutokset.html"
    if not os.path.exists(html_polku):
        print(f"Ei löydy tiedostoa {html_polku}, ei päivitetä.")
        return
        
    with open(html_polku, 'r', encoding='utf-8') as f:
        sisalto = f.read()
        
    nykyinen_pvm = datetime.now().strftime("%d.%m.%Y")
    
    uusi_html_lohkare = f'''
    <div class="change-item">
      <span class="version-tag">Automaattipäivitys</span>
      <div class="change-date">{nykyinen_pvm} | Tekoälyn katsaus pellin alle</div>
      {uusi_teksti}
    </div>
'''
    
    # Etsi otsikon h1 loppu ja injektoi sen jälkeen
    etsinta = '<h1 class="hero-title" style="text-align: left; margin-bottom: 40px;">Päivitykset & <span class="hero-accent">Muutokset</span></h1>'
    insertti_kohta = sisalto.find(etsinta)
    if insertti_kohta > -1:
        insertti_kohta += len(etsinta)
        uusi_sisalto = sisalto[:insertti_kohta] + uusi_html_lohkare + sisalto[insertti_kohta:]
        with open(html_polku, 'w', encoding='utf-8') as f:
            f.write(uusi_sisalto)
        print("✅ Muutosloki päivitetty!")
        return True
    return False

def main():
    if not ANTHROPIC_API_KEY:
        print("Ei Claude-avainta muutoslokia varten, hypätään yli.")
        return
        
    commits = hae_git_historia()
    if not commits:
        print("Ei uusia committeja uutisoitavaksi muutoslokiin.")
        return
        
    print(f"Generoidaan muutoslokia {len(commits)} commitin pohjalta...")
    html_teksti = muotoile_claudella(commits)
    if html_teksti:
        paivita_html(html_teksti)

if __name__ == "__main__":
    main()
