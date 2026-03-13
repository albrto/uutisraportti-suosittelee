#!/bin/bash
# Kopioi suositukset.json iCloud-kansiosta ja pushaa GitHubiin

cp "/Users/antero/Library/Mobile Documents/com~apple~CloudDocs/Koodi/Uutisrapsan suositukset/suositukset.json" \
   /Users/antero/.gemini/antigravity/scratch/uutisraportti-web/suositukset.json

cd /Users/antero/.gemini/antigravity/scratch/uutisraportti-web

git add suositukset.json
git commit -m "Päivitetty data $(date '+%d.%m.%Y')"
git push

echo "✅ Julkaistu! https://albrto.github.io/uutisraportti-suosittelee/"
