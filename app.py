import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Arkose Analytics 2025",
    page_icon="🧗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CHARGEMENT ET NETTOYAGE DES DONNÉES (Commun à toutes les pages)
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        return None
        
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    mois_map_int = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    df["Mois"] = df["Date"].dt.month.map(mois_map_int)
    ordre_mois = list(mois_map_int.values())
    ordre_jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    df["Mois"] = pd.Categorical(df["Mois"], categories=ordre_mois, ordered=True)
    df["Jour"] = pd.Categorical(df["Jour"], categories=ordre_jours, ordered=True)
    return df

# Chargement
df = load_data("ARKOSE donnees_2025_graph.csv")

# --- BARRE LATÉRALE DE NAVIGATION ---
st.sidebar.title("🧗‍♂️ Arkose Analytics")
st.sidebar.markdown("---")

# Menu de navigation
page = st.sidebar.radio(
    "Aller vers :", 
    ["📊 Dashboard", "🤖 Automatisations", "👥 Base Clients", "⚙️ Réglages"]
)

st.sidebar.markdown("---")


# ==========================================
# PAGE 1 : DASHBOARD (Ton code précédent)
# ==========================================
def show_dashboard():
    if df is None:
        st.error("Fichier CSV introuvable.")
        return

    st.title("📊 Tableau de Bord")
    st.caption("Suivi des performances Sport & Restauration")

    # FILTRES (Spécifiques au dashboard)
    with st.expander("🔍 Filtres", expanded=False):
        mois_options = df["Mois"].unique().sort_values()
        jour_options = df["Jour"].unique().sort_values()
        
        c1, c2 = st.columns(2)
        selected_mois = c1.multiselect("Mois", options=mois_options, default=mois_options)
        selected_jours = c2.multiselect("Jours", options=jour_options, default=jour_options)

    filtered_df = df[df["Mois"].isin(selected_mois) & df["Jour"].isin(selected_jours)]

    # KPIs
    passages_totaux = filtered_df["Passage"].sum()
    couverts_servis = filtered_df["Plat"].sum()
    taux_transfo = filtered_df["% Plat"].mean()
    
    # Simulation CA
    avg_ticket_entry = 15
    avg_ticket_food = 22
    ca_total = (passages_totaux * avg_ticket_entry) + (couverts_servis * avg_ticket_food)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Chiffre d'Affaires Est.", f"{ca_total:,.0f} €")
    k2.metric("Grimpeurs", f"{passages_totaux:,.0f}")
    k3.metric("Plats Servis", f"{couverts_servis:,.0f}")
    k4.metric("Taux Conversion", f"{taux_transfo:.1f}%")

    st.markdown("---")

    # GRAPHIQUES
    tab_charts, tab_data = st.tabs(["📈 Graphiques", "📄 Données"])
    
    with tab_charts:
        # Graphique principal
        line_df = filtered_df.sort_values("Date")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=line_df['Date'], y=line_df['Passage'], name="Grimpeurs", line=dict(color='#29B6F6')), secondary_y=False)
        fig.add_trace(go.Scatter(x=line_df['Date'], y=line_df['Plat'], name="Plats", line=dict(color='#FF7043')), secondary_y=True)
        fig.update_layout(title_text="Sport vs Food", height=450)
        st.plotly_chart(fig, use_container_width=True)

        # Graphiques secondaires
        c_left, c_right = st.columns(2)
        with c_left:
            bar_grouped = filtered_df.groupby("Jour", observed=True)["Passage"].mean().reset_index()
            fig_bar = px.bar(bar_grouped, x="Jour", y="Passage", title="Affluence Hebdo", color="Passage")
            st.plotly_chart(fig_bar, use_container_width=True)
        with c_right:
            labels = ['Sport', 'Food']
            values = [passages_totaux * avg_ticket_entry, couverts_servis * avg_ticket_food]
            fig_pie = px.pie(names=labels, values=values, title="Répartition CA", hole=0.4, color_discrete_sequence=['#29B6F6', '#FF7043'])
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab_data:
        st.dataframe(filtered_df, use_container_width=True)


# ==========================================
# PAGE 2 : AUTOMATISATIONS (Documentation)
# ==========================================
def show_automations():
    st.title("🤖 Centre d'Automatisation (n8n)")
    st.info("Cette page permet de surveiller l'état des workflows marketing.")

    # Simulation d'un statut live
    c1, c2, c3 = st.columns(3)
    c1.success("🟢 Acquisition (Actif)")
    c2.warning("🟡 Conversion (En pause)")
    c3.success("🔵 Fidélisation (Actif)")

    st.subheader("Historique récent")
    st.table(pd.DataFrame({
        "Date": ["Aujourd'hui 10:00", "Hier 14:00", "Hier 09:00"],
        "Workflow": ["Conversion Resto", "Relance J+21", "Acquisition"],
        "Statut": ["✅ Succès", "✅ Succès", "⚠️ Alerte Slack envoyée"],
        "Détail": ["Ratio 12% détecté", "3 emails envoyés", "Créneau vide mardi"]
    }))

# ==========================================
# PAGE 3 : CLIENTS (CRM Simplifié)
# ==========================================
def show_clients():
    st.title("👥 Base Clients")
    st.write("Gestion simplifiée des profils grimpeurs.")
    
    # Faux tableau CRM pour l'exemple
    crm_data = pd.DataFrame({
        "Nom": ["Dupont", "Martin", "Durand", "Petit"],
        "Prénom": ["Jean", "Sophie", "Luc", "Emma"],
        "Dernière Visite": ["2025-01-12", "2025-01-10", "2024-12-20", "2025-01-14"],
        "Statut": ["Actif", "Actif", "🔴 À relancer", "Nouveau"],
        "Abonnement": ["Infinity", "Carnet 10", "Aucun", "Infinity"]
    })
    
    st.dataframe(
        crm_data, 
        use_container_width=True,
        column_config={
            "Statut": st.column_config.SelectboxColumn(
                "Statut",
                options=["Actif", "🔴 À relancer", "Nouveau"],
                width="medium"
            )
        }
    )

# ==========================================
# PAGE 4 : RÉGLAGES
# ==========================================
def show_settings():
    st.title("⚙️ Réglages de l'application")
    
    st.subheader("Hypothèses Financières")
    c1, c2 = st.columns(2)
    c1.number_input("Prix moyen Entrée (€)", value=15.0)
    c2.number_input("Prix moyen Plat (€)", value=15.5)
    
    st.subheader("Connexions API")
    st.text_input("Clé API Google Sheets", type="password")
    st.text_input("Webhook Slack", type="password")
    
    st.button("Sauvegarder les paramètres")

# ==========================================
# ROUTAGE (Le "Cerveau" de la navigation)
# ==========================================
if page == "📊 Dashboard":
    show_dashboard()
elif page == "🤖 Automatisations":
    show_automations()
elif page == "👥 Base Clients":
    show_clients()
elif page == "⚙️ Réglages":
    show_settings()