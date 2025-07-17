try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print("Benodigde module ontbreekt: ", e)
    print("Installeer dependencies met: pip install requests beautifulsoup4")
    exit()

def scrape_bedrijven(plaats):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.telefoonboek.nl/zoeken/{plaats}/?what=restaurant"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Fout bij het ophalen van gegevens: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    bedrijven = []
    for item in soup.select(".search-item__content"):
        naam_tag = item.select_one("h2.heading")
        adres_tag = item.select_one("div.contact-item__address")

        naam = naam_tag.text.strip() if naam_tag else "Onbekend"
        adres = adres_tag.text.strip().replace("\n", " ") if adres_tag else "-"

        score = 5
        if any(x in naam.lower() for x in ['restaurant', 'bistro', 'brasserie']):
            score += 2
        if any(x in naam.lower() for x in ['hotel', 'grill', 'catering']):
            score += 1

        bedrijven.append({
            "Bedrijf": naam,
            "Adres": adres,
            "Leadscore": score,
            "Contactoptie": f"Zoek op: {naam}"
        })

    return bedrijven

if __name__ == "__main__":
    plaats = "Gorinchem"
    print(f"Zoeken naar bedrijven in: {plaats}\n")
    resultaten = scrape_bedrijven(plaats)

    if resultaten:
        print(f"{len(resultaten)} bedrijven gevonden in {plaats}:")
        for r in resultaten:
            print(f"- {r['Bedrijf']} | {r['Adres']} | Leadscore: {r['Leadscore']} | {r['Contactoptie']}")
    else:
        print("Geen bedrijven gevonden. Probeer een andere plaats of controleer je internetverbinding.")