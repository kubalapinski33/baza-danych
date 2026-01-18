import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
# Dane pobierane są z "Secrets" w Streamlit Cloud lub pliku .env lokalnie
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Zarządzanie Magazynem", layout="wide")
st.title("📦 System Zarządzania Produktami")

# --- FUNKCJE POMOCNICZE ---
def get_categories():
    response = supabase.table("kategorie").select("*").execute()
    return response.data

def get_products():
    # Pobieramy produkty wraz z nazwą kategorii (Join)
    response = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    return response.data

# --- SIDEBAR: DODAWANIE KATEGORII ---
with st.sidebar:
    st.header("➕ Dodaj Kategorię")
    kat_nazwa = st.text_input("Nazwa kategorii")
    kat_opis = st.text_area("Opis kategorii")
    if st.button("Dodaj Kategorię"):
        if kat_nazwa:
            supabase.table("kategorie").insert({"nazwa": kat_nazwa, "opis": kat_opis}).execute()
            st.success(f"Dodano kategorię: {kat_nazwa}")
            st.rerun()
        else:
            st.error("Nazwa jest wymagana!")

# --- GŁÓWNY PANEL: PRODUKTY ---
col1, col2 = st.columns([2, 1])

with col2:
    st.header("➕ Dodaj Produkt")
    kategorie = get_categories()
    kat_opcje = {k['nazwa']: k['id'] for k in kategorie}
    
    p_nazwa = st.text_input("Nazwa produktu")
    p_liczba = st.number_input("Liczba", min_value=0, step=1)
    p_cena = st.number_input("Cena", min_value=0.0, format="%.2f")
    p_kat = st.selectbox("Kategoria", options=list(kat_opcje.keys()))
    
    if st.button("Dodaj Produkt"):
        if p_nazwa:
            data = {
                "nazwa": p_nazwa,
                "liczba": p_liczba,
                "cena": p_cena,
                "kategoria_id": kat_opcje[p_kat]
            }
            supabase.table("produkty").insert(data).execute()
            st.success("Produkt dodany!")
            st.rerun()

with col1:
    st.header("📋 Lista Produktów")
    produkty = get_products()
    
    if produkty:
        for p in produkty:
            with st.expander(f"{p['nazwa']} ({p['kategorie']['nazwa']})"):
                st.write(f"Ilość: {p['liczba']} | Cena: {p['cena']} zł")
                if st.button(f"Usuń {p['nazwa']}", key=f"del_{p['id']}"):
                    supabase.table("produkty").delete().eq("id", p['id']).execute()
                    st.success("Usunięto!")
                    st.rerun()
    else:
        st.info("Brak produktów w bazie.")

# --- SEKCJA USUWANIA KATEGORII ---
st.divider()
st.header("🗑️ Usuń Kategorię")
if kategorie:
    del_kat_name = st.selectbox("Wybierz kategorię do usunięcia", options=[k['nazwa'] for k in kategorie])
    if st.button("Usuń wybraną kategorię"):
        target_id = kat_opcje[del_kat_name]
        # Uwaga: Supabase wyrzuci błąd, jeśli kategoria ma przypisane produkty (klucz obcy)
        try:
            supabase.table("kategorie").delete().eq("id", target_id).execute()
            st.success("Kategoria usunięta!")
            st.rerun()
        except Exception as e:
            st.error("Nie można usunąć kategorii, która zawiera produkty!")
