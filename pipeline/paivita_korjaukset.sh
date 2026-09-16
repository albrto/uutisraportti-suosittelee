#!/bin/bash
# Siirrytään skriptin omaan kansioon (tärkeää jos kutsutaan muualta)
cd "$(dirname "$0")"

# 1. Hae korjaukset ja ohitukset pilvestä (iPadilta)
echo "☁️ Haetaan uusimmat korjaukset pilvestä..."
cd "/Users/antero/Koodi/uutisraportti-web" && git pull --quiet || true
cd "/Users/antero/Koodi/uutisraportti-web/pipeline"
python3 synkronoi_pilvi_tiedostot.py

# 2. Tarkista löytyykö korjaukset.json (esim. juuri pilvestä haettu)
if [ ! -f korjaukset.json ] || [ ! -s korjaukset.json ] || [ "$(cat korjaukset.json)" == "[]" ]; then
    echo "ℹ️ Ei korjauksia sovellettavaksi (korjaukset.json on tyhjä tai puuttuu)."
    exit 0
fi

# 3. Sovella korjaukset
echo "⚙️ Sovelletaan korjaukset suositukset.json-tiedostoon..."
python3 sovella_korjaukset.py korjaukset.json

if [ $? -eq 0 ]; then
    # 4. Päivitä validaattorin data (epailyttavat.js) jotta korjatut häviävät listalta
    echo "🔄 Päivitetään validaattorin data..."
    python3 validoi_suosittelijat.py

    # 5. Julkaise muutokset tuotantoon jos soveltaminen onnistui
    echo "🚀 Julkaistaan muutokset tuotantoon..."
    /Users/antero/Koodi/uutisraportti-web/julkaise.sh
    
    # 6. Siivoa korjaukset.json talteen (tai poista)
    mv korjaukset.json korjaukset_applied_$(date +%Y%m%d_%H%M%S).json
else
    echo "❌ Korjausten soveltaminen epäonnistui, keskeytetään julkaisu."
    exit 1
fi
