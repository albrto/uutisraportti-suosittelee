# Paikallisten työkalujen varmuuskopiot

Nämä ovat **varmuuskopioita** Anteron koneella olevista paikallisista työkaluista,
jotka eivät muuten olisi missään versionhallinnassa. Sivusto tai GitHub Actions
**ei käytä näitä** — ajettavat originaalit ovat koneella polussa
`/Users/antero/.gemini/antigravity/scratch/` ja niissä on kovakoodattuja
paikallisia polkuja.

| Tiedosto | Originaali | Käyttö |
|---|---|---|
| `generoi_validointidata.py` | `scratch/generoi_validointidata.py` | Paikallinen versio, jota `aja_automaatio.sh` kutsuu. **HUOM: eri skripti kuin `scripts/generoi_validointidata.py`** — tämä tuottaa vanhaa "vain epäilyttävät" -muotoa (`epailyttavat_suositukset`) paikalliselle validaattorille; web-repon versio tuottaa kaikki suositukset `is_suspicious`-lipulla admin-UI:lle. |
| `korjaa_suosittelijat_interaktiivisesti.py` | `scratch/korjaa_suosittelijat_interaktiivisesti.py` | Interaktiivinen suosittelijakorjaustyökalu. |
| `validaattori/index.html` | `scratch/validointidata/index.html` | Paikallinen validaattori-UI (`kaynnista_validaattori.sh`). |
| `validaattori/palvelin.py` | `scratch/validointidata/palvelin.py` | Validaattori-UI:n paikallinen kehityspalvelin. |

Jos originaali muuttuu, päivitä kopio tänne. Jos scratch-kansio katoaa,
palauta tiedostot täältä ja korjaa tarvittaessa kovakoodatut polut.

Varmuuskopioitu 16.9.2026.
