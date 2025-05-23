import streamlit as st
import yfinance as yf
import os

# ---------------------- CINTA SUPERIOR CON DIVISAS, CRIPTOS Y COMMODITIES ----------------------

# Ticker: nombre -> símbolo de Yahoo Finance
activos = {
    "USD/COP": "USDCOP=X",
    "EUR/COP": "EURCOP=X",
    "GBP/COP": "GBPCOP=X",
    "JPY/COP": "JPYCOP=X",
    "CHF/COP": "CHFCOP=X",
    "CAD/COP": "CADCOP=X",
    "BTC/USD": "BTC-USD",
    "ETH/USD": "ETH-USD",
}

# Descargar precios actuales
precios = yf.download(list(activos.values()), period="1d")['Close'].iloc[-1]
texto_ticker = " | ".join([f"{nombre}: ${precios[ticker]:,.2f}" for nombre, ticker in activos.items()])

# Mostrar ticker en movimiento con HTML y CSS
st.markdown(f"""
    <style>
    .scrolling-ticker {{
        background-color: #1a1a1a;
        color: #00FFAA;
        padding: 8px 0;
        font-weight: bold;
        font-family: monospace;
        overflow: hidden;
        white-space: nowrap;
        box-shadow: inset 0 0 15px #00000055;
    }}
    .scrolling-text {{
        display: inline-block;
        padding-left: 100%;
        animation: scroll-left 40s linear infinite;
    }}
    @keyframes scroll-left {{
        0% {{ transform: translateX(0%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    </style>
    <div class='scrolling-ticker'>
        <div class='scrolling-text'>{texto_ticker}</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------- ESTILO GENERAL ----------------------
st.markdown("""
    <style>
    .title { font-size:42px; font-weight:700; color:#2c3e50; margin-top:10px; }
    .subtitle { font-size:20px; color:#555; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------- ENCABEZADO ----------------------
st.markdown("<div class='title'>💬 Text Mining, Machine Learning y Procesamiento del Lenguaje Natural</div>", unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)
with col1:
    st.write("")
with col2:
    st.image("Image/Escudo_Javeriana.jpg",  width=100)
with col3:
    st.write("")

st.markdown("<div class='subtitle'>Departamento de Economía y Finanzas · Pontificia Universidad Javeriana de Cali</div>", unsafe_allow_html=True)
# ---------------------- SECCIÓN 1: Text Mining ----------------------
st.header("📘 ¿Qué es la Minería de Texto?")
st.info("""
La **Minería de Texto** es el proceso de transformar texto sin estructura en datos útiles para el análisis. 
Se aplican técnicas como tokenización, extracción de palabras clave, análisis de sentimiento, clasificación de documentos, entre otros.
""")

# ---------------------- SECCIÓN 2: Text Mining + ML ----------------------
st.header("🧠 Text Mining con Machine Learning")
st.warning("""
Con **Machine Learning**, la minería de texto permite construir modelos que clasifican, agrupan o predicen a partir de datos textuales.
Se utilizan algoritmos como Naive Bayes, Support Vector Machines (SVM), o redes neuronales.
""")

st.code("""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)
model = MultinomialNB().fit(X, y)
""", language="python")

# ---------------------- SECCIÓN 3: PLN ----------------------
st.header("🌐 Procesamiento del Lenguaje Natural (PLN)")
st.success("""
El **PLN** busca que las computadoras comprendan, interpreten y generen lenguaje humano. 
Aplicaciones comunes incluyen asistentes virtuales, traductores automáticos, chatbots, y más.
Se apoya en bibliotecas como **spaCy**, **NLTK**, y **Transformers**.
""")

st.code("""
import spacy

nlp = spacy.load("es_core_news_sm")
doc = nlp("La minería de texto es fundamental en la economía digital.")
for token in doc:
    print(token.text, token.pos_, token.dep_)
""", language="python")

# ---------------------- PIE DE PÁGINA ----------------------
st.markdown("---")
st.caption("🎓 Desarrollado para la Pontificia Universidad Javeriana de Cali · Departamento de Economía y Finanzas")
