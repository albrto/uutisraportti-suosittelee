#!/bin/bash
# Kopioi suositukset.json iCloud-kansiosta, luo .js-versio ja pushaa GitHubiin

SOURCE_JSON="/Users/antero/Library/Mobile Documents/com~apple~CloudDocs/Koodi/Uutisrapsan suositukset/suositukset.json"
TARGET_DIR="/Users/antero/.gemini/antigravity/scratch/uutisraportti-web"

# 1. Kopioi JSON
cp "$SOURCE_JSON" "$TARGET_DIR/suositukset.json"

# 2. Luo JS-versio (CORS-ohitusta varten)
cat "$TARGET_DIR/suositukset.json" | sed '1s/^/window.SUOSITUKSET_DATA = /' | sed '$s/$/;/' > "$TARGET_DIR/suositukset.js"

# 3. Git-toimenpiteet
cd "$TARGET_DIR"
git add .
git commit -m "Päivitys: $(date '+%d.%m.%Y %H:%M')"
git push

echo "✅ Julkaistu! https://albrto.github.io/uutisraportti-suosittelee/"
