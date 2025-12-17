import json
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
)

# 2. CHARGEMENT ET NETTOYAGE DES DONNÉES
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    mois_map_int = {
        1: "Janvier",
        2: "Février",
        3: "Mars",
        4: "Avril",
        5: "Mai",
        6: "Juin",
        7: "Juillet",
        8: "Août",
        9: "Septembre",
        10: "Octobre",
        11: "Novembre",
        12: "Décembre",
    }

    df["Mois"] = df["Date"].dt.month.map(mois_map_int)

    ordre_mois = list(mois_map_int.values())
    ordre_jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    df["Mois"] = pd.Categorical(df["Mois"], categories=ordre_mois, ordered=True)
    df["Jour"] = pd.Categorical(df["Jour"], categories=ordre_jours, ordered=True)

    return df


@st.cache_data
def load_workflow(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

try:
    df = load_data("ARKOSE donnees_2025_graph.csv")
except FileNotFoundError:
    st.error("⚠️ Fichier CSV introuvable. Veuillez vérifier le nom du fichier.")
    st.stop()

# 3. SIDEBAR (FILTRES)
st.sidebar.title("🔍 Filtres")
mois_options = df["Mois"].unique().sort_values()
jour_options = df["Jour"].unique().sort_values()

selected_mois = st.sidebar.multiselect("📅 Mois", options=mois_options, default=mois_options)
selected_jours = st.sidebar.multiselect("📆 Jours", options=jour_options, default=jour_options)

filtered_df = df[df["Mois"].isin(selected_mois) & df["Jour"].isin(selected_jours)]

# 4. TITRE ET KPIs
st.title("🧗 Arkose Analytics 2025")
st.markdown("---")

# --- AJOUT SECTION FINANCIÈRE (Basée sur Tarifs Réels) ---
st.markdown("---")
st.header("💶 Analyse Financière & Rentabilité")

with st.expander("⚙️ Modifier les hypothèses de prix (Tarifs 2025)", expanded=True):
    col_conf1, col_conf2, col_conf3 = st.columns(3)

    avg_price_entry = col_conf1.number_input(
        "Rev. Moy./Grimpeur (€)",
        value=15.0,
        step=0.5,
        help="Moyenne pondérée entre séance unitaire (18€), carnet 10 (15€) et abonnements.",
    )

    avg_price_dish = col_conf2.number_input("Prix Moyen Plat (€)", value=15.5, step=0.5)

    avg_price_snack = col_conf3.number_input("Prix Moy. Snack/Entrée (€)", value=7.0, step=0.5)

revenue_sport = filtered_df["Passage"] * avg_price_entry
revenue_food = (filtered_df["Plat"] * avg_price_dish) + (filtered_df["Entrée"] * avg_price_snack)
total_revenue = revenue_sport + revenue_food

col_fin1, col_fin2, col_fin3 = st.columns(3)

col_fin1.metric(
    "💰 Chiffre d'Affaires Estimé",
    f"{total_revenue.sum():,.0f} €",
    help="CA Sport + CA Resto sur la période sélectionnée",
)

food_share = (revenue_food.sum() / total_revenue.sum()) * 100 if total_revenue.sum() > 0 else 0
col_fin2.metric(
    "🍔 Part du CA Restauration",
    f"{food_share:.1f} %",
    delta="Objectif : 25%",
    delta_color="off",
)

passage_sum = filtered_df["Passage"].sum()
avg_spend_per_visitor = total_revenue.sum() / passage_sum if passage_sum else 0
col_fin3.metric(
    "💳 Dépense Moyenne / Visiteur",
    f"{avg_spend_per_visitor:.2f} €" if passage_sum else "N/A",
    help="CA Total divisé par le nombre de grimpeurs",
)

# --- ANALYSE FINANCIÈRE AVANCÉE (Mix Produit) ---
st.markdown("---")
st.header("💶 Simulateur de Chiffre d'Affaires (Mix Clients)")

st.info("💡 Le CSV ne distinguant pas les types de clients, utilisons ce simulateur pour estimer la répartition.")

col_mix1, col_mix2, col_mix3 = st.columns(3)

with col_mix1:
    st.subheader("💳 Abonnés (Infinity)")
    price_sub = st.number_input("Rev. moyen/séance Abonné (€)", value=10.0, step=0.5)
    pct_sub = st.slider("% de la fréquentation (Abonnés)", 0, 100, 40) / 100

with col_mix2:
    st.subheader("🎟️ Carnets (10 sessions)")
    price_pack = st.number_input("Prix séance Carnet (€)", value=15.0, step=0.5)
    pct_pack = st.slider("% de la fréquentation (Carnets)", 0, 100, 30) / 100

with col_mix3:
    st.subheader("🎫 Unitaires / Autres")
    price_unit = st.number_input("Prix séance Unitaire (€)", value=17.0, step=0.5)
    pct_unit = max(0.0, 1.0 - (pct_sub + pct_pack))
    st.metric("Reste (Unitaires)", f"{pct_unit*100:.0f}%")
    st.progress(pct_unit)

if pct_sub + pct_pack + pct_unit > 1.0:
    st.error("⚠️ Attention : Le total des pourcentages dépasse 100% !")

avg_weighted_price = (price_sub * pct_sub) + (price_pack * pct_pack) + (price_unit * pct_unit)

st.caption(f"🏁 Prix moyen pondéré par grimpeur calculé : **{avg_weighted_price:.2f} €**")

avg_price_dish = 15.5
avg_price_snack = 7.0

rev_sport_mix = filtered_df["Passage"] * avg_weighted_price
rev_food_mix = (filtered_df["Plat"] * avg_price_dish) + (filtered_df.get("Entrée", 0) * avg_price_snack)
total_rev_mix = rev_sport_mix + rev_food_mix

m1, m2, m3 = st.columns(3)
m1.metric("💰 CA Total Estimé", f"{total_rev_mix.sum():,.0f} €")
m2.metric("🧗 Dont Escalade", f"{rev_sport_mix.sum():,.0f} €", delta="Base Sport")
share_food_mix = (rev_food_mix.sum() / total_rev_mix.sum()) * 100 if total_rev_mix.sum() > 0 else 0
m3.metric("🍔 Dont Restauration", f"{rev_food_mix.sum():,.0f} €", delta=f"{share_food_mix:.1f}% du CA")

passages_totaux = filtered_df["Passage"].sum()
couverts_servis = filtered_df["Plat"].sum()
taux_transfo = filtered_df["% Plat"].mean()
affluence_moy = filtered_df["Total_jour"].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Grimpeurs Totaux", f"{passages_totaux:,.0f}")
kpi2.metric("Plats Servis", f"{couverts_servis:,.0f}")
kpi3.metric("Taux Conv. Resto", f"{taux_transfo:.1f}%")
kpi4.metric("Affluence Moy./Jour", f"{affluence_moy:.0f}")

st.markdown("---")

# 5. ZONE PRINCIPALE (ONGLETS)
tab_charts, tab_data, tab_ops = st.tabs(["📊 Tableaux de bord", "📝 Données brutes", "🤖 Automations n8n"])

with tab_charts:
    st.markdown("### 📉 Analyse simplifiée : Flux vs Ventes")

    weekly_df = (
        filtered_df.set_index("Date")
        .resample("W")
        .agg({"Passage": "sum", "Plat": "sum", "Total_jour": "sum"})
        .reset_index()
    )
    weekly_df["Taux_Conversions"] = (
        (weekly_df["Plat"] / weekly_df["Passage"].replace(0, pd.NA)) * 100
    ).fillna(0)

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            "🌊 Flux Grimpeurs (Volume)",
            "🍔 Ventes Resto (Volume)",
            "🎯 Efficacité Commerciale (% qui mangent)",
        ),
        row_heights=[0.4, 0.3, 0.3],
    )

    fig.add_trace(
        go.Scatter(
            x=weekly_df["Date"],
            y=weekly_df["Passage"],
            fill="tozeroy",
            name="Grimpeurs",
            line=dict(color="#29B6F6", width=2),
            hovertemplate="%{y} grimpeurs<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=weekly_df["Date"],
            y=weekly_df["Plat"],
            name="Plats",
            marker_color="#FF7043",
            hovertemplate="%{y} plats<extra></extra>",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=weekly_df["Date"],
            y=weekly_df["Taux_Conversions"],
            name="Taux Conv. %",
            line=dict(color="#66BB6A", width=3),
            mode="lines+markers",
            hovertemplate="%{y:.1f}% ont mangé<extra></extra>",
        ),
        row=3,
        col=1,
    )

    fig.add_hline(y=20, line_dash="dot", annotation_text="Objectif 20%", row=3, col=1, line_color="gray")

    fig.update_layout(
        height=700,
        showlegend=False,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

with tab_data:
    st.subheader("📋 Détail des journées")
    st.caption("Tableau interactif : cliquez sur une colonne pour trier.")

    clean_df = filtered_df[["Date", "Jour", "Passage", "Plat", "% Plat", "Total_jour"]].copy()

    st.dataframe(
        clean_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Jour": st.column_config.TextColumn("Jour"),
            "Passage": st.column_config.NumberColumn("🧗 Grimpeurs", format="%d", help="Nombre d'entrées sport"),
            "Plat": st.column_config.NumberColumn("🍔 Plats", format="%d", help="Nombre de plats vendus"),
            "% Plat": st.column_config.ProgressColumn(
                "Conversion Resto",
                format="%.1f%%",
                min_value=0,
                max_value=30,
            ),
            "Total_jour": st.column_config.NumberColumn("Total Personnes", format="%d"),
        },
    )

    csv = clean_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Télécharger ce tableau en Excel/CSV",
        data=csv,
        file_name="arkose_donnees_propres.csv",
        mime="text/csv",
    )

