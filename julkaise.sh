#!/bin/bash
# Kopioi suositukset.json iCloud-kansiosta, luo .js-versio ja pushaa GitHubiin

SOURCE_JSON="/Users/antero/Library/Mobile Documents/com~apple~CloudDocs/Koodi/Uutisrapsa.fi/suositukset.json"
TARGET_DIR="/Users/antero/.gemini/antigravity/scratch/uutisraportti-web"

# 1. Kopioi JSON
cp "$SOURCE_JSON" "$TARGET_DIR/suositukset.json"


# 2.5 Päivitä myös admin/epailyttavat.js ja tyhjennä korjaukset
EPAILYTTAVAT_JS="/Users/antero/.gemini/antigravity/scratch/validointidata/epailyttavat.js"
if [ -f "$EPAILYTTAVAT_JS" ]; then
    cp "$EPAILYTTAVAT_JS" "$TARGET_DIR/admin/epailyttavat.js"
fi
echo "[]" > "$TARGET_DIR/admin/korjaukset.json"

# 3. Git-toimenpiteet
cd "$TARGET_DIR"
git add .
git commit -m "Päivitys: $(date '+%d.%m.%Y %H:%M')"
git push

echo "✅ Julkaistu! https://albrto.github.io/uutisraportti-suosittelee/"
