import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import zipfile
from scrapper import BookScraper
from sauvegarder import Sauvegarde

class LivreDashboardApp:
    def __init__(self):
        self.page = st.session_state.get("page", "accueil")
        self.data_scraped = st.session_state.get("data_scraped", False)

    @st.cache_data(show_spinner=False)
    def run_scraping(self):
        scraper = BookScraper()
        return scraper.scrape_books()

    @st.cache_data(show_spinner=False)
    def load_data(self):
        try:
            return pd.read_csv("books_data.csv")
        except FileNotFoundError:
            st.error("❌ Fichier books_data.csv introuvable. Veuillez scraper les données d'abord.")
            return pd.DataFrame()

    def page_accueil(self):
        st.title("📚 Bienvenue sur l'application de Web Scraping de livres")

        st.markdown("""
        Cette application permet de :
        - 🔎 Scraper des livres depuis [books.toscrape.com](http://books.toscrape.com)
        - 📊 Visualiser les données sous forme de graphiques interactifs
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔎 Scraper les données"):
                with st.spinner("Scraping en cours..."):
                    data = self.run_scraping()
                    sauvegarde = Sauvegarde(data)
                    sauvegarde.to_csv("books_data.csv")
                    st.session_state.data_scraped = True
                    st.success("✅ Données scrapées et enregistrées dans books_data.csv")

        with col2:
            if st.button("📊 Voir le tableau de bord"):
                if not st.session_state.get("data_scraped", False):
                    st.warning("⚠️ Vous devez d'abord scraper les données.")
                else:
                    st.session_state.page = "dashboard"
                    st.rerun()

    def page_dashboard(self):
        st.title("📊 Tableau de bord - Livres scrapés")

        df = self.load_data()
        if df.empty:
            st.warning("Aucune donnée disponible. Revenez à l'accueil pour scraper.")
            return

        col1, col2 = st.columns(2)
        with col1:
            selected_note = st.selectbox("🎯 Filtrer par note (étoiles)", sorted(df["Note (étoiles)"].unique()))
        with col2:
            prix_max = st.slider("💰 Prix maximal (£)", float(df["Prix (£)"].min()), float(df["Prix (£)"].max()), float(df["Prix (£)"].max()))

        filtered_df = df[(df["Note (étoiles)"] == selected_note) & (df["Prix (£)"] <= prix_max)]

        st.subheader("📑 Statistiques descriptives")
        st.dataframe(filtered_df.describe(), use_container_width=True)

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

        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="png")
        buf1.seek(0)

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png")
        buf2.seek(0)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("distribution_prix.png", buf1.read())
            zf.writestr("distribution_notes.png", buf2.read())
        zip_buffer.seek(0)

        st.download_button("📥 Télécharger les graphiques (PNG)", zip_buffer, "graphique_livres.zip", "application/zip")

        st.subheader("📚 Détail des livres filtrés")
        st.dataframe(filtered_df, use_container_width=True)

        st.download_button("📥 Télécharger les données filtrées", filtered_df.to_csv(index=False).encode("utf-8"), "livres_filtres.csv", "text/csv")

        if st.button("🏠 Retour à l'accueil"):
            st.session_state.page = "accueil"
            st.rerun()

    def run(self):
        if st.session_state.get("page", "accueil") == "accueil":
            self.page_accueil()
        elif st.session_state.get("page") == "dashboard":
            self.page_dashboard()
