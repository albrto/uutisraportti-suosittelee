import json
import os
import requests
import urllib.parse

STATUS_FILE = "ajon_tulos.json"
EPAILYTTAVAT_FILE = "admin/epailyttavat.json"
NETLIFY_URL = "https://uutisrapsa.fi/"

def hae_epailyttavien_luettelo(jakso_id):
    if not os.path.exists(EPAILYTTAVAT_FILE):
        return 0
    
    try:
        with open(EPAILYTTAVAT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for jakso in data:
            if jakso.get("jakso_id") == jakso_id:
                return len(jakso.get("epailyttavat_suositukset", []))
    except Exception as e:
        print(f"Laheta_ilmoitus: Virhe luettaessa epailyttavat.json: {e}")
        
    return 0

def laheta_sahkoposti(otsikko, viesti):
    print(f"Lähetetään sähköposti Netlify Formsin kautta:\nOtsikko: {otsikko}\n{viesti}")
    
    payload = {
        "form-name": "automaatio-ilmoitus",
        "subject": otsikko,
        "viesti": viesti
    }
    
    try:
        res = requests.post(NETLIFY_URL, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if res.status_code == 200:
            print("✅ Sähköposti-ilmoitus lähetetty onnistuneesti!")
        else:
            print(f"❌ Sähköposti-ilmoituksen lähetys epäonnistui: {res.status_code}")
    except Exception as e:
        print(f"❌ Yhteysvirhe sähköpostin lähetyksessä: {e}")

def main():
    if not os.path.exists(STATUS_FILE):
        print("laheta_ilmoitus.py: Ei raportoitavaa, uusia jaksoja ei käsitelty.")
        return

    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            tulos = json.load(f)
    except Exception as e:
        print(f"Virhe luettaessa ajon statusta: {e}")
        return

    jakso_otsikko = tulos.get("jakso_otsikko", "Nimetön jakso")
    suos_kpl = tulos.get("suosituksia_kpl", 0)
    jakson_id = tulos.get("jakson_id", "")
    
    epailyttavia_kpl = hae_epailyttavien_luettelo(jakson_id)
    
    sähköpostin_otsikko = f"Uutisraportti: Uusi jakso '{jakso_otsikko}' käsitelty!"
    
    viesti = f"Skripti ajettiin onnistuneesti.\n\nKäsitelty jakso: {jakso_otsikko}\nAnalysoitavaksi löytyi yhteensä {suos_kpl} suositusta.\n\n"
    
    if epailyttavia_kpl > 0:
        sähköpostin_otsikko = f"⚠️ Huomio: Uudessa Uutisraportti-jaksossa epäilyttäviä suosittelijoita!"
        viesti += f"⚠️ HUOMIO: Skripti poimi tästä jaksosta {epailyttavia_kpl} epäilyttävää suosittelijanimeä, jotka eivät täsmää RSS-feediin.\n"
        viesti += "Käy tarkistamassa ja vahvistamassa ne osoitteessa: https://uutisrapsa.fi/admin\n"
    else:
        viesti += "Kaikki suosittelijanimet vaikuttivat luotettavilta.\n"
        
    laheta_sahkoposti(sähköpostin_otsikko, viesti)
    
    # Siivous
    os.remove(STATUS_FILE)

if __name__ == "__main__":
    main()
