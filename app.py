@st.cache_data(ttl=600)
def haal_bedrijven_op(plaats):
    if not plaats:
        return []
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = build_overpass_query(plaats)
    try:
        response = requests.post(overpass_url, data=query, timeout=25)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        st.error(f"Fout bij het ophalen van gegevens: {e}")
        return []

    bedrijven = []
    grote_ketens = ["Albert Heijn", "Jumbo", "Lidl", "PLUS", "Aldi", "Coop"]
    branche_map = {
        "hospital": "Ziekenhuis",
        "pharmacy": "Apotheek",
        "school": "School",
        "kindergarten": "Kinderdagverblijf",
        "restaurant": "Restaurant",
        "cafe": "Café",
        "bar": "Bar",
        "fast_food": "Fastfood",
        "pub": "Pub",
        "biergarten": "Biergarten",
        "hotel": "Hotel",
        "bakery": "Bakkerij",
        "butcher": "Slager",
        "supermarket": "Supermarkt",
        "confectionery": "Zoetwaren",
        "food": "Voedselfabriek",
        "works": "Productielocatie",
        "bowling_alley": "Bowlingbaan",
        "Onbekend": "Onbekend"
    }

    for element in data.get("elements", []):
        tags = element.get("tags", {})

        # Geavanceerde check voor gesloten locaties
        if any(k.startswith(("disused:", "abandoned:", "was:")) for k in tags.keys()):
            continue
        if tags.get("disused") == "yes" or tags.get("abandoned") == "yes" or tags.get("closed") == "yes":
            continue

        if "name" not in tags or not tags.get("name").strip():
            continue

        naam = tags.get("name")
        straat = tags.get("addr:street", "")
        huisnummer = tags.get("addr:housenumber", "")
        postcode = tags.get("addr:postcode", "")

        branche_raw = (
            tags.get("shop") or
            tags.get("amenity") or
            tags.get("craft") or
            tags.get("tourism") or
            tags.get("leisure") or
            "Onbekend"
        )
        branche = branche_map.get(branche_raw, branche_raw.capitalize())

        if branche == "Supermarkt" and any(k in naam for k in grote_ketens):
            continue

        adres = f"{straat} {huisnummer}, {postcode}".strip().strip(',')

        score = 5
        if branche_raw in ["restaurant", "cafe", "bar", "fast_food", "pub", "biergarten", "bakery", "butcher"]:
            score += 2
        elif branche_raw in ["supermarket", "confectionery", "hotel"]:
            score += 1

        zoek_telefoon = f'<a href="https://www.google.com/search?q=telefoonnummer+{urllib.parse.quote(naam)}+{urllib.parse.quote(plaats)}" target="_blank">KLIK</a>'
        
        bedrijven.append({
            "Naam instelling": naam,
            "Adres": adres if adres else "Onbekend",
            "Categorie": branche,
            "Leadscore": score,
            "Telefoonnummer": zoek_telefoon
        })

    return bedrijven
