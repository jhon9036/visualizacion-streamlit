import unicodedata

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# CONFIGURACION
# =========================
st.set_page_config(
    page_title="Accidentes viales - Streamlit",
    page_icon="🚦",
    layout="wide",
)

st.title("🚦 Visualización de Accidentes Viales")

st.write(
    """
Aplicación interactiva desarrollada en Streamlit para analizar accidentes viales,
identificar barrios con mayor accidentalidad y observar patrones en el tiempo.
"""
)

ruta = "data/Accidentes_Viales_20260426.csv"

# Paletas de color
PALETA_CATEGORICA = px.colors.qualitative.Set3
PALETA_BARRIOS = px.colors.qualitative.Bold
PALETA_CONTINUA = "Turbo"
PALETA_CALOR = "YlOrRd"


# =========================
# FUNCIONES
# =========================
def normalizar_columna(nombre):
    nombre = str(nombre).strip().lower()
    nombre = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("utf-8")
    nombre = nombre.replace(" ", "_").replace("-", "_")
    return nombre


def buscar_columna(df, palabra):
    for col in df.columns:
        if palabra in col:
            return col
    return None


def contar_accidentes_por_barrio(df_base, top_n):
    conteo = (
        df_base["barrio"]
        .dropna()
        .value_counts()
        .head(top_n)
        .rename_axis("Barrio")
        .reset_index(name="Cantidad de accidentes")
    )

    # En barras horizontales Plotly dibuja la primera categoria abajo.
    return conteo.sort_values("Cantidad de accidentes", ascending=True)


