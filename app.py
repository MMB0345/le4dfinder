import streamlit as st

# Streamlit webinterface om leads te tonen op basis van plaatsnaam
st.set_page_config(page_title="LeadFinder – Ongediertebestrijding", layout="wide")
st.title("🔍 LeadFinder – Bedrijven met kans op ongediertebestrijding")

plaats = st.text_input("Voer een plaatsnaam in", value="Gorinchem")

def scrape_bedrijven(plaats):
    # Simuleer data voor demo-doeleinden
    voorbeeld_data = [
        {"Bedrijf": "Bistro Piccolo", "Adres": "Korenbrugstraat 28, Gorinchem", "Leadscore": 8, "Contactoptie": "Zoek op: Bistro Piccolo"},
        {"Bedrijf": "De Malle Molen", "Adres": "Arkelstraat 90, Gorinchem", "Leadscore": 7, "Contactoptie": "Zoek op: De Malle Molen"},
        {"Bedrijf": "Il Sole", "Adres": "Van Hoornestraat 22, Gorinchem", "Leadscore": 7, "Contactoptie": "Zoek op: Il Sole"},
        {"Bedrijf": "Warung Jannie", "Adres": "Burgstraat 24, Gorinchem", "Leadscore": 6, "Contactoptie": "Zoek op: Warung Jannie"},
        {"Bedrijf": "Nieuw Oosten City", "Adres": "Twijnderstraat 23, Gorinchem", "Leadscore": 6, "Contactoptie": "Zoek op: Nieuw Oosten City"},
        {"Bedrijf": "Délifrance", "Adres": "Piazza Center 7, Gorinchem", "Leadscore": 5, "Contactoptie": "Zoek op: Délifrance"}
    ]
    return voorbeeld_data

if st.button("Start zoeken"):
    st.info(f"Bedrijven worden gezocht in: {plaats}")
    resultaten = scrape_bedrijven(plaats)

    if resultaten:
        st.success(f"{len(resultaten)} bedrijven gevonden in {plaats}.")
        st.dataframe(resultaten)
    else:
        st.warning("Geen bedrijven gevonden. Probeer een andere plaats.")
