#!/bin/bash
echo "📡 Käynnistetään validaattori-palvelin..."
cd "/Users/antero/Koodi/uutisraportti-web/pipeline/validointidata"
open "http://127.0.0.1:5001"
python3 palvelin.py
