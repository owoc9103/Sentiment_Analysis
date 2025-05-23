# descarga_datos.py
import yfinance as yf
import pandas as pd

def obtener_datos_tesla(fecha_inicio: str, fecha_fin: str):
    data = yf.download("TSLA", start=fecha_inicio, end=fecha_fin)
    return data