#!/bin/bash
# Kopioi suositukset.json iCloud-kansiosta ja pushaa GitHubiin

cp "/Users/antero/Library/Mobile Documents/com~apple~CloudDocs/Koodi/Uutisrapsan suositukset/suositukset.json" \
   /Users/antero/.gemini/antigravity/scratch/uutisraportti-web/suositukset.json

cd /Users/antero/.gemini/antigravity/scratch/uutisraportti-web

git add .
git commit -m "Päivitys: $(date '+%d.%m.%Y %H:%M')"
git push

echo "✅ Julkaistu! https://albrto.github.io/uutisraportti-suosittelee/"
