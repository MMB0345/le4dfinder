import streamlit as st
import requests
from bs4 import BeautifulSoup

# Streamlit webinterface om leads te tonen op basis van plaatsnaam
st.set_page_config(page_title="LeadFinder – Ongediertebestrijding", layout="wide")
st.title("🔍 LeadFinder – Bedrijven met kans op ongediertebestrijding")

plaats = st.text_input("Voer een plaatsnaam in", value="Gorinchem")


def scrape_bedrijven(plaats):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.telefoonboek.nl/zoeken/{plaats}/?what=restaurant"
    response = requests.get(url, headers=headers)
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

if st.button("Start zoeken"):
    st.info(f"Bedrijven worden gezocht in: {plaats}")
    resultaten = scrape_bedrijven(plaats)

    if resultaten:
        st.success(f"{len(resultaten)} bedrijven gevonden in {plaats}.")
        st.dataframe(resultaten)
    else:
        st.warning("Geen bedrijven gevonden. Probeer een andere plaats.")
