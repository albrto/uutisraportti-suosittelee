#!/usr/bin/env python3
"""
Generoi validointi-JSON-tiedoston selainpohjaista validointisivua varten.
Sisältää kaikki epäilyttävät tapaukset audio URL:eineen ja kestoineen.

Tulos: /Users/antero/.gemini/antigravity/scratch/validointidata/epailyttavat.json
"""
import feedparser
import json
import re
import os

SUOSITUKSET = "suositukset.json"
OHITUKSET = "admin/ohitukset.json"
RSS_URL = "https://feeds.captivate.fm/uutisraportti-podcast/"
TULOS = "admin/epailyttavat.json"

TUNNETUT_NIMET = [
    "Tuomas Peltomäki", "Salla Vuorikoski", "Marko Junkkari",
    "Jussi Niemeläinen", "Anna-Sofia Berner", "Alma Onali",
    "Rasmus Helaniemi", "Helmi Sundström", "Hanna Havusto",
    "John Helin", "Sohvi Sirkesalo", "Maria Manner", "Maria Pettersson",
    "Onni Niemi", "Joakim Westrén-Doll", "Alli Hallonblad",
    "Pekka Mykkänen", "Teemu Muhonen", "Paavo Teittinen",
    "Lari Malmberg", "Anni Keski-Heikkilä", "Anni Lassila",
    "Aino Frilander", "Timo R. Stewart", "Elina Kervinen",
    "Elli Harju", "Emil Elo", "Hanna Mahlamäki",
    "Hilla Körkkä", "Jarno Hartikainen", "Tommi Nieminen",
    "Ville Similä", "Venla Kuokkanen", "Toni Lehtinen",
    "Sara Vainio", "Susanna Salmi", "Niklas Storås",
    "Matti Apunen", "Pia Elonen", "Tuija Siltamäki",
    "Tuomas Niskakangas", "Julian Puumalainen",
    "Karoliina Knuuti", "Anni Huttunen",
    "Milka Valtanen", "Matilda Jokinen", "Ida-Sofia Hirvonen",
    "Inkeri Harju", "Milla Palkoaho", "Oskari Eronen",
    "Jukka Huusko", "Joona Aaltonen", "Heini Pitkänen",
    "Irina Hala", "Ilmo Ilkka", "Jantso Jokelin",
    "Aleksi Af Heurlin", "Jaakko Lyytinen", "Harri Sulavuori",
    "Petja Pelli", "Suvi Turtiainen",
]

ETUNIMI_KARTTA = {
    "tuomas": "Tuomas Peltomäki",
    "salla": "Salla Vuorikoski",
    "marko": "Marko Junkkari",
    "jussi": "Jussi Niemeläinen",
    "anna-sofia": "Anna-Sofia Berner",
    "alma": "Alma Onali",
    "rasmus": "Rasmus Helaniemi",
    "helmi": "Helmi Sundström",
    "hanna": "Hanna Havusto",
    "john": "John Helin",
    "sohvi": "Sohvi Sirkesalo",
    "maria": "Maria Manner",
    "onni": "Onni Niemi",
    "joakim": "Joakim Westrén-Doll",
    "alli": "Alli Hallonblad",
    "pekka": "Pekka Mykkänen",
    "teemu": "Teemu Muhonen",
    "paavo": "Paavo Teittinen",
    "lari": "Lari Malmberg",
    "julian": "Julian Puumalainen",
    "anni": "Anni Lassila",
}


def poimi_osallistujat_rss(kuvaus):
    if not kuvaus:
        return []
    osallistujat = set()
    kuvaus_lower = kuvaus.lower()
    for nimi in TUNNETUT_NIMET:
        if nimi.lower() in kuvaus_lower:
            osallistujat.add(nimi)
    studio_patterns = [
        r'[Ss]tudiossa\s+([^.]+)',
        r'[Kk]eskustelevat\s+([^.]+)',
    ]
    for pattern in studio_patterns:
        match = re.search(pattern, kuvaus)
        if match:
            lause = match.group(1)
            sanat = re.findall(r'\b([A-ZÄÖÅ][a-zäöåé-]+)\b', lause)
            for sana in sanat:
                etunimi = sana.lower()
                if etunimi in ETUNIMI_KARTTA:
                    osallistujat.add(ETUNIMI_KARTTA[etunimi])
    return sorted(osallistujat)


def loytyy(suosittelija, rss_osallistujat):
    for os in rss_osallistujat:
        if suosittelija.lower() == os.lower():
            return True
        s = suosittelija.split()
        o = os.split()
        if s and o:
            if s[-1].lower() == o[-1].lower() and len(s[-1]) > 2:
                return True
            if s[0].lower() == o[0].lower() and len(s[0]) > 3:
                return True
    return False


def kesto_sekunteina(kesto_str):
    """Muuntaa HH:MM:SS tai MM:SS → sekunnit"""
    if not kesto_str:
        return 0
    osat = kesto_str.strip().split(":")
    try:
        osat = [int(x) for x in osat]
        if len(osat) == 3:
            return osat[0] * 3600 + osat[1] * 60 + osat[2]
        elif len(osat) == 2:
            return osat[0] * 60 + osat[1]
        else:
            return int(osat[0])
    except:
        return 0


def main():
    print("Ladataan RSS-syöte...")
    feed = feedparser.parse(RSS_URL)

    # Rakenna RSS-kartta: id → {audio_url, kesto_sek, osallistujat, kuvaus}
    rss_kartta = {}
    for entry in feed.entries:
        entry_id = entry.get("id", "")
        otsikko = entry.get("title", "")
        kuvaus = entry.get("summary", "") or entry.get("description", "")
        kesto_str = entry.get("itunes_duration", "")
        kesto_sek = kesto_sekunteina(kesto_str)

        # Audio URL
        audio_url = ""
        for link in entry.get("links", []):
            if link.get("type", "").startswith("audio"):
                audio_url = link["href"]
                break

        osallistujat = poimi_osallistujat_rss(kuvaus)

        rss_kartta[entry_id] = {
            "otsikko": otsikko,
            "kuvaus": kuvaus[:400],
            "audio_url": audio_url,
            "kesto_sek": kesto_sek,
            "kesto_str": kesto_str,
            "osallistujat": osallistujat,
        }

    print(f"RSS: {len(feed.entries)} jaksoa ladattu.\n")

    # Lue suositukset
    with open(SUOSITUKSET, encoding="utf-8") as f:
        data = json.load(f)

    # Lataa ohitukset
    ohitukset_set = set()
    if os.path.exists(OHITUKSET):
        with open(OHITUKSET, encoding="utf-8") as f:
            for o in json.load(f):
                ohitukset_set.add((o.get("jakso_id", ""), o.get("r_idx", -1)))

    # Ryhmittele epäilyttävät jakson mukaan
    epailyttavat_jaksot = {}

    for j_idx, jakso in enumerate(data):
        jakso_id = jakso["id"]
        jakso_otsikko = jakso["jakso_otsikko"]

        rss_info = rss_kartta.get(jakso_id)
        if not rss_info:
            # Yritä otsikolla
            for rid, rinfo in rss_kartta.items():
                if rinfo["otsikko"] == jakso_otsikko:
                    rss_info = rinfo
                    break

        if not rss_info or not rss_info.get("osallistujat"):
            continue

        rss_osallistujat = rss_info["osallistujat"]

        for r_idx, rec in enumerate(jakso.get("suositukset", [])):
            suosittelija = rec.get("suosittelija", "")
            if not suosittelija:
                continue
            if not loytyy(suosittelija, rss_osallistujat):
                # Tarkista onko ohitettu
                if (jakso_id, r_idx) in ohitukset_set:
                    continue
                # Tallenna jakso-avaimella
                if jakso_id not in epailyttavat_jaksot:
                    epailyttavat_jaksot[jakso_id] = {
                        "j_idx": j_idx,
                        "jakso_id": jakso_id,
                        "jakso_otsikko": jakso_otsikko,
                        "paivamaara": jakso.get("paivamaara", "?"),
                        "audio_url": rss_info.get("audio_url", ""),
                        "kesto_sek": rss_info.get("kesto_sek", 0),
                        "kesto_str": rss_info.get("kesto_str", ""),
                        "rss_osallistujat": rss_osallistujat,
                        "rss_kuvaus": rss_info.get("kuvaus", ""),
                        "epailyttavat_suositukset": [],
                    }
                epailyttavat_jaksot[jakso_id]["epailyttavat_suositukset"].append({
                    "r_idx": r_idx,
                    "suosittelija": suosittelija,
                    "teos": rec.get("teos", "?"),
                    "paakategoria": rec.get("paakategoria", ""),
                    "kuvaus": rec.get("kuvaus", ""),
                    "google_linkki": rec.get("google_linkki", ""),
                })

    tuloslista = list(epailyttavat_jaksot.values())
    tuloslista.sort(key=lambda x: x["paivamaara"], reverse=True)

    os.makedirs(os.path.dirname(TULOS), exist_ok=True)
    with open(TULOS, "w", encoding="utf-8") as f:
        json.dump(tuloslista, f, ensure_ascii=False, indent=2)

    # Luo myös JS-versio, jota index.html lataa
    tulos_js = TULOS.replace(".json", ".js")
    with open(tulos_js, "w", encoding="utf-8") as f:
        f.write("window.VALIDATION_DATA = ")
        json.dump(tuloslista, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"✅ Generoitu {len(tuloslista)} jaksoa, yhteensä {sum(len(j['epailyttavat_suositukset']) for j in tuloslista)} epäilyttävää suositusta.")
    print(f"   Tiedosto: {TULOS}")


if __name__ == "__main__":
    main()