with tab_ops:
    st.subheader("🤖 Suivi des automations n8n")
    st.caption("Exports prêts à importer dans n8n. Vérifiez vos identifiants OAuth2 avant d'activer.")

    workflows = [
        ("🟢 Acquisition Heures Creuses", "n8n_arkose_acquisition.json"),
        ("🟡 Conversion Restauration", "n8n_arkose_conversion.json"),
        ("🔵 Fidélisation J+21", "n8n_arkose_fidelisation.json"),
    ]

    description_map = {
        "Schedule Trigger": "Déclenche le scénario chaque semaine (heures creuses).",
        "Date Calculation": "Prend la date actuelle et soustrait 7 jours pour cibler la semaine passée.",
        "Read Google Sheets": "Récupère les données dans Google Sheets sur la plage A:Z pour la date calculée.",
        "If Capacity < 40%": "Teste si le nombre de passages est inférieur au seuil (40% de capacité).",
        "Send Email": "Envoie un email promo aux abonnés si la capacité est basse.",

        "Schedule Daily": "Déclenche le scénario chaque jour.",
        "Get Yesterday": "Calcule la date d’hier (J-1).",
        "Fetch Data": "Lit la ligne de la date d’hier dans Google Sheets.",
        "Calculate Ratio": "Calcule le ratio plats / passages pour mesurer la conversion resto.",
        "If Ratio < 15%": "Vérifie si la conversion resto est sous 15%.",
        "Slack Alert": "Envoie une alerte Slack pour lancer une promo resto si le ratio est faible.",

        "Daily Trigger": "Déclenche le scénario fidélisation chaque jour.",
        "Get All Clients": "Récupère tous les clients depuis Google Sheets (fichier clients).",
        "Filter 21 Days": "Filtre les clients dont la dernière visite date de 21 jours.",
        "Email Relance": "Envoie un email de relance personnalisée aux clients absents depuis 3 semaines.",
    }

    for label, path in workflows:
        workflow = load_workflow(path)

        st.markdown(f"### {label}")

        if workflow is None:
            st.warning(f"Fichier manquant : {path}")
            continue

        nodes = workflow.get("nodes", [])
        trigger_name = "N/A"
        if nodes:
            trigger = next((n for n in nodes if "schedule" in n.get("type", "")), nodes[0])
            trigger_name = trigger.get("name", "N/A")

        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.write(f"Bloc de départ : **{trigger_name}** · Total blocs : **{len(nodes)}**")
        with col_b:
            st.download_button(
                "⬇️ Export n8n",
                data=json.dumps(workflow, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name=path,
                mime="application/json",
                help="Télécharger le workflow pour import dans n8n",
            )

        node_rows = [
            {
                "#": idx + 1,
                "Bloc": node.get("name", ""),
                "Type": node.get("type", ""),
                "Notes": description_map.get(node.get("name", ""), node.get("notes", "")),
            }
            for idx, node in enumerate(nodes)
        ]

        node_df = pd.DataFrame(node_rows)
        st.dataframe(node_df, hide_index=True, use_container_width=True)
        st.divider()
