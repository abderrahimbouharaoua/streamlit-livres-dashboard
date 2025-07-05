import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import zipfile
from scrapper import BookScraper
from sauvegarder import Sauvegarde

# ------------------ IMPORTS css------------------ #
# --- CSS PERSONNALISÉ POUR STYLE ET FOND ---


# Configuration de la page Streamlit
st.set_page_config(page_title="📚 Dashboard Livres", layout="wide")

# ------------------ INITIALISATION DE LA SESSION ------------------ #
# On initialise des variables dans session_state pour gérer la navigation et le statut du scraping
if "page" not in st.session_state:
    st.session_state.page = "accueil"  # Page par défaut
if "data_scraped" not in st.session_state:
    st.session_state.data_scraped = False  # Indique si les données ont été scrapées

# ------------------ FONCTION DE SCRAPING AVEC CACHE ------------------ #
@st.cache_data(show_spinner=False)
def run_scraping():
    """
    Lance le scraping des livres et met en cache le résultat
    pour éviter de refaire ce calcul à chaque exécution.
    """
    scraper = BookScraper()
    return scraper.scrape_books()

# ------------------ FONCTION DE CHARGEMENT DE DONNÉES AVEC CACHE ------------------ #
@st.cache_data(show_spinner=False)
def load_data():
    """
    Charge le fichier CSV books_data.csv en cache pour éviter
    de relire le fichier à chaque interaction.
    """
    try:
        return pd.read_csv("books_data.csv")
    except FileNotFoundError:
        st.error("❌ Fichier books_data.csv introuvable. Veuillez scraper les données d'abord.")
        return pd.DataFrame()

# ------------------ PAGE D'ACCUEIL ------------------ #
def page_accueil():
    st.title("📚 Bienvenue sur l'application de Web Scraping de livres")

    st.markdown("""
    Cette application permet de :
    - 🔎 Scraper des livres depuis [books.toscrape.com](http://books.toscrape.com)
    - 📊 Visualiser les données sous forme de graphiques interactifs
    """)

    # Création de deux colonnes pour les boutons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔎 Scraper les données"):
            # Quand on clique sur scraper, on lance la fonction de scraping
            with st.spinner("Scraping en cours..."):
                data = run_scraping()
                # Sauvegarde les données scrapées dans un fichier CSV
                sauvegarde = Sauvegarde(data)
                sauvegarde.to_csv("books_data.csv")
                st.session_state.data_scraped = True  # Mise à jour de l'état
                st.success("✅ Données scrapées et enregistrées dans books_data.csv")

    with col2:
        if st.button("📊 Voir le tableau de bord"):
            # Avant d'aller au dashboard, on vérifie que les données existent
            if not st.session_state.data_scraped:
                st.warning("⚠️ Vous devez d'abord scraper les données.")
            else:
                # Changement de page vers dashboard et rechargement de l'app
                st.session_state.page = "dashboard"
                st.rerun()

# ------------------ PAGE TABLEAU DE BORD ------------------ #
def page_dashboard():
    st.title("📊 Tableau de bord - Livres scrapés")

    # Chargement des données avec cache
    df = load_data()
    if df.empty:
        st.warning("Aucune donnée disponible. Revenez à l'accueil pour scraper.")
        return

    # Création de deux colonnes pour les filtres
    col1, col2 = st.columns(2)
    with col1:
        # Filtrage par note (étoiles)
        selected_note = st.selectbox("🎯 Filtrer par note (étoiles)", sorted(df["Note (étoiles)"].unique()))
    with col2:
        # Filtrage par prix maximum avec un slider
        prix_max = st.slider("💰 Prix maximal (£)", float(df["Prix (£)"].min()), float(df["Prix (£)"].max()), float(df["Prix (£)"].max()))

    # Application des filtres
    filtered_df = df[(df["Note (étoiles)"] == selected_note) & (df["Prix (£)"] <= prix_max)]

    # Affichage des statistiques descriptives du dataframe filtré
    st.subheader("📑 Statistiques descriptives")
    st.dataframe(filtered_df.describe(), use_container_width=True)

    # Affichage des graphiques dans deux colonnes
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 📈 Distribution des prix")
        fig1, ax1 = plt.subplots()
        ax1.hist(filtered_df["Prix (£)"], bins=10, color='skyblue')
        ax1.set_xlabel("Prix (£)")
        ax1.set_ylabel("Nombre de livres")
        ax1.set_title("Distribution des prix")
        st.pyplot(fig1)
        st.caption("💡 Ce graphique montre combien de livres se trouvent dans chaque tranche de prix.")

    with col4:
        st.markdown("#### ⭐ Répartition des notes")
        fig2, ax2 = plt.subplots()
        ax2.hist(filtered_df["Note (étoiles)"], bins=5, color='orange', rwidth=0.9)
        ax2.set_xlabel("Note (étoiles)")
        ax2.set_ylabel("Nombre de livres")
        ax2.set_title("Distribution des notes")
        st.pyplot(fig2)
        st.caption("💡 Ce graphique montre la répartition des livres selon leur note en étoiles.")

    # Préparation des images PNG des graphiques en mémoire
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png")
    buf1.seek(0)

    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)

    # Création d'un fichier ZIP en mémoire contenant les deux images
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("distribution_prix.png", buf1.read())
        zf.writestr("distribution_notes.png", buf2.read())
    zip_buffer.seek(0)

    # Bouton pour télécharger le ZIP des graphiques PNG
    st.download_button(
        label="📥 Télécharger les graphiques (PNG)",
        data=zip_buffer,
        file_name="graphique_livres.zip",
        mime="application/zip"
    )

    # Affichage du tableau des livres filtrés
    st.subheader("📚 Détail des livres filtrés")
    st.dataframe(filtered_df, use_container_width=True)

    # Bouton pour télécharger les données filtrées en CSV
    st.download_button(
        label="📥 Télécharger les données filtrées",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="livres_filtres.csv",
        mime="text/csv"
    )

    # Bouton pour revenir à la page d'accueil
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = "accueil"
        st.rerun()

# ------------------ ROUTEUR DE PAGES ------------------ #
# Affiche la page d'accueil ou le dashboard selon la valeur dans session_state
if st.session_state.page == "accueil":
    page_accueil()
elif st.session_state.page == "dashboard":
    page_dashboard()
