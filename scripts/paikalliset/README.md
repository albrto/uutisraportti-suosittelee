# Paikallisten työkalujen varmuuskopiot

Nämä ovat **varmuuskopioita** Anteron koneella olevista paikallisista työkaluista,
jotka eivät muuten olisi missään versionhallinnassa. Sivusto tai GitHub Actions
**ei käytä näitä** — ajettavat originaalit ovat pipeline-repossa
`/Users/antero/Library/Mobile Documents/com~apple~CloudDocs/Koodi/Uutisrapsa.fi/`
(iCloud) ja niissä on kovakoodattuja paikallisia polkuja.

| Tiedosto | Originaali (pipeline-repossa) | Käyttö |
|---|---|---|
| `generoi_validointidata.py` | repon juuri | Paikallinen versio, jota `aja_automaatio.sh` kutsuu. **HUOM: eri skripti kuin `scripts/generoi_validointidata.py`** — tämä tuottaa vanhaa "vain epäilyttävät" -muotoa (`epailyttavat_suositukset`) paikalliselle validaattorille; web-repon versio tuottaa kaikki suositukset `is_suspicious`-lipulla admin-UI:lle. |
| `korjaa_suosittelijat_interaktiivisesti.py` | repon juuri | Interaktiivinen suosittelijakorjaustyökalu. |
| `validaattori/index.html` | `validointidata/index.html` | Paikallinen validaattori-UI (`kaynnista_validaattori.sh`). |
| `validaattori/palvelin.py` | `validointidata/palvelin.py` | Validaattori-UI:n paikallinen kehityspalvelin. |

Jos originaali muuttuu, päivitä kopio tänne.

Historia: originaalit asuivat 16.9.2026 asti Google Antigravityn scratch-kansiossa
(`/Users/antero/.gemini/antigravity/scratch/`), josta ne siirrettiin pipeline-repoon;
samalla tämä web-repon työkopio muutti polkuun `/Users/antero/Koodi/uutisraportti-web`.

Varmuuskopioitu 16.9.2026, polut päivitetty muuton jälkeen samana päivänä.
