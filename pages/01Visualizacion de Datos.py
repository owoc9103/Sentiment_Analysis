import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# ------------------------ CONFIGURACIÓN DE PÁGINA ------------------------
st.set_page_config(page_title="Javeriana Cali - App Financiera", layout="centered")

# ------------------------ ENCABEZADO INSTITUCIONAL ------------------------
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Logo_PUJ.svg/2560px-Logo_PUJ.svg.png", width=250)
st.title("Universidad Javeriana de Cali")
st.subheader("Facultad de Ciencias Económicas y Administrativas")

# ------------------------ EMPRESAS TECNOLÓGICAS DISPONIBLES ------------------------
opciones_empresas = {
    "Tesla (TSLA)": "TSLA",
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Google / Alphabet (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "NVIDIA (NVDA)": "NVDA",
    "Meta / Facebook (META)": "META"
}

# ------------------------ SIDEBAR: PARÁMETROS ------------------------
st.sidebar.header("Parámetros de descarga")
empresa_nombre = st.sidebar.selectbox("Selecciona una empresa", list(opciones_empresas.keys()))
ticker = opciones_empresas[empresa_nombre]

fecha_inicio = st.sidebar.date_input("Fecha de inicio", pd.to_datetime("2020-01-01"))
fecha_fin = st.sidebar.date_input("Fecha de fin", pd.to_datetime("today"))

# ------------------------ FUNCIÓN PARA DESCARGAR DATOS ------------------------
def obtener_datos_empresa(ticker: str, fecha_inicio: str, fecha_fin: str):
    data = yf.download(ticker, start=fecha_inicio, end=fecha_fin)
    return data

# ------------------------ VALIDACIÓN Y DESCARGA ------------------------
st.markdown(f"### Visualización de Precios Históricos de **{empresa_nombre}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2:
    st.image("Image/Escudo_Javeriana.jpg",  width=100)
with col3:
    st.write("")


st.markdown("""
Este aplicativo fue desarrollado con fines académicos como parte de un ejercicio práctico en análisis financiero usando Streamlit.  
Permite consultar, visualizar y descargar los precios históricos de acciones de empresas tecnológicas, usando datos de `Yahoo Finance`.

---
""")

if fecha_inicio >= fecha_fin:
    st.error("La fecha de inicio debe ser anterior a la fecha de fin.")
else:
    st.write(f"### Precios desde **{fecha_inicio}** hasta **{fecha_fin}**")
    datos = obtener_datos_empresa(ticker, str(fecha_inicio), str(fecha_fin))

    if datos.empty:
        st.warning("No se encontraron datos para el período seleccionado.")
    else:
        st.subheader("📉 Precio de cierre")
        st.line_chart(datos["Close"])

        datos["Daily Return"] = datos["Close"].pct_change()
        volatilidad = datos["Daily Return"].std()
        
        #media=datos['Close'].mean()
        
        
        st.markdown("### 📈 Métricas Clave del Precio de la Acción")

        #st.metric(label="📊 Precio de Cierre Promedio", value=round(media,2), delta=100)
        #st.markdown("📊 Precio de Cierre Promedio", f"${datos['Close'].mean():.2f}")
        #col1, col2, col3 = st.columns(3)
        #with  col1:
        #    st.metric("Precio de Cierre Promedio", media=datos['Close'].mean())
        #with col2:
        #    st.markdown("🔼 Precio Máximo", datos['High'].max())
        #with col3:
        #    st.markdown("🔽 Precio Mínimo", datos['Low'].min())

        #col4, col5, col6 = st.columns(2)
        #col4.metric("📥 Precio de Apertura Promedio", f"${datos['Open'].mean():.2f}")
        #col5.metric("📈 Volatilidad Diaria", f"{volatilidad*100:.2f}%")
        

        st.markdown("---")
        

        st.subheader("📊 Tabla de datos")
        st.dataframe(datos)


        

        

        csv = datos.to_csv().encode("utf-8")
        st.download_button(
            label="📥 Descargar como CSV",
            data=csv,
            file_name=f"{ticker}_{fecha_inicio}_a_{fecha_fin}.csv",
            mime="text/csv"
        )
