import streamlit as st
import requests
import pandas as pd
import urllib.parse
import io

st.set_page_config(page_title="LeadFinder - Let's Go Pest Control", layout="wide")
st.markdown("""
    <style>
    .mouse-run {
        position: fixed;
        top: 20px;
        left: -150px;
        width: 100px;
        z-index: 9999;
        animation: runmouse 3s linear forwards;
    }
    
    @keyframes runmouse {
        from { left: -150px; }
        to { left: 100%; }
    }
    </style>
    <img src='https://le4dfinder.streamlit.app/files/f40aa35a-8787-4044-ac3e-9286b9b4b6d3.png' class='mouse-run'>
    """, unsafe_allow_html=True)

st.title("🔍 LeadFinder - Let's Go Pest Control")

plaats = st.text_input("Vul een plaatsnaam of provincie in", value="Gorinchem").strip().capitalize()

# Overpass API query opstellen (OpenStreetMap)
def build_overpass_query(plaats):
    return f"""
    [out:json];
    area[name=\"{plaats}\"]->.zoekgebied;
    (
      node[\"amenity\"=\"hospital\"](area.zoekgebied);
      node[\"amenity\"=\"pharmacy\"](area.zoekgebied);
      node[\"amenity\"=\"school\"](area.zoekgebied);
      node[\"amenity\"=\"kindergarten\"](area.zoekgebied);
      node[\"shop\"=\"supermarket\"](area.zoekgebied);
      node[\"shop\"=\"bakery\"](area.zoekgebied);
      node[\"shop\"=\"butcher\"](area.zoekgebied);
      node[\"craft\"=\"confectionery\"](area.zoekgebied);
      node[\"industrial\"=\"food\"](area.zoekgebied);
      node[\"man_made\"=\"works\"](area.zoekgebied);
    );
    out body;
    """

# API-aanroep en verwerking
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
    grote_ketens = ["Albert Heijn", "Jumbo", "Lidl", "PLUS", "Aldi", "Coop"]
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        naam = tags.get("name", "Onbekend")
        straat = tags.get("addr:street", "")
        huisnummer = tags.get("addr:housenumber", "")
        postcode = tags.get("addr:postcode", "")
        branche_raw = tags.get("shop") or tags.get("amenity") or tags.get("craft", "")
        branche_map = {
            "hospital": "Ziekenhuis",
            "pharmacy": "Apotheek",
            "school": "School",
            "kindergarten": "Kinderdagverblijf",
            "restaurant": "Restaurant",
            "bakery": "Bakkerij",
            "butcher": "Slager",
            "supermarket": "Supermarkt",
            "confectionery": "Zoetwaren",
            "food": "Voedselfabriek",
            "works": "Productielocatie"
        }
        branche = branche_map.get(branche_raw, branche_raw.capitalize())

        # Grote supermarktketens overslaan
        if branche == "Supermarkt" and any(k in naam for k in grote_ketens):
            continue

        adres = f"{straat} {huisnummer}, {postcode}".strip().strip(',')

        score = 5
        if branche_raw in ["restaurant", "bakery", "butcher"]:
            score += 2
        elif branche_raw in ["supermarket", "confectionery"]:
            score += 1

        zoek_telefoon = f'<a href="https://www.google.com/search?q=telefoonnummer+{naam.replace(" ", "+")}+{plaats.replace(" ", "+")}" target="_blank">KLIK</a>'
        
        if adres != "Onbekend":
            bedrijven.append({
            "Naam instelling": naam,
            "Adres": adres if adres else "Onbekend",
            "Categorie": branche,
            "Leadscore": score,
            "Telefoonnummer": zoek_telefoon
        })

    return bedrijven

if st.button("Start zoeken"):
    st.info(f"We halen bedrijven op in de regio: {plaats}")
    resultaten = haal_bedrijven_op(plaats)
    if resultaten:
        st.success(f"{len(resultaten)} bedrijven gevonden in {plaats}.")
        df_resultaat = pd.DataFrame(resultaten)

        # Sidebar filters
        st.sidebar.header("🔎 Filters")
        unieke_categorieen = sorted(df_resultaat['Categorie'].unique())
        gekozen_categorie = st.sidebar.selectbox("Filter op categorie", ["Alles"] + unieke_categorieen)
        if gekozen_categorie != "Alles":
            df_resultaat = df_resultaat[df_resultaat['Categorie'] == gekozen_categorie]
        
        # Samenvatting
        st.markdown(f"### 📊 {len(df_resultaat)} resultaten met gemiddelde score van {df_resultaat['Leadscore'].mean():.1f}")

        # Leadscore visueel
        def score_icoon(score):
            if score >= 7:
                return f"🟢 {score}"
            elif score >= 6:
                return f"🟡 {score}"
            else:
                return f"🔴 {score}"
        df_resultaat['Leadscore'] = df_resultaat['Leadscore'].apply(score_icoon)

        # Data tonen
        # Data tonen als HTML-tabel met werkende links
        st.markdown(df_resultaat.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Downloadknop voor Excel-export
        excel_buffer = io.BytesIO()
        df_resultaat.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        st.download_button(
            label="📥 Download als Excel-bestand",
            data=excel_buffer,
            file_name=f"leadfinder_{plaats.lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Geen bedrijven gevonden. Controleer de plaatsnaam of probeer een andere regio.")
