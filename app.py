"""
Aplicación de análisis de accidentes viales — Versión profesional mejorada
"""
from __future__ import annotations

import unicodedata

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Accidentes Viales · Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────
DATA_PATH = "data/Accidentes_Viales_20260426.csv"

COLORES = {
    "primario": "#E63946",
    "secundario": "#457B9D",
    "fondo_oscuro": "#0F1923",
    "fondo_medio": "#1A2535",
    "fondo_carta": "#1E2D3D",
    "texto_claro": "#E8F4F8",
    "texto_gris": "#8AAFC0",
    "acento_verde": "#2DCE89",
    "acento_amarillo": "#FFB347",
}

PALETA_BARRIOS = [
    "#E63946", "#457B9D", "#2DCE89", "#FFB347", "#A78BFA",
    "#34D399", "#F472B6", "#60A5FA", "#FBBF24", "#A3E635",
]

MAPA_MESES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
    "1": "Ene", "2": "Feb", "3": "Mar", "4": "Abr", "5": "May", "6": "Jun",
    "7": "Jul", "8": "Ago", "9": "Sep", "10": "Oct", "11": "Nov", "12": "Dic",
    "ene": "Ene", "enero": "Ene",
    "feb": "Feb", "febrero": "Feb",
    "mar": "Mar", "marzo": "Mar",
    "abr": "Abr", "abril": "Abr",
    "may": "May", "mayo": "May",
    "jun": "Jun", "junio": "Jun",
    "jul": "Jul", "julio": "Jul",
    "ago": "Ago", "agosto": "Ago",
    "sep": "Sep", "sept": "Sep", "septiembre": "Sep",
    "oct": "Oct", "octubre": "Oct",
    "nov": "Nov", "noviembre": "Nov",
    "dic": "Dic", "diciembre": "Dic",
}

ORDEN_MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

MESES_COMPLETOS = {
    "Ene": "Enero", "Feb": "Febrero", "Mar": "Marzo", "Abr": "Abril",
    "May": "Mayo", "Jun": "Junio", "Jul": "Julio", "Ago": "Agosto",
    "Sep": "Septiembre", "Oct": "Octubre", "Nov": "Noviembre", "Dic": "Diciembre"
}

ESCALA_CALOR = [
    [0.00, "#EAF2F8"],
    [0.20, "#D4E6F1"],
    [0.40, "#F9E79F"],
    [0.60, "#F5B041"],
    [0.80, "#EC7063"],
    [1.00, "#C0392B"],
]

LAYOUT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'IBM Plex Sans', sans-serif", color=COLORES["texto_claro"]),
    margin=dict(l=20, r=20, t=60, b=40),
)

