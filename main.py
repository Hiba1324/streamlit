import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Dashboard interactif automatique",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 100

    df = pd.DataFrame({
        "Age": np.random.randint(18, 60, n),
        "Revenu": np.random.randint(2500, 15000, n),
        "Score": np.round(np.random.uniform(0, 100, n), 2),
        "Montant_Achat": np.round(np.random.uniform(50, 3000, n), 2),
        "Quantite": np.random.randint(1, 20, n),
        "Satisfaction": np.random.randint(1, 6, n),
        "Temps_Site": np.round(np.random.uniform(1, 120, n), 2),

        "Ville": np.random.choice(["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger"], n),
        "Genre": np.random.choice(["Homme", "Femme"], n),
        "Produit": np.random.choice(["PC", "Téléphone", "Casque", "Imprimante", "Tablette"], n),
        "Segment_Client": np.random.choice(["Premium", "Standard", "Nouveau"], n),
        "Statut": np.random.choice(["Payé", "En attente", "Annulé"], n),
        "Region": np.random.choice(["Nord", "Sud", "Est", "Ouest", "Centre"], n),
        "Canal": np.random.choice(["Web", "Magasin", "Mobile"], n),
        "Paiement": np.random.choice(["Carte", "Cash", "Virement"], n),

        "Date_Commande": pd.date_range(start="2026-01-01", periods=n, freq="D"),
        "Date_Inscription": pd.date_range(start="2025-09-01", periods=n, freq="2D"),
        "Date_Livraison": pd.date_range(start="2026-01-03", periods=n, freq="D"),
        "Date_Relance": pd.date_range(start="2026-02-01", periods=n, freq="3D"),

        "Fidelite": np.random.choice(["Oui", "Non"], n)
    })

    return df


def try_convert_dates(df):
    df_copy = df.copy()

    for col in df_copy.columns:
        if df_copy[col].dtype == "object":
            converted = pd.to_datetime(df_copy[col], errors="coerce")
            if converted.notna().sum() >= 0.7 * len(df_copy):
                df_copy[col] = converted

    return df_copy


def detect_variable_types(df):
    quantitative = df.select_dtypes(include=np.number).columns.tolist()
    temporelle = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()

    qualitative = []
    for col in df.columns:
        if col not in quantitative and col not in temporelle:
            qualitative.append(col)

    return quantitative, qualitative, temporelle


def variable_type(col, quantitative, qualitative, temporelle):
    if col in quantitative:
        return "Quantitative"
    if col in qualitative:
        return "Qualitative"
    if col in temporelle:
        return "Date"
    return "Inconnue"


def choose_auto_chart(x, y, quantitative, qualitative, temporelle):
    x_type = variable_type(x, quantitative, qualitative, temporelle)
    y_type = variable_type(y, quantitative, qualitative, temporelle) if y != "Aucune" else None

    if x_type == "Date" or y_type == "Date":
        return "Line chart"

    if x_type == "Qualitative" and y == "Aucune":
        return "Bar chart"

    if x_type == "Quantitative" and y == "Aucune":
        return "Histogramme"

    if x_type == "Quantitative" and y_type == "Quantitative":
        return "Scatter plot"

    if (x_type == "Qualitative" and y_type == "Quantitative") or (
        x_type == "Quantitative" and y_type == "Qualitative"
    ):
        return "Boxplot"

    return "Bar chart"


def create_chart(df, x, y, chart_type):
    title = f"{chart_type} - {x}" if y == "Aucune" else f"{chart_type} - {x} / {y}"

    if chart_type == "Bar chart":
        counts = df[x].value_counts().reset_index()
        counts.columns = [x, "Nombre"]
        fig = px.bar(counts, x=x, y="Nombre", title=title, text="Nombre")

    elif chart_type == "Histogramme":
        fig = px.histogram(df, x=x, title=title, nbins=20)

    elif chart_type == "Scatter plot":
        fig = px.scatter(df, x=x, y=y, title=title, hover_data=df.columns)

    elif chart_type == "Boxplot":
        fig = px.box(df, x=x, y=y, title=title)

    elif chart_type == "Line chart":
        temp_df = df.copy()

        if y == "Aucune":
            temp_df = temp_df.groupby(x).size().reset_index(name="Nombre")
            fig = px.line(temp_df, x=x, y="Nombre", title=title, markers=True)
        else:
            if pd.api.types.is_datetime64_any_dtype(temp_df[x]):
                temp_df = temp_df.sort_values(by=x)
                fig = px.line(temp_df, x=x, y=y, title=title, markers=True)
            elif pd.api.types.is_datetime64_any_dtype(temp_df[y]):
                temp_df = temp_df.sort_values(by=y)
                fig = px.line(temp_df, x=y, y=x, title=title, markers=True)
            else:
                fig = px.line(temp_df, x=x, y=y, title=title, markers=True)

    else:
        fig = px.scatter(df, x=x, y=y, title=title)

    fig.update_layout(height=550)
    return fig


st.title("📊 Dashboard interactif avec détection automatique")
st.write("Application Streamlit : détection des variables, filtre simple et visualisation interactive.")

st.sidebar.header("📁 Source des données")
uploaded_file = st.sidebar.file_uploader("Importer un fichier CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Fichier CSV importé avec succès.")
else:
    df = generate_data()
    st.sidebar.info("Données exemple utilisées : 100 lignes × 20 colonnes.")

df = try_convert_dates(df)
quantitative, qualitative, temporelle = detect_variable_types(df)

st.subheader("✅ Détection automatique des types de variables")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Variables quantitatives", len(quantitative))
    st.write(quantitative)

with col2:
    st.metric("Variables qualitatives", len(qualitative))
    st.write(qualitative)

with col3:
    st.metric("Variables dates", len(temporelle))
    st.write(temporelle)

st.sidebar.header("🔎 Filtre simple")

filtered_df = df.copy()

if qualitative:
    filter_col = st.sidebar.selectbox("Choisir une colonne qualitative pour filtrer", qualitative)
    values = sorted(filtered_df[filter_col].dropna().unique().tolist())
    selected_values = st.sidebar.multiselect(
        f"Filtrer par {filter_col}",
        values,
        default=values
    )

    if selected_values:
        filtered_df = filtered_df[filtered_df[filter_col].isin(selected_values)]

st.sidebar.write(f"Nombre de lignes affichées : {len(filtered_df)}")

st.subheader("🎛️ Visualisation interactive")

all_columns = df.columns.tolist()

c1, c2, c3 = st.columns(3)

with c1:
    x_var = st.selectbox("Choisir la variable X", all_columns)

with c2:
    y_var = st.selectbox("Choisir la variable Y", ["Aucune"] + all_columns)

with c3:
    chart_choice = st.selectbox(
        "Choisir le type de graphique",
        ["Auto", "Bar chart", "Histogramme", "Scatter plot", "Boxplot", "Line chart"]
    )

if chart_choice == "Auto":
    final_chart = choose_auto_chart(x_var, y_var, quantitative, qualitative, temporelle)
else:
    final_chart = chart_choice

st.info(
    f"Type X : {variable_type(x_var, quantitative, qualitative, temporelle)} | "
    f"Type Y : {variable_type(y_var, quantitative, qualitative, temporelle) if y_var != 'Aucune' else 'Aucune'} | "
    f"Graphique choisi : {final_chart}"
)

try:
    fig = create_chart(filtered_df, x_var, y_var, final_chart)
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error("Impossible d'afficher ce graphique avec ces variables.")
    st.write("Détail de l'erreur :", e)

st.subheader("📋 Aperçu des données")
st.dataframe(filtered_df, use_container_width=True)

st.caption("Projet Streamlit : dashboard simple avec titre dynamique, filtre simple et graphique interactif.")
