import streamlit as st
import requests
import pandas as pd
import urllib.parse

st.set_page_config(page_title="LeadFinder – Ongediertebestrijding", layout="wide")
st.title("🔍 LeadFinder – Bedrijven met kans op ongediertebestrijding")

plaats = st.text_input("Vul een plaatsnaam in", value="Gorinchem")

# Overpass API query opstellen (OpenStreetMap)
def build_overpass_query(plaats):
    return f"""
    [out:json];
    area[name="{plaats}"]->.zoekgebied;
    (
      node["amenity"="restaurant"](area.zoekgebied);
      node["shop"="supermarket"](area.zoekgebied);
      node["shop"="bakery"](area.zoekgebied);
      node["shop"="butcher"](area.zoekgebied);
      node["craft"="confectionery"](area.zoekgebied);
    );
    out body;
    """

# API-aanroep en verwerking
@st.cache_data(show_spinner=False)
def haal_bedrijven_op(plaats):
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
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        naam = tags.get("name", "Onbekend")
        straat = tags.get("addr:street", "")
        huisnummer = tags.get("addr:housenumber", "")
        postcode = tags.get("addr:postcode", "")
        branche = tags.get("shop") or tags.get("amenity") or tags.get("craft", "")

        adres = f"{straat} {huisnummer}, {postcode}".strip().strip(',')

        score = 5
        if branche in ["restaurant", "bakery", "butcher"]:
            score += 2
        elif branche in ["supermarket", "confectionery"]:
            score += 1

        zoek_telefoon = f"https://www.google.com/search?q=telefoonnummer+{urllib.parse.quote(naam)}+{urllib.parse.quote(plaats)}"

        bedrijven.append({
            "Bedrijfsnaam": naam,
            "Adres": adres if adres else "Onbekend",
            "Categorie": branche,
            "Leadscore": score,
            "Telefoonnummer (zoeken)": zoek_telefoon,
            "Zoek online": f"Zoek op: {naam} {plaats}"
        })

    return bedrijven

if st.button("Start zoeken"):
    st.info(f"We halen bedrijven op in de regio: {plaats}")
    resultaten = haal_bedrijven_op(plaats)
    if resultaten:
        st.success(f"{len(resultaten)} bedrijven gevonden in {plaats}.")
        st.dataframe(pd.DataFrame(resultaten))
    else:
        st.warning("Geen bedrijven gevonden. Controleer de plaatsnaam of probeer een andere regio.")