@st.cache_data
def cargar_datos():
    df = pd.read_csv(ruta)

    df.columns = [normalizar_columna(col) for col in df.columns]

    col_fecha = buscar_columna(df, "fecha")
    col_barrio = buscar_columna(df, "barrio")
    col_vehiculos = buscar_columna(df, "vehicul")
    col_heridos = buscar_columna(df, "herid")
    col_fallecidos = buscar_columna(df, "fallecid")
    col_direccion = buscar_columna(df, "direccion")

    renombres = {}

    if col_fecha:
        renombres[col_fecha] = "fecha"
    if col_barrio:
        renombres[col_barrio] = "barrio"
    if col_vehiculos:
        renombres[col_vehiculos] = "vehiculos"
    if col_heridos:
        renombres[col_heridos] = "heridos"
    if col_fallecidos:
        renombres[col_fallecidos] = "fallecidos"
    if col_direccion:
        renombres[col_direccion] = "direccion"

    df = df.rename(columns=renombres)

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df["año"] = df["fecha"].dt.year
        df["mes"] = df["fecha"].dt.month

    for col in ["vehiculos", "heridos", "fallecidos"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "barrio" in df.columns:
        df["barrio"] = df["barrio"].astype("string").str.strip().str.upper()
        df["barrio"] = df["barrio"].replace({"": pd.NA, "NAN": pd.NA, "NONE": pd.NA})

    return df


df = cargar_datos()

# Crear variable de gravedad
if "heridos" in df.columns:
    df["gravedad"] = df["heridos"].apply(lambda x: "Con heridos" if x > 0 else "Sin heridos")


# =========================
# INFORMACION GENERAL
# =========================
st.success("✅ Dataset cargado correctamente")

with st.expander("📋 Ver información general del dataset"):
    st.write("Filas y columnas:", df.shape)
    st.write("Columnas detectadas:")
    st.write(df.columns.tolist())
    st.dataframe(df.head(10), use_container_width=True)


# =========================
# FILTROS
# =========================
st.sidebar.header("🔎 Filtros de exploración")

df_filtrado = df.copy()

if "fecha" in df.columns:
    fechas_validas = df["fecha"].dropna()

    if not fechas_validas.empty:
        fecha_min = fechas_validas.min().date()
        fecha_max = fechas_validas.max().date()

        rango_fechas = st.sidebar.date_input(
            "Selecciona rango de fechas",
            value=[fecha_min, fecha_max],
        )

        if len(rango_fechas) == 2:
            fecha_inicio = pd.to_datetime(rango_fechas[0])
            fecha_fin = pd.to_datetime(rango_fechas[1])

            df_filtrado = df_filtrado[
                (df_filtrado["fecha"] >= fecha_inicio)
                & (df_filtrado["fecha"] <= fecha_fin)
            ]

if "barrio" in df_filtrado.columns:
    barrios = sorted(df_filtrado["barrio"].dropna().unique())
    max_barrios = max(1, len(barrios))

    top_n = st.sidebar.slider(
        "Cantidad de barrios a mostrar",
        min_value=1,
        max_value=max_barrios,
        value=min(10, max_barrios),
        help="Controla cuantos barrios aparecen en las graficas tipo Top.",
    )

    barrios_seleccionados = st.sidebar.multiselect(
        "Filtrar por barrios específicos",
        barrios,
        default=[],
        placeholder="Déjalo vacío para usar todos",
        help="Si seleccionas barrios aquí, las graficas se calculan solo con esos barrios.",
    )

    if barrios_seleccionados:
        df_filtrado = df_filtrado[df_filtrado["barrio"].isin(barrios_seleccionados)]
        top_n_real = min(top_n, len(barrios_seleccionados))
    else:
        top_n_real = min(top_n, df_filtrado["barrio"].nunique())

    st.sidebar.caption(
        f"Mostrando hasta {top_n_real} barrios "
        f"de {df_filtrado['barrio'].nunique()} disponibles con los filtros actuales."
    )
else:
    top_n = 10
    top_n_real = 10

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados. Cambia los filtros e intenta nuevamente.")
    st.stop()


# =========================
# INDICADORES
# =========================
st.subheader("📌 Indicadores principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Accidentes", df_filtrado.shape[0])

with col2:
    if "barrio" in df_filtrado.columns:
        st.metric("Barrios", df_filtrado["barrio"].nunique())
    else:
        st.metric("Barrios", "N/A")

with col3:
    if "heridos" in df_filtrado.columns:
        st.metric("Heridos", int(df_filtrado["heridos"].sum()))
    else:
        st.metric("Heridos", "N/A")

with col4:
    if "vehiculos" in df_filtrado.columns:
        st.metric("Vehículos", int(df_filtrado["vehiculos"].sum()))
    else:
        st.metric("Vehículos", "N/A")


# =========================
# 1. BARRAS HORIZONTALES
# =========================
st.subheader("1. Comparación: barrios con más accidentes")

if "barrio" in df_filtrado.columns:
    accidentes_barrio = contar_accidentes_por_barrio(df_filtrado, top_n_real)

    fig1 = px.bar(
        accidentes_barrio,
        x="Cantidad de accidentes",
        y="Barrio",
        orientation="h",
        text="Cantidad de accidentes",
        color="Cantidad de accidentes",
        color_continuous_scale=PALETA_CONTINUA,
        title=f"Top {top_n_real} barrios con más accidentes",
    )

    fig1.update_traces(textposition="outside")
    fig1.update_layout(
        xaxis_title="Cantidad de accidentes",
        yaxis_title="Barrio",
        template="plotly_dark",
        margin=dict(l=20, r=40, t=70, b=40),
    )

    st.plotly_chart(fig1, use_container_width=True)


# =========================
# 2. LINEA TEMPORAL
# =========================
st.subheader("2. Evolución temporal de accidentes")

if "fecha" in df_filtrado.columns:
    accidentes_tiempo = (
        df_filtrado.dropna(subset=["fecha"])
        .groupby(pd.Grouper(key="fecha", freq="ME"))
        .size()
        .reset_index(name="Cantidad de accidentes")
    )

    fig2 = px.line(
        accidentes_tiempo,
        x="fecha",
        y="Cantidad de accidentes",
        markers=True,
        title="Evolución mensual de accidentes viales",
    )

    fig2.update_traces(
        line=dict(width=4, color="#00BFFF"),
        marker=dict(size=9, color="#FFDD57"),
    )

    fig2.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Cantidad de accidentes",
        template="plotly_dark",
    )

    st.plotly_chart(fig2, use_container_width=True)


# =========================
# 3. HISTOGRAMA
# =========================
st.subheader("3. Distribución de heridos por accidente")

if "heridos" in df_filtrado.columns:
    fig3 = px.histogram(
        df_filtrado,
        x="heridos",
        color="gravedad" if "gravedad" in df_filtrado.columns else None,
        nbins=10,
        title="Distribución del número de heridos por accidente",
        color_discrete_sequence=["#2ECC71", "#E74C3C"],
    )

    fig3.update_layout(
        xaxis_title="Número de heridos",
        yaxis_title="Frecuencia",
        template="plotly_dark",
    )

    st.plotly_chart(fig3, use_container_width=True)


# =========================
# 4. DISPERSION
# =========================
st.subheader("4. Relación entre vehículos y heridos")

