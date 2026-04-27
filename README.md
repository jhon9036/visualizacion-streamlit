# Visualización de Accidentes Viales - Streamlit

## Descripción

Esta aplicación web interactiva fue desarrollada con Streamlit para analizar un dataset de accidentes viales. El objetivo es identificar patrones relacionados con barrios de mayor accidentalidad, evolución temporal, personas heridas, vehículos involucrados y distribución de los accidentes.

## Dataset

- **Fuente:** Datos Abiertos Colombia
- **Tema:** Accidentes viales
- **Archivo utilizado:** `Accidentes_Viales_20260426.csv`
- **Descripción:** El dataset contiene registros de accidentes viales con variables como fecha de ocurrencia, barrio, dirección, vehículos involucrados y personas heridas.

## Hallazgos principales

1. Algunos barrios concentran una mayor cantidad de accidentes viales.
2. La evolución temporal permite observar meses con mayor o menor accidentalidad.
3. La distribución de heridos permite analizar la gravedad de los accidentes.
4. La relación entre vehículos involucrados y personas heridas ayuda a comprender el impacto de cada accidente.
5. El mapa de calor permite identificar periodos donde se concentran más registros.

## Visualizaciones implementadas

1. Gráfico de barras horizontal para comparar barrios con más accidentes.
2. Gráfico de línea para observar la evolución temporal.
3. Histograma para analizar la distribución de heridos.
4. Gráfico de dispersión para relacionar vehículos involucrados y heridos.
5. Gráfico de dona para representar proporciones.
6. Gráfico de caja para comparar distribución de heridos por barrio.
7. Mapa de calor para analizar accidentes por mes y año.

## Tecnologías utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- GitHub
- Streamlit Community Cloud

## Instalación y ejecución local

### Requisitos previos

Tener instalado Python y Git.



### Pasos de instalación


git clone https://github.com/jhon9036/visualizacion-streamlit.git
cd visualizacion-streamlit
pip install -r requirements.txt
streamlit run app.py

## Despligue

 enlace de la app desplegada https://visualizacion-app-ewpzxyn7u7vlbqlqpmwpbq.streamlit.app/.

 ## Autor

 Autor: Jhon Alexander Vargas Catuche