import streamlit as st
import feedparser
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from urllib.parse import quote
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
import plotly.express as px
import io

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Sentimiento de Noticias con IA",
    page_icon="📰",
    layout="wide"
)



# Inicializar variables de estado de sesión si no existen
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'last_topic' not in st.session_state:
    st.session_state.last_topic = ""
if 'sentiment_df' not in st.session_state:
    st.session_state.sentiment_df = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0

# Cache para mejorar rendimiento
@st.cache_data(ttl=3600)  # Cache por 1 hora
def fetch_news(topic, max_articles=100):
    """Obtener artículos de noticias basados en el tema proporcionado."""
    encoded_topic = quote(topic)
    url = f"https://news.google.com/rss/search?q={encoded_topic}"
    
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return []
            
        articles = []
        for entry in feed.entries[:max_articles]:
            title = entry.title if 'title' in entry else ''
            summary = remove_html_tags(entry.summary) if 'summary' in entry else ''
            link = entry.link if 'link' in entry else ''
            published = entry.published if 'published' in entry else ''
            
            if title:
                articles.append({
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'published': published
                })
        return articles
    except Exception as e:
        st.error(f"Error al obtener noticias: {e}")
        return []

def remove_html_tags(text):
    """Eliminar etiquetas HTML de una cadena usando BeautifulSoup."""
    if text:
        return BeautifulSoup(text, "html.parser").get_text()
    return ""

def analyze_sentiment(text):
    """Analizar el sentimiento del texto proporcionado."""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    if polarity > 0.1:
        sentiment = 'Positivo'
    elif polarity < -0.1:
        sentiment = 'Negativo'
    else:
        sentiment = 'Neutro'
        
    return {
        'sentiment': sentiment,
        'polarity': polarity,
        'subjectivity': subjectivity
    }

def process_article(article, idx, total):
    """Procesar un artículo individual para análisis de sentimiento."""
    full_text = article['title'] + " " + article['summary']
    sentiment_data = analyze_sentiment(full_text)
    article.update(sentiment_data)
    
    # Actualizar progreso
    st.session_state.progress = (idx + 1) / total
    
    return article

def create_sentiment_dataframe(articles):
    """Crear un DataFrame de pandas a partir de los artículos analizados."""
    df = pd.DataFrame(articles)
    
    if 'published' in df.columns:
        df['date'] = pd.to_datetime(df['published'], errors='coerce').dt.date
    
    return df

def generate_word_cloud(text):
    """Generar una nube de palabras a partir del texto proporcionado."""
    if not text.strip():
        return None
        
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        max_words=100
    ).generate(text)
    
    return wordcloud

def plot_sentiment_distribution(df):
    """Graficar la distribución del sentimiento."""
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentimiento', 'Cantidad']
    
    fig = px.pie(
        sentiment_counts, 
        values='Cantidad', 
        names='Sentimiento', 
        title='Distribución del Sentimiento'
    )
    return fig

def plot_sentiment_over_time(df):
    """Graficar sentimiento a lo largo del tiempo si hay datos disponibles."""
    if 'date' not in df.columns or df['date'].isna().all():
        return None
        
    sentiment_by_date = pd.crosstab(df['date'], df['sentiment'])
    sentiment_by_date = sentiment_by_date.reset_index()
    
    sentiment_by_date_long = pd.melt(
        sentiment_by_date, 
        id_vars=['date'], 
        value_vars=['Positivo', 'Neutro', 'Negativo'],
        var_name='Sentimiento',
        value_name='Cantidad'
    )
    
    fig = px.line(
        sentiment_by_date_long, 
        x='date', 
        y='Cantidad', 
        color='Sentimiento',
        title='Tendencias del Sentimiento en el Tiempo'
    )
    return fig

def plot_polarity_subjectivity(df):
    """Crear un diagrama de dispersión de polaridad vs subjetividad."""
    fig = px.scatter(
        df, 
        x='polarity', 
        y='subjectivity', 
        color='sentiment',
        hover_data=['title'],
        title='Polaridad vs Subjetividad'
    )
    
    fig.update_layout(
        xaxis_title="Polaridad (Negativo ⟷ Positivo)",
        yaxis_title="Subjetividad (Hecho ⟷ Opinión)"
    )
    
    return fig

def display_article_list(df):
    """Mostrar la lista de artículos con su sentimiento."""
    st.subheader("Artículos de Noticias")
    
    sentiment_badges = {
        'Positivo': '🟢 Positivo',
        'Neutro': '🔵 Neutro',
        'Negativo': '🔴 Negativo'
    }
    
    for i, row in df.iterrows():
        with st.expander(f"{row['title']} [{sentiment_badges[row['sentiment']]}]"):
            st.markdown(f"**Resumen:** {row['summary']}")
            st.markdown(f"**Polaridad:** {row['polarity']:.2f} | **Subjetividad:** {row['subjectivity']:.2f}")
            if row['link']:
                st.markdown(f"[Leer artículo completo]({row['link']})")

