import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Visualización de datos",
    layout="wide"
)

st.title("Aplicación de visualización de datos en Streamlit")

st.write("""
Esta aplicación permite explorar un dataset mediante gráficos interactivos.
""")

archivo = st.file_uploader("Sube el archivo CSV", type=["csv"])

if archivo is not None:
    df = pd.read_csv(archivo)

    st.subheader("Vista previa del dataset")
    st.dataframe(df.head())

    st.subheader("Información general del dataset")
    st.write("Cantidad de filas y columnas:", df.shape)

    st.subheader("Columnas disponibles")
    st.write(df.columns.tolist())

    st.subheader("Resumen estadístico")
    st.write(df.describe())
else:
    st.info("Por favor sube un archivo CSV para comenzar.")