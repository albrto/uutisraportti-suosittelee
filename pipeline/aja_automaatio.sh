#!/bin/bash
# Siirrytään työkansioon
cd "/Users/antero/Koodi/uutisraportti-web/pipeline"

# Yhteiset skriptit (../scripts/) ajetaan paikallisessa moodissa:
# datakopiot tässä kansiossa, epäilyttävät validointidatassa
export UUTISRAPSA_DATAKANSIO="/Users/antero/Koodi/uutisraportti-web/pipeline"
export UUTISRAPSA_EPAILYTTAVAT="/Users/antero/Koodi/uutisraportti-web/pipeline/validointidata/epailyttavat.json"

echo "🚀 Aloitetaan automaatio $(date)"

# Hae mahdolliset iPadilla tehdyt ohitukset/korjaukset
echo "☁️ Haetaan iPadin tekemät ohitukset..."
git -C "/Users/antero/Koodi/uutisraportti-web" pull --quiet || true
./venv/bin/python3 synkronoi_pilvi_tiedostot.py

# Ajetaan automaatio (Deepgram + Claude) käyttäen virtuaaliympäristöä
./venv/bin/python3 ../scripts/uutisraportti_automaatio_deepgram_claude.py

# Päivitetään validointidata (epailyttavat.js + .json) tarkistustyökalua ja
# sähköposti-ilmoitusta varten
./venv/bin/python3 validoi_suosittelijat.py

# Lähetetään mahdollinen sähköposti-ilmoitus (jos uusia jaksoja käsiteltiin)
./venv/bin/python3 ../scripts/laheta_ilmoitus.py

echo "✅ Automaatio suoritettu $(date)"
