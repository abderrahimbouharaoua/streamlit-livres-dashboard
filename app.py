import streamlit as st
from app_ui import LivreDashboardApp

# Configuration de la page Streamlit
st.set_page_config(page_title="📚 Dashboard Livres", layout="wide")

# Créer une instance de l'application orientée objet
dashboard_app = LivreDashboardApp()

# Démarrer l'application
dashboard_app.run()
