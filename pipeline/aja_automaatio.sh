#!/bin/bash
# Siirrytään työkansioon
cd "/Users/antero/Koodi/uutisraportti-web/pipeline"

echo "🚀 Aloitetaan automaatio $(date)"

# Hae mahdolliset iPadilla tehdyt ohitukset/korjaukset
echo "☁️ Haetaan iPadin tekemät ohitukset..."
cd "/Users/antero/Koodi/uutisraportti-web" && git pull --quiet || true
cd "/Users/antero/Koodi/uutisraportti-web/pipeline"
./venv/bin/python3 synkronoi_pilvi_tiedostot.py

# Ajetaan automaatio (Deepgram + Claude) käyttäen virtuaaliympäristöä
./venv/bin/python3 uutisraportti_automaatio_deepgram_claude.py

# Päivitetään validointidata (epailyttavat.js + .json) tarkistustyökalua ja
# sähköposti-ilmoitusta varten
./venv/bin/python3 validoi_suosittelijat.py

# Lähetetään mahdollinen sähköposti-ilmoitus (jos uusia jaksoja käsiteltiin)
./venv/bin/python3 laheta_ilmoitus.py

echo "✅ Automaatio suoritettu $(date)"