# ──────────────────────────────────────────────
# CSS PERSONALIZADO
# ──────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    .stApp {{
        background-color: {COLORES['fondo_oscuro']};
        font-family: 'IBM Plex Sans', sans-serif;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}

    [data-testid="stSidebar"] {{
        background-color: {COLORES['fondo_medio']};
        border-right: 1px solid #2A3F54;
    }}
    [data-testid="stSidebar"] * {{
        color: {COLORES['texto_claro']} !important;
    }}

    .hero-header {{
        background: linear-gradient(135deg, {COLORES['fondo_medio']} 0%, #0D2137 100%);
        border-left: 4px solid {COLORES['primario']};
        border-radius: 0 12px 12px 0;
        padding: 24px 32px;
        margin-bottom: 32px;
    }}
    .hero-header h1 {{
        color: {COLORES['texto_claro']};
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }}
    .hero-header p {{
        color: {COLORES['texto_gris']};
        font-size: 0.95rem;
        margin: 0;
    }}

    .kpi-card {{
        background: {COLORES['fondo_carta']};
        border: 1px solid #2A3F54;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        transition: border-color .2s, transform .2s;
    }}
    .kpi-card:hover {{
        border-color: {COLORES['secundario']};
        transform: translateY(-2px);
    }}
    .kpi-card .kpi-label {{
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: .12em;
        text-transform: uppercase;
        color: {COLORES['texto_gris']};
        margin-bottom: 8px;
    }}
    .kpi-card .kpi-value {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2rem;
        font-weight: 600;
        color: {COLORES['texto_claro']};
    }}
    .kpi-card .kpi-icon {{
        font-size: 1.4rem;
        margin-bottom: 6px;
    }}

    .section-title {{
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
        color: {COLORES['primario']};
        margin: 40px 0 16px 0;
    }}

    hr.custom-hr {{
        border: none;
        border-top: 1px solid #2A3F54;
        margin: 32px 0;
    }}

    [data-testid="stExpander"] {{
        background: {COLORES['fondo_carta']};
        border: 1px solid #2A3F54 !important;
        border-radius: 10px;
    }}

    .stDownloadButton > button {{
        background: {COLORES['primario']};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 24px;
        width: 100%;
    }}
    .stDownloadButton > button:hover {{
        background: #C1121F;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid #2A3F54;
        border-radius: 8px;
        overflow: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────────
def normalizar_columna(nombre: str) -> str:
    nombre = str(nombre).strip().lower()
    nombre = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return nombre.replace(" ", "_").replace("-", "_")


def buscar_columna(df: pd.DataFrame, palabra: str) -> str | None:
    return next((col for col in df.columns if palabra in col), None)


def aplicar_layout(fig: go.Figure, **kwargs) -> go.Figure:
    config = {**LAYOUT_BASE, **kwargs}
    fig.update_layout(**config)
    return fig


# ──────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df.columns = [normalizar_columna(c) for c in df.columns]

    mapeo = {
        buscar_columna(df, k): v
        for k, v in {
            "fecha": "fecha",
            "barrio": "barrio",
            "vehicul": "vehiculos",
            "herid": "heridos",
            "fallecid": "fallecidos",
            "direccion": "direccion",
        }.items()
        if buscar_columna(df, k)
    }
    df = df.rename(columns=mapeo)

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df["año"] = df["fecha"].dt.year
        df["mes"] = df["fecha"].dt.month

    for col in ["vehiculos", "heridos", "fallecidos"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "barrio" in df.columns:
        df["barrio"] = (
            df["barrio"]
            .astype("string")
            .str.strip()
            .str.upper()
            .replace({"": pd.NA, "NAN": pd.NA, "NONE": pd.NA})
        )

    return df


# ──────────────────────────────────────────────
# CARGA
# ──────────────────────────────────────────────
with st.spinner("Cargando datos…"):
    df = cargar_datos()

if "heridos" in df.columns:
    df["gravedad"] = df["heridos"].apply(
        lambda x: "Con heridos" if x > 0 else "Sin heridos"
    )

# ──────────────────────────────────────────────
# ENCABEZADO
# ──────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-header">
        <h1>🚦 Dashboard — Accidentes Viales</h1>
        <p>Análisis interactivo de siniestralidad vial · Filtra, explora y descarga los datos</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# SIDEBAR — FILTROS
# ──────────────────────────────────────────────
top_n = 10
top_n_real = 10

with st.sidebar:
    st.markdown("## 🔎 Filtros")
    st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

    df_filtrado = df.copy()

    if "fecha" in df.columns:
        fechas_validas = df["fecha"].dropna()
        if not fechas_validas.empty:
            fecha_min = fechas_validas.min().date()
            fecha_max = fechas_validas.max().date()

            rango = st.date_input(
                "Rango de fechas",
                value=[fecha_min, fecha_max],
                min_value=fecha_min,
                max_value=fecha_max,
            )

            if len(rango) == 2:
                df_filtrado = df_filtrado[
                    df_filtrado["fecha"].between(
                        pd.Timestamp(rango[0]),
                        pd.Timestamp(rango[1])
                    )
                ]

    if "barrio" in df_filtrado.columns:
        barrios_disponibles = sorted(df_filtrado["barrio"].dropna().unique().tolist())
        max_barrios = max(1, len(barrios_disponibles))

        top_n = st.slider(
            "Barrios en gráficas Top",
            min_value=1,
            max_value=min(max_barrios, 30),
            value=min(10, max_barrios),
            help="Número de barrios que se muestran en las gráficas comparativas.",
        )

        barrios_sel = st.multiselect(
            "Barrios específicos",
            options=barrios_disponibles,
            default=[],
            placeholder="Todos los barrios",
        )

        if barrios_sel:
            df_filtrado = df_filtrado[df_filtrado["barrio"].isin(barrios_sel)]
            top_n_real = min(top_n, len(barrios_sel))
        else:
            top_n_real = min(top_n, df_filtrado["barrio"].nunique())

        st.caption(
            f"📍 Mostrando **{top_n_real}** de **{df_filtrado['barrio'].nunique()}** barrios disponibles"
        )

    st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

    with st.expander("📋 Información del dataset"):
        st.write(f"**Filas:** {df.shape[0]:,}  |  **Columnas:** {df.shape[1]}")
        st.write("**Columnas detectadas:**")
        st.code(", ".join(df.columns.tolist()), language=None)
        st.dataframe(df.head(5), use_container_width=True)

# ──────────────────────────────────────────────
# VALIDACIÓN
# ──────────────────────────────────────────────
if df_filtrado.empty:
    st.warning("⚠️ Sin datos con los filtros seleccionados. Ajusta los parámetros del sidebar.")
    st.stop()

# ──────────────────────────────────────────────
# PREPARACIÓN DINÁMICA PARA GRÁFICAS POR BARRIO
# ──────────────────────────────────────────────
ranking_barrios = pd.DataFrame(columns=["Barrio", "Accidentes"])
barrios_top = []
df_top_barrios = df_filtrado.copy()

if "barrio" in df_filtrado.columns:
    ranking_barrios = (
        df_filtrado["barrio"]
        .dropna()
        .value_counts()
        .reset_index()
    )
    ranking_barrios.columns = ["Barrio", "Accidentes"]

    top_n_real = min(top_n_real, len(ranking_barrios))
    barrios_top = ranking_barrios.head(top_n_real)["Barrio"].tolist()
    df_top_barrios = df_filtrado[df_filtrado["barrio"].isin(barrios_top)].copy()

paleta_base = PALETA_BARRIOS
paleta_top = (paleta_base * ((max(1, len(barrios_top)) // len(paleta_base)) + 1))[:max(1, len(barrios_top))]

altura_grafica_barrios = max(380, 55 * max(1, top_n_real))

# ──────────────────────────────────────────────
# KPI CARDS
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">Indicadores clave</p>', unsafe_allow_html=True)

total_acc = df_filtrado.shape[0]
total_barrios = df_filtrado["barrio"].nunique() if "barrio" in df_filtrado.columns else "—"
total_heridos = int(df_filtrado["heridos"].sum()) if "heridos" in df_filtrado.columns else "—"
total_vehiculos = int(df_filtrado["vehiculos"].sum()) if "vehiculos" in df_filtrado.columns else "—"

kpis = [
    ("🚨", "Accidentes", f"{total_acc:,}"),
    ("📍", "Barrios", f"{total_barrios:,}" if isinstance(total_barrios, int) else total_barrios),
    ("🤕", "Heridos", f"{total_heridos:,}" if isinstance(total_heridos, int) else total_heridos),
    ("🚗", "Vehículos", f"{total_vehiculos:,}" if isinstance(total_vehiculos, int) else total_vehiculos),
]

cols = st.columns(4)
for col, (icono, label, valor) in zip(cols, kpis):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icono}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# GRÁFICAS — Fila 1
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">Distribución espacial y temporal</p>', unsafe_allow_html=True)

col_izq, col_der = st.columns([1, 1], gap="large")

# 1. Barras horizontales
with col_izq:
    st.markdown("##### 🏘️ Top barrios con más accidentes")

    if not ranking_barrios.empty:
        top_df = ranking_barrios.head(top_n_real).sort_values("Accidentes", ascending=True)

        fig1 = px.bar(
            top_df,
            x="Accidentes",
            y="Barrio",
            orientation="h",
            text="Accidentes",
        )

        fig1.update_traces(
            textposition="outside",
            textfont_size=12,
            marker=dict(
                color=COLORES["primario"],
                line=dict(color="rgba(255,255,255,0.20)", width=1)
            ),
            hovertemplate="<b>%{y}</b><br>Accidentes: %{x}<extra></extra>",
        )

        aplicar_layout(
            fig1,
            title=f"Top {top_n_real} barrios con mayor siniestralidad",
            xaxis_title="Cantidad de accidentes",
            yaxis_title="",
            height=altura_grafica_barrios,
        )

        fig1.update_yaxes(automargin=True, categoryorder="total ascending")
        fig1.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")

        st.plotly_chart(fig1, use_container_width=True)
        st.caption("Esta gráfica compara solo los barrios seleccionados en el ranking actual.")

# 2. Línea temporal
# 2. Línea temporal
with col_der:
    st.markdown("##### 📈 Evolución mensual")

    if "fecha" in df_filtrado.columns:
        df_tiempo = (
            df_filtrado.dropna(subset=["fecha"])
            .groupby(pd.Grouper(key="fecha", freq="ME"))
            .size()
            .reset_index(name="Accidentes")
        )

        fig2 = px.area(
            df_tiempo,
            x="fecha",
            y="Accidentes",
            color_discrete_sequence=[COLORES["primario"]],
        )

        fig2.update_traces(
            line=dict(width=2.5, color=COLORES["primario"]),
            fillcolor="rgba(230,57,70,0.15)",
            marker=dict(size=5, color=COLORES["acento_amarillo"]),
            hovertemplate="<b>Fecha:</b> %{x|%b %Y}<br><b>Accidentes:</b> %{y}<extra></extra>",
        )

        aplicar_layout(
            fig2,
            title="Evolución de accidentes por mes",
            xaxis_title="",
            yaxis_title="Cantidad de accidentes",
            height=420,
        )

        fig2.update_xaxes(showgrid=False)
        fig2.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")

        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Permite identificar meses donde la accidentalidad aumenta o disminuye.")

col_a, col_b = st.columns([1.2, 0.8], gap="large")

# 3. Histograma heridos
with col_a:
    st.markdown("##### 🩺 Distribución de heridos por accidente")

    if "heridos" in df_filtrado.columns:
        fig3 = px.histogram(
            df_filtrado,
            x="heridos",
            color="gravedad" if "gravedad" in df_filtrado.columns else None,
            nbins=12,
            color_discrete_map={
                "Sin heridos": COLORES["acento_verde"],
                "Con heridos": COLORES["primario"],
            },
            barmode="overlay",
            opacity=0.85,
        )

        fig3.update_traces(marker_line_width=0)

        aplicar_layout(
            fig3,
            title="Frecuencia de heridos por accidente",
            xaxis_title="Número de heridos",
            yaxis_title="Frecuencia",
            bargap=0.05,
            height=420,
        )

        fig3.update_xaxes(showgrid=False)
        fig3.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")

        st.plotly_chart(fig3, use_container_width=True)
        st.caption("Ayuda a ver si la mayoría de accidentes dejan pocos o muchos heridos.")

# 4. Dona de gravedad
with col_b:
    st.markdown("##### 🍩 Gravedad de accidentes")

    if "gravedad" in df_filtrado.columns:
        grav_df = df_filtrado["gravedad"].value_counts().reset_index()
        grav_df.columns = ["Gravedad", "Cantidad"]

        fig4 = px.pie(
            grav_df,
            names="Gravedad",
            values="Cantidad",
            hole=0.55,
            color="Gravedad",
            color_discrete_map={
                "Sin heridos": COLORES["acento_verde"],
                "Con heridos": COLORES["primario"],
            },
        )

        fig4.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color=COLORES["fondo_oscuro"], width=2)),
            hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>",
        )

        aplicar_layout(
            fig4,
            title="Accidentes con y sin heridos",
            showlegend=False,
            height=420,
        )

        st.plotly_chart(fig4, use_container_width=True)
        st.caption("Resume de forma rápida la proporción de accidentes con afectación humana.")

st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# GRÁFICAS — Fila 3
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">Análisis por barrio</p>', unsafe_allow_html=True)

col_c, col_d = st.columns(2, gap="large")

# 5. Dispersión vehículos vs heridos
with col_c:
    st.markdown("##### 🔵 Vehículos vs heridos")

    if {"vehiculos", "heridos"}.issubset(df_top_barrios.columns) and not df_top_barrios.empty:
        hover_cols = [c for c in ["fecha", "barrio", "direccion"] if c in df_top_barrios.columns]

        df_scatter = df_top_barrios.copy()
        df_scatter["tam_punto"] = df_scatter["heridos"].fillna(0) + 1

        mostrar_leyenda = top_n_real <= 8

        fig5 = px.scatter(
            df_scatter,
            x="vehiculos",
            y="heridos",
            color="barrio" if "barrio" in df_scatter.columns else None,
            size="tam_punto",
            size_max=18,
            hover_data=hover_cols or None,
            color_discrete_sequence=paleta_top,
            category_orders={"barrio": barrios_top},
            opacity=0.80,
        )

        fig5.update_traces(
            marker=dict(line=dict(width=0.6, color="white"))
        )

        aplicar_layout(
            fig5,
            title=f"Relación entre vehículos involucrados y heridos · Top {top_n_real} barrios",
            xaxis_title="Vehículos involucrados",
            yaxis_title="Personas heridas",
            showlegend=mostrar_leyenda,
            height=max(420, 50 * max(1, top_n_real)),
        )

        fig5.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        fig5.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")

        st.plotly_chart(fig5, use_container_width=True)
        st.caption("Cada punto representa un accidente. Más arriba significa mayor número de heridos.")
    else:
        st.info("Sin columnas suficientes para el gráfico de dispersión.")

# 6. Boxplot por barrio
with col_d:
    st.markdown("##### 📦 Heridos por barrio (boxplot)")

    if "barrio" in df_top_barrios.columns and "heridos" in df_top_barrios.columns and not df_top_barrios.empty:
        fig6 = px.box(
            df_top_barrios,
            x="barrio",
            y="heridos",
            color="barrio",
            color_discrete_sequence=paleta_top,
            category_orders={"barrio": barrios_top},
            points="outliers",
        )

        fig6.update_traces(marker_size=4)

        aplicar_layout(
            fig6,
            title=f"Distribución de heridos en los {top_n_real} barrios principales",
            xaxis_title="",
            yaxis_title="Número de heridos",
            xaxis_tickangle=-35,
            showlegend=False,
            height=max(420, 50 * max(1, top_n_real)),
        )

        fig6.update_xaxes(automargin=True)
        fig6.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")

        st.plotly_chart(fig6, use_container_width=True)
        st.caption("Sirve para comparar si en algunos barrios los accidentes suelen ser más graves.")
    else:
        st.info("No hay datos suficientes para el boxplot.")

st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# MAPA DE CALOR
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">Mapa de calor temporal</p>', unsafe_allow_html=True)
st.markdown("##### 🗓️ Accidentes por año y mes")
st.caption("Cómo leer esta gráfica: los colores más intensos representan los periodos con mayor concentración de accidentes.")

if {"año", "mes"}.issubset(df_filtrado.columns):
    df_calor = df_filtrado.copy()

    df_calor["mes"] = (
        df_calor["mes"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(MAPA_MESES)
        .fillna(df_calor["mes"])
    )

    tabla_pivot = (
        df_calor.groupby(["año", "mes"])
        .size()
        .reset_index(name="Accidentes")
        .pivot(index="año", columns="mes", values="Accidentes")
        .reindex(columns=ORDEN_MESES, fill_value=0)
        .sort_index()
        .fillna(0)
    )

    texto_celdas = tabla_pivot.astype(int).astype(str)
    texto_celdas = texto_celdas.mask(tabla_pivot.eq(0), "")

    serie_picos = tabla_pivot.stack()
    anio_pico, mes_pico = serie_picos.idxmax()
    valor_pico = int(serie_picos.max())

    fig7 = go.Figure(
        go.Heatmap(
            z=tabla_pivot.values,
            x=tabla_pivot.columns,
            y=tabla_pivot.index.astype(str),
            colorscale=ESCALA_CALOR,
            zmin=0,
            zmax=max(1, int(tabla_pivot.to_numpy().max())),
            text=texto_celdas.values,
            texttemplate="%{text}",
            textfont=dict(size=12, color="white"),
            xgap=5,
            ygap=5,
            colorbar=dict(
                title="Accidentes",
                thickness=16,
                len=0.85,
            ),
            hovertemplate=(
                "<b>Año:</b> %{y}<br>"
                "<b>Mes:</b> %{x}<br>"
                "<b>Accidentes:</b> %{z}<extra></extra>"
            ),
        )
    )

    aplicar_layout(
        fig7,
        title=(
            "Concentración mensual de accidentes"
            "<br><sup>Colores más intensos = mayor número de accidentes</sup>"
        ),
        xaxis=dict(
            title="Mes",
            showgrid=False,
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            title="Año",
            showgrid=False,
            tickfont=dict(size=12),
        ),
        height=max(400, 120 + 70 * tabla_pivot.shape[0]),
    )

    fig7.add_annotation(
        x=1,
        y=1.12,
        xref="paper",
        yref="paper",
        text=f"Pico del período: {MESES_COMPLETOS.get(mes_pico, mes_pico)} de {anio_pico} ({valor_pico} accidentes)",
        showarrow=False,
        font=dict(size=12, color=COLORES["texto_claro"]),
        align="right",
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.info(
        f"Interpretación rápida: el período más crítico fue **{MESES_COMPLETOS.get(mes_pico, mes_pico)} de {anio_pico}**, "
        f"con **{valor_pico} accidentes**. Esta visual permite identificar en qué momentos del año se concentra más la accidentalidad."
    )
else:
    st.warning("No se encontraron las columnas 'año' y 'mes'.")

st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# HALLAZGOS
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">Síntesis de resultados</p>', unsafe_allow_html=True)

barrio_top = "—"
cant_top = 0

if "barrio" in df_filtrado.columns and not df_filtrado["barrio"].dropna().empty:
    vc = df_filtrado["barrio"].value_counts()
    barrio_top, cant_top = vc.idxmax(), int(vc.max())

tasa_heridos = (
    round(
        df_filtrado[df_filtrado["heridos"] > 0].shape[0] / total_acc * 100, 1
    )
    if "heridos" in df_filtrado.columns and total_acc > 0
    else 0
)

st.markdown(
    f"""
    <div style="
        background:{COLORES['fondo_carta']};
        border:1px solid #2A3F54;
        border-radius:12px;
        padding:24px 32px;
        line-height:2;
        color:{COLORES['texto_claro']};
        font-size:0.95rem;
    ">
        📊 Se analizaron <strong>{total_acc:,} registros</strong> de accidentes viales.<br>
        📍 El barrio más afectado es <strong>{barrio_top}</strong> con <strong>{cant_top:,} accidentes</strong>.<br>
        🤕 Se reportan <strong>{total_heridos:,} personas heridas</strong> ({tasa_heridos}% de los accidentes).<br>
        🚗 Se registran <strong>{total_vehiculos:,} vehículos involucrados</strong> en total.<br>
        📈 La evolución mensual permite identificar picos y caídas de siniestralidad.<br>
        🗓️ El mapa de calor evidencia con claridad los periodos de mayor concentración de accidentes.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<hr class='custom-hr'>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DESCARGA
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">Exportar datos</p>', unsafe_allow_html=True)

csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")

col_dl, col_info = st.columns([1, 2])

with col_dl:
    st.download_button(
        label="⬇️ Descargar CSV filtrado",
        data=csv_bytes,
        file_name="accidentes_viales_filtrados.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_info:
    st.caption(
        f"El archivo incluye **{df_filtrado.shape[0]:,} filas** y "
        f"**{df_filtrado.shape[1]} columnas** con los filtros actuales."
    )