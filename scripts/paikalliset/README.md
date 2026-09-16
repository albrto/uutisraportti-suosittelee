# Paikallisten työkalujen varmuuskopiot

Nämä ovat **varmuuskopioita** Anteron koneella olevista paikallisista työkaluista,
jotka eivät muuten olisi missään versionhallinnassa. Sivusto tai GitHub Actions
**ei käytä näitä** — ajettavat originaalit ovat pipeline-repossa
`/Users/antero/Library/Mobile Documents/com~apple~CloudDocs/Koodi/Uutisrapsa.fi/`
(iCloud) ja niissä on kovakoodattuja paikallisia polkuja.

| Tiedosto | Originaali (pipeline-repossa) | Käyttö |
|---|---|---|
| `validoi_suosittelijat.py` | repon juuri | Paikallisen validointidatan ainoa generaattori 16.9.2026 alkaen: kirjoittaa `validointidata/epailyttavat.js` (validaattori-UI) ja `.json` (laheta_ilmoitus, korjaa_suosittelijat) samalla liputuslogiikalla. Eri skripti kuin web-repon `scripts/generoi_validointidata.py`, joka tuottaa admin-UI:n `admin/epailyttavat.json`in (`is_suspicious`-liput). |
| `korjaa_suosittelijat_interaktiivisesti.py` | repon juuri | Interaktiivinen suosittelijakorjaustyökalu. |
| `validaattori/index.html` | `validointidata/index.html` | Paikallinen validaattori-UI (`kaynnista_validaattori.sh`). |
| `validaattori/palvelin.py` | `validointidata/palvelin.py` | Validaattori-UI:n paikallinen kehityspalvelin. |

Jos originaali muuttuu, päivitä kopio tänne.

Poistettu 16.9.2026: paikallinen `generoi_validointidata.py` (eläköitetty — sen
löyhempi liputuslogiikka ylikirjoitti `validoi_suosittelijat.py`:n tiukemman
`epailyttavat.js`:n; nyt validoi tuottaa molemmat tiedostot yksin).

Historia: originaalit asuivat 16.9.2026 asti Google Antigravityn scratch-kansiossa
(`/Users/antero/.gemini/antigravity/scratch/`), josta ne siirrettiin pipeline-repoon;
samalla tämä web-repon työkopio muutti polkuun `/Users/antero/Koodi/uutisraportti-web`.

Varmuuskopioitu 16.9.2026, polut päivitetty muuton jälkeen samana päivänä.