if "vehiculos" in df_filtrado.columns and "heridos" in df_filtrado.columns:
    hover_cols = [
        col
        for col in ["fecha", "barrio", "direccion"]
        if col in df_filtrado.columns
    ]

    fig4 = px.scatter(
        df_filtrado,
        x="vehiculos",
        y="heridos",
        color="barrio" if "barrio" in df_filtrado.columns else None,
        size="heridos",
        hover_data=hover_cols if hover_cols else None,
        title="Relación entre vehículos involucrados y personas heridas",
        color_discrete_sequence=PALETA_BARRIOS,
    )

    fig4.update_layout(
        xaxis_title="Vehículos involucrados",
        yaxis_title="Personas heridas",
        template="plotly_dark",
    )

    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No se encontraron columnas suficientes para hacer la gráfica de dispersión.")


# =========================
# 5. DONA
# =========================
st.subheader("5. Proporción de accidentes según gravedad")

if "gravedad" in df_filtrado.columns:
    gravedad = df_filtrado["gravedad"].value_counts().reset_index()
    gravedad.columns = ["Gravedad", "Cantidad"]

    fig5 = px.pie(
        gravedad,
        names="Gravedad",
        values="Cantidad",
        hole=0.45,
        title="Proporción de accidentes con y sin heridos",
        color="Gravedad",
        color_discrete_map={
            "Sin heridos": "#2ECC71",
            "Con heridos": "#E74C3C",
        },
    )

    fig5.update_layout(template="plotly_dark")

    st.plotly_chart(fig5, use_container_width=True)


# =========================
# 6. CAJA
# =========================
st.subheader("6. Distribución de heridos en los barrios principales")

if "barrio" in df_filtrado.columns and "heridos" in df_filtrado.columns:
    barrios_top = (
        df_filtrado["barrio"]
        .dropna()
        .value_counts()
        .head(top_n_real)
        .index
    )

    df_box = df_filtrado[df_filtrado["barrio"].isin(barrios_top)]

    fig6 = px.box(
        df_box,
        x="barrio",
        y="heridos",
        color="barrio",
        title=f"Distribución de heridos en los {top_n_real} barrios principales",
        color_discrete_sequence=PALETA_CATEGORICA,
    )

    fig6.update_layout(
        xaxis_title="Barrio",
        yaxis_title="Número de heridos",
        xaxis_tickangle=-45,
        showlegend=False,
        template="plotly_dark",
    )

    st.plotly_chart(fig6, use_container_width=True)


# =========================
# 7. MAPA DE CALOR
# =========================
st.subheader("7. Mapa de calor: accidentes por mes y año")

if "año" in df_filtrado.columns and "mes" in df_filtrado.columns:
    tabla_calor = (
        df_filtrado.groupby(["año", "mes"])
        .size()
        .reset_index(name="Cantidad de accidentes")
    )

    tabla_pivot = tabla_calor.pivot(
        index="año",
        columns="mes",
        values="Cantidad de accidentes",
    ).fillna(0)

    fig7 = px.imshow(
        tabla_pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=PALETA_CALOR,
        title="Cantidad de accidentes por año y mes",
    )

    fig7.update_layout(
        xaxis_title="Mes",
        yaxis_title="Año",
        template="plotly_dark",
    )

    st.plotly_chart(fig7, use_container_width=True)


# =========================
# HALLAZGOS
# =========================
st.subheader("🔎 Hallazgos principales")

barrio_mayor = "No disponible"
cantidad_barrio_mayor = 0

if "barrio" in df_filtrado.columns and not df_filtrado["barrio"].dropna().empty:
    barrio_mayor = df_filtrado["barrio"].value_counts().idxmax()
    cantidad_barrio_mayor = df_filtrado["barrio"].value_counts().max()

total_accidentes = df_filtrado.shape[0]
total_heridos = int(df_filtrado["heridos"].sum()) if "heridos" in df_filtrado.columns else 0
total_vehiculos = int(df_filtrado["vehiculos"].sum()) if "vehiculos" in df_filtrado.columns else 0

st.write(
    f"""
1. Se analizaron **{total_accidentes} registros** de accidentes viales según los filtros seleccionados.
2. El barrio con mayor número de accidentes es **{barrio_mayor}**, con **{cantidad_barrio_mayor} registros**.
3. En los datos filtrados se registran **{total_heridos} personas heridas**.
4. Se reportan **{total_vehiculos} vehículos involucrados** en los accidentes analizados.
5. La gráfica temporal permite observar meses donde la accidentalidad aumenta o disminuye.
6. El mapa de calor ayuda a identificar periodos con mayor concentración de accidentes.
"""
)


# =========================
# DESCARGA
# =========================
st.subheader("⬇️ Descargar datos filtrados")

csv = df_filtrado.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar datos filtrados en CSV",
    data=csv,
    file_name="accidentes_viales_filtrados.csv",
    mime="text/csv",
)