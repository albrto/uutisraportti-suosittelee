import feedparser
import json
import re
import os

RSS_URL = "https://feeds.captivate.fm/uutisraportti-podcast/"
TULOS_TIEDOSTO = "/Users/antero/Koodi/uutisraportti-web/pipeline/suositukset.json"

# ===== TUNNETUT TOIMITTAJAT =====
TUNNETUT_NIMET = [
    "Tuomas Peltomäki", "Salla Vuorikoski", "Marko Junkkari",
    "Jussi Niemeläinen", "Anna-Sofia Berner", "Alma Onali",
    "Rasmus Helaniemi", "Helmi Sundström", "Hanna Havusto",
    "John Helin", "Maria Manner", "Maria Pettersson",
    "Onni Niemi", "Joakim Westrén-Doll", "Alli Hallonblad",
    "Pekka Mykkänen", "Teemu Muhonen", "Paavo Teittinen",
    "Lari Malmberg", "Anni Keski-Heikkilä", "Anni Lassila",
    "Aino Frilander", "Timo R. Stewart", "Elina Kervinen",
    "Elli Harju", "Emil Elo", "Hanna Mahlamäki",
    "Hilla Körkkö", "Jarno Hartikainen", "Tommi Nieminen",
    "Ville Similä", "Venla Kuokkanen", "Toni Lehtinen",
    "Sara Vainio", "Susanne Salmi", "Niclas Storås",
    "Matti Apunen", "Pia Elonen", "Tuija Siltamäki",
    "Tuomas Niskakangas", "Julian Puumalainen",
    "Karoliina Knuuti", "Anni Huttunen",
    "Milka Valtanen", "Matilda Jokinen", "Iida Sofia Hirvonen",
    "Inkeri Harju", "Milla Palkoaho", "Oskari Eronen",
    "Jukka Huusko", "Joona Aaltonen", "Heini Pitkänen",
    "Irina Hasala", "Ilmo Ilkka", "Jantso Jokelin",
    "Alex af Heurlin", "Jaakko Lyytinen", "Harri Sulavuori",
    "Petja Pelli", "Suvi Turtiainen",
    "Pihla Saravirta", "Topi Kosunen", "Susanna Reinboth",
]

ETUNIMI_KARTTA = {
    "tuomas": "Tuomas Peltomäki", "salla": "Salla Vuorikoski", "marko": "Marko Junkkari",
    "jussi": "Jussi Niemeläinen", "anna-sofia": "Anna-Sofia Berner", "alma": "Alma Onali",
    "rasmus": "Rasmus Helaniemi", "helmi": "Helmi Sundström", "hanna": "Hanna Havusto",
    "john": "John Helin",
    # "Sohvi" on Anna-Sofia Bernerin lempinimi podcastissa (Sohvi Sirkesalo oli virheellinen haamunimi)
    "sohvi": "Anna-Sofia Berner", "maria": "Maria Manner",
    "onni": "Onni Niemi", "joakim": "Joakim Westrén-Doll", "alli": "Alli Hallonblad",
    "pekka": "Pekka Mykkänen", "teemu": "Teemu Muhonen", "paavo": "Paavo Teittinen",
    "lari": "Lari Malmberg", "milka": "Milka Valtanen", "julian": "Julian Puumalainen",
    # Anni Keski-Heikkilä oli podcastin vakiokasvo (ei enää HS:llä) —
    # pelkkä "Anni" vanhoissa jaksokuvauksissa viittaa häneen, ei Anni Lassilaan
    "anni": "Anni Keski-Heikkilä", "iida": "Iida Sofia Hirvonen",
    "pihla": "Pihla Saravirta", "topi": "Topi Kosunen", "susanna": "Susanna Reinboth"
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
        # Nimet voivat olla myös ENNEN verbiä: "Sohvi, Marko ja Tommi keskustelevat..."
        r'([^.]+?)\s+keskustelevat']
    for pattern in studio_patterns:
        match = re.search(pattern, kuvaus)
        if match:
            sanat = re.findall(r'\b([A-ZÄÖÅ][a-zäöåé]+(?:-[A-ZÄÖÅ][a-zäöåé]+)?)\b', match.group(1))
            for sana in sanat:
                if sana.lower() in ETUNIMI_KARTTA:
                    osallistujat.add(ETUNIMI_KARTTA[sana.lower()])
    return sorted(osallistujat)