def main():
    """Función principal para la app de Streamlit."""
    st.title("📰 Analizador de Sentimiento de Noticias con IA")
    
    with st.sidebar:
        st.title("Configuración")
        
        topic = st.text_input("Buscar Tema:", value="tecnología")
        max_articles = st.slider("Máximo de Artículos:", min_value=10, max_value=1000, value=100)
        
        with st.expander("Opciones Avanzadas"):
            sentiment_threshold = st.slider(
                "Umbral de Sentimiento:", 
                min_value=0.0, 
                max_value=0.5, 
                value=0.1,
                help="Umbral para clasificar sentimiento como positivo/negativo"
            )
        
        st.markdown("---")
        st.subheader("Acerca de")
        st.info("""
        Esta herramienta analiza el sentimiento de artículos de noticias recientes sobre el tema que elijas.

        **Características:**
        - Búsqueda de noticias en tiempo real
        - Análisis de sentimiento
        - Visualizaciones interactivas
        - Análisis de tendencias

        Creado por: Oscar Walduin Orozco Cerón).
        """)
        
        st.markdown("---")
        st.caption("© 2025 Analizador de Noticias - Universidad Javeriana Cali")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("Ingresa un tema para analizar el sentimiento de las noticias recientes.")
        
        analyze_button = st.button("Analizar Noticias", use_container_width=True)
        
        if analyze_button or (topic and topic != st.session_state.last_topic):
            with st.spinner("Obteniendo artículos de noticias..."):
                articles = fetch_news(topic, max_articles)
                
            if not articles:
                st.warning("No se encontraron artículos. Intenta con otro tema.")
            else:
                st.session_state.progress = 0
                progress_bar = st.progress(0)
                
                total_articles = len(articles)
                with ThreadPoolExecutor(max_workers=min(8, total_articles)) as executor:
                    processed_articles = list(executor.map(
                        lambda x: process_article(x[1], x[0], total_articles),
                        enumerate(articles)
                    ))
                
                progress_bar.progress(1.0)
                time.sleep(0.5)
                progress_bar.empty()
                
                st.session_state.articles = processed_articles
                st.session_state.last_topic = topic
                st.session_state.sentiment_df = create_sentiment_dataframe(processed_articles)
                
                st.success(f"¡{len(processed_articles)} artículos analizados!")
    
    with col2:
        if st.session_state.sentiment_df is not None and not st.session_state.sentiment_df.empty:
            df = st.session_state.sentiment_df
            total = len(df)
            positive = sum(df['sentiment'] == 'Positivo')
            negative = sum(df['sentiment'] == 'Negativo')
            neutral = sum(df['sentiment'] == 'Neutro')
            
            #st.subheader("Resumen")
            #metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            #metrics_col1.metric("Positivo", f"{positive} ({positive/total*100:.1f}%)")
            #metrics_col2.metric("Neutro", f"{neutral} ({neutral/total*100:.1f}%)")
            #metrics_col3.metric("Negativo", f"{negative} ({negative/total*100:.1f}%)")
            st.image("Image/Escudo_Javeriana.jpg",  width=100)
    if st.session_state.sentiment_df is not None and not st.session_state.sentiment_df.empty:
        df = st.session_state.sentiment_df
        
        tab1, tab2, tab3, tab4 = st.tabs(["Artículos", "Análisis de Sentimiento", "Nube de Palabras", "Tendencias"])
        
        with tab1:
            display_article_list(df)
        
        with tab2:
            pie_col, scatter_col = st.columns(2)
            with pie_col:
                fig_pie = plot_sentiment_distribution(df)
                st.plotly_chart(fig_pie, use_container_width=True)
            with scatter_col:
                fig_scatter = plot_polarity_subjectivity(df)
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab3:
            all_text = " ".join([article['title'] + " " + article['summary'] for article in st.session_state.articles])
            wordcloud = generate_word_cloud(all_text)
            
            if wordcloud:
                st.subheader("Nube de Palabras")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                buf.seek(0)
                
                st.download_button(
                    label="Descargar Nube de Palabras",
                    data=buf,
                    file_name=f"nube_{topic}_{time.strftime('%Y%m%d')}.png",
                    mime="image/png"
                )
            else:
                st.warning("No hay suficiente texto para generar una nube de palabras.")
        
        with tab4:
            fig_trend = plot_sentiment_over_time(df)
            if fig_trend:
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Análisis temporal no disponible para estos artículos.")
            
            st.subheader("Exportar Datos")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Descargar Datos en CSV",
                csv,
                f"sentimiento_noticias_{topic}_{time.strftime('%Y%m%d')}.csv",
                "text/csv",
                key='download-csv'
            )

# Ejecutar la app
if __name__ == "__main__":
    main()