def main():
    print("Ladataan RSS-syöte...")
    feed = feedparser.parse(RSS_URL)
    rss_kartta = {}
    for entry in feed.entries:
        audio_url = entry.enclosures[0].href if "enclosures" in entry and entry.enclosures else ""
        # Arvioidaan kesto (vapaaehtoinen lisäys UI:ta varten)
        kesto_str = str(entry.itunes_duration) if hasattr(
            entry, 'itunes_duration') else ""
        kesto_sek = 0
        if kesto_str:
            parts = kesto_str.split(':')
            if len(parts) == 3:
                kesto_sek = int(parts[0]) * 3600 + \
                    int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                kesto_sek = int(parts[0]) * 60 + int(parts[1])

        rss_kartta[entry.get("id", "")] = {
            "otsikko": entry.get("title", ""),
            "osallistujat": poimi_osallistujat_rss(entry.get("summary", "") or entry.get("description", "")),
            "audio_url": audio_url,
            "kuvaus": entry.get("summary", "") or entry.get("description", ""),
            "kesto_sek": kesto_sek,
            "kesto_str": kesto_str
        }

    with open(TULOS_TIEDOSTO, "r", encoding="utf-8") as f:
        data = json.load(f)

    tulos_jaksot = []

    for jakso in data:
        rss_info = rss_kartta.get(jakso["id"])
        if not rss_info:
            for rinfo in rss_kartta.values():
                if rinfo["otsikko"] == jakso["jakso_otsikko"]:
                    rss_info = rinfo
                    break

        if not rss_info or not rss_info["osallistujat"]:
            continue

        epailyttavat_recs = []
        for r_idx, rec in enumerate(jakso.get("suositukset", [])):
            suosittelija = rec.get("suosittelija", "")
            if not suosittelija:
                continue

            loytyy = False
            for osallistuja in rss_info["osallistujat"]:
                if suosittelija.lower() == osallistuja.lower():
                    loytyy = True
                    break
                s_osat, o_osat = suosittelija.split(), osallistuja.split()
                if s_osat and o_osat:
                    if s_osat[-1].lower() == o_osat[-1].lower() and len(s_osat[-1]) > 2:
                        loytyy = True
                        break
                    if s_osat[0].lower() == o_osat[0].lower() and len(
                            s_osat[0]) > 3:
                        loytyy = True
                        break

            # Tarkan kirjoitusasun invariantti: lähes oikea nimi (esim.
            # "Johnn Helin") ei saa mennä sukunimiosuman turvin läpi —
            # kaikki muut kuin täsmälleen tunnetut nimet liputetaan.
            if loytyy and suosittelija != "tuntematon" and suosittelija not in TUNNETUT_NIMET:
                loytyy = False

            if not loytyy:
                epailyttavat_recs.append({
                    "r_idx": r_idx,
                    "suosittelija": suosittelija,
                    "teos": rec.get("teos", "?"),
                    "kuvaus": rec.get("kuvaus", "")[:150],
                    "paakategoria": rec.get("paakategoria", "")
                })

        if epailyttavat_recs:
            # Suodatetaan pois pysyvästi ohitetut (varmistetut) tapaukset
            ohitukset_polku = os.path.join(
                os.path.dirname(TULOS_TIEDOSTO), "ohitukset.json")
            varmistetut = []
            if os.path.exists(ohitukset_polku):
                try:
                    with open(ohitukset_polku, "r", encoding="utf-8") as f:
                        varmistetut = json.load(f)
                except BaseException:
                    pass

            lopulliset_epailyttavat = []
            for e in epailyttavat_recs:
                is_ignored = False
                for v in varmistetut:
                    if v.get("jakso_id") == jakso["id"] and v.get(
                            "r_idx") == e["r_idx"]:
                        is_ignored = True
                        break
                if not is_ignored:
                    lopulliset_epailyttavat.append(e)

            if lopulliset_epailyttavat:
                rss_dict = rss_info if rss_info is not None else {}
                tulos_jaksot.append({
                    "jakso_id": str(jakso.get("id", "")),
                    "jakso_otsikko": str(jakso.get("jakso_otsikko", "")),
                    "paivamaara": str(jakso.get("paivamaara", "?")),
                    "rss_osallistujat": rss_dict.get("osallistujat", []), # type: ignore
                    "rss_kuvaus": str(rss_dict.get("kuvaus", ""))[:300] + "...",
                    "audio_url": str(rss_dict.get("audio_url", "")),
                    "kesto_sek": int(rss_dict.get("kesto_sek", 0) or 0), # type: ignore
                    "kesto_str": str(rss_dict.get("kesto_str", "")),
                    "epailyttavat_suositukset": lopulliset_epailyttavat
                })

    VALIDOINTI_DIR = "/Users/antero/Koodi/uutisraportti-web/pipeline/validointidata"
    VALIDOINTI_JS = os.path.join(VALIDOINTI_DIR, "epailyttavat.js")
    # JSON-muotoa lukevat laheta_ilmoitus.py ja korjaa_suosittelijat.py;
    # JS-muotoa validaattori-UI (index.html). Sama data, sama liputuslogiikka.
    VALIDOINTI_JSON = os.path.join(VALIDOINTI_DIR, "epailyttavat.json")

    try:
        if not os.path.exists(VALIDOINTI_DIR):
            os.makedirs(VALIDOINTI_DIR)
        with open(VALIDOINTI_JS, "w", encoding="utf-8") as f:
            f.write("window.VALIDATION_DATA = ")
            json.dump(tulos_jaksot, f, ensure_ascii=False, indent=2)
            f.write(";")
        with open(VALIDOINTI_JSON, "w", encoding="utf-8") as f:
            json.dump(tulos_jaksot, f, ensure_ascii=False, indent=2)
        print(
            f"✅ Tallennettu {
                len(tulos_jaksot)} jaksoa (yhteensä {
                sum(
                    len(
                        j['epailyttavat_suositukset']) for j in tulos_jaksot)} tapausta) tiedostoihin: {VALIDOINTI_JS} ja .json")
    except Exception as e:
        print(f"❌ Virhe: {e}")


if __name__ == "__main__":
    main()
