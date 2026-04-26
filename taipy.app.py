import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64
from pathlib import Path
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Dashboard Administrativo de Riesgo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. AUTO-REFRESH (Cada 10 minutos)
st_autorefresh(interval=600000, key="datarefresh")

# 3. CSS "HARD" PARA ELIMINAR ESPACIO SUPERIOR (ZERO MARGIN)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap');
    
    /* Ocultar headers de sistema de Streamlit */
    [data-testid="stHeader"], header {
        display: none !important;
        height: 0px !important;
    }
    
    /* Eliminar el padding superior del contenedor de la app */
    .stApp {
        margin-top: -85px !important;
    }

    /* Forzar que el bloque de contenido no tenga espacios */
    .main .block-container {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100%;
    }

    /* Estética de fondo y fuentes */
    html, body, .main { 
        font-family: 'Roboto', sans-serif; 
        overflow: hidden; 
        background-color: #0E1117;
    }

    /* Contenedor del encabezado personalizado */
    .header-container {
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        padding: 5px 15px;
        background-color: #0E1117; 
        border-bottom: 1px solid #444;
        height: 7vh;
        margin-bottom: 5px;
    }
    
    .title-main { font-size: 1.3rem; font-weight: bold; margin: 0; color: #2b5dda; line-height: 1.1; }
    .subtitle-sub { font-size: 0.75rem; color: #ffffff; margin: 0; }
    .update-text { font-size: 0.65rem; color: #FFBB4D; text-align: right; line-height: 1.1; }
    
    /* Quitar gaps entre elementos de Streamlit */
    [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNCIONES Y ENCABEZADO
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return ""

ahora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
logo_path = Path("assets/logo.png")
logo_html = f'<img src="data:image/png;base64,{get_base64(logo_path)}" style="height:4vh;">' if logo_path.exists() else ''

# Encabezado corregido para evitar renderizado de texto plano
st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; align-items: center; gap: 20px;">
            {logo_html}
            <div>
                <p class="title-main">Unidad Administrativa Integral de Riesgo</p>
                <p class="subtitle-sub">Indicadores Macroeconómicos BCV.</p>
            </div>
        </div>
        <div class="update-text">Última actualización:<br><b>{ahora}</b></div>
    </div>
    """, unsafe_allow_html=True)

# --- ALTURAS OPTIMIZADAS PARA EVITAR SCROLL ---
alt_sup = 380 
alt_inf = 260
m_plotly = dict(l=10, r=10, t=30, b=30)

# --- FILA SUPERIOR ---
col_sup_izq, col_sup_der = st.columns(2)

with col_sup_izq:
    try:
        df1 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Tasa Overnight Diaria', usecols="A,H")
        df1 = df1[df1.iloc[:, 1] != 0].dropna().tail(7)
        fechas1 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df1.iloc[:, 0])]
        fig1 = go.Figure(go.Scatter(x=fechas1, y=df1.iloc[:, 1], mode='lines+markers+text', text=[f"{val}%" for val in df1.iloc[:, 1]], textposition="top center", cliponaxis=False, line=dict(color='#60CCC8', width=4, shape='spline'), marker=dict(size=10, color='#FFFFFF', line=dict(width=2, color='#60CCC8')), textfont=dict(size=13, color="white")))
        fig1.update_layout(title="Tasa Overnight Diaria", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=alt_sup, margin=m_plotly, xaxis=dict(tickangle=-30, tickfont=dict(color="white", size=9)), yaxis=dict(gridcolor='#222222', tickfont=dict(color="white")), font=dict(color="#2b5dda"))
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G1: {e}")

with col_sup_der:
    try:
        df2 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Reservas Bancarias Excedentari', usecols="A,B")
        df2 = df2.dropna().head(7).iloc[::-1]
        fechas2 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df2.iloc[:, 0])]
        fig2 = go.Figure(go.Bar(x=fechas2, y=df2.iloc[:, 1]/1000, text=[f"{v/1000:,.3f}MM" for v in df2.iloc[:, 1]], textposition='outside', marker_color='#2b5dda', cliponaxis=False, textfont=dict(size=13, color="white")))
        fig2.update_layout(title="Reservas Bancarias Excedentarias", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=alt_sup, margin=m_plotly, xaxis=dict(tickangle=-30, tickfont=dict(color="white", size=9)), yaxis=dict(gridcolor='#222222', tickfont=dict(color="white")), font=dict(color="#2b5dda"))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G2: {e}")

# --- FILA INFERIOR ---
col_inf_1, col_inf_2, col_inf_3, col_inf_4 = st.columns([0.2, 0.2, 0.3, 0.3])

# 1. Tasa Overnight Mensual
with col_inf_1:
    try:
        df3 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Tasa Overnight Mensual', usecols="A,D").iloc[0:5]
        fig3 = go.Figure(go.Scatter(x=df3.iloc[:, 0], y=df3.iloc[:, 1], mode='lines+markers+text', text=[f"{val}%" for val in df3.iloc[:, 1]], textposition="top center", cliponaxis=False, line=dict(color='#FFBB4D', width=3, shape='spline'), textfont=dict(size=10, color="white")))
        fig3.update_layout(title="Tasa Overnight Mensual", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=alt_inf, margin=m_plotly, xaxis=dict(tickfont=dict(color="white", size=8)), yaxis=dict(showticklabels=False, gridcolor='#222222'), font=dict(color="#2b5dda"))
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G3: {e}")

# 2. Base Monetaria
with col_inf_2:
    try:
        df4 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Base Monetaria', usecols="A,B,C")
        df4['Fecha_DT'] = pd.to_datetime(df4.iloc[:, 0])
        hoy = datetime.now()
        df_f4 = df4[(df4['Fecha_DT'].dt.month == hoy.month) & (df4['Fecha_DT'].dt.year == hoy.year)].sort_values('Fecha_DT')
        fechas4 = [d.strftime('%d/%m/%Y') for d in df_f4['Fecha_DT']]
        montos4 = df_f4.iloc[:, 1] / 1000000
        fig4 = go.Figure(go.Bar(x=fechas4, y=montos4, text=[f"{v:,.1f}MM" for v in montos4], textposition='inside', marker_color='#4D79FF', textfont=dict(size=9)))
        fig4.update_layout(title="Base Monetaria", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=alt_inf, margin=m_plotly, xaxis=dict(tickfont=dict(color="white", size=8)), yaxis=dict(showticklabels=False), font=dict(color="#2b5dda"))
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G4: {e}")

# 3. Liquidez Monetaria
with col_inf_3:
    try:
        df5 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Liquidez Monetaria', usecols="A,G,H")
        df5['Fecha_DT'] = pd.to_datetime(df5.iloc[:, 0])
        df_f5 = df5.tail(5).sort_values('Fecha_DT')
        fechas5 = [d.strftime('%d/%m/%Y') for d in df_f5['Fecha_DT']]
        montos5 = df_f5.iloc[:, 1] / 1000000
        fig5 = go.Figure(go.Bar(x=fechas5, y=montos5, text=[f"{int(v):,}MM" for v in montos5], textposition='inside', marker_color='#60CCC8'))
        fig5.update_layout(title="Liquidez Monetaria", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=alt_inf, margin=m_plotly, xaxis=dict(tickfont=dict(color="white", size=8)), yaxis=dict(showticklabels=False), font=dict(color="#2b5dda"))
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G5: {e}")

# 4. Reservas Internacionales $
with col_inf_4:
    try:
        df6 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Resev. Internacionales $', usecols="A,D,E")
        df6['Fecha_DT'] = pd.to_datetime(df6.iloc[:, 0])
        df_f6 = df6.tail(5).sort_values('Fecha_DT')
        fechas6 = [d.strftime('%d/%m/%Y') for d in df_f6['Fecha_DT']]
        montos6 = df_f6.iloc[:, 1]
        fig6 = go.Figure(go.Bar(x=fechas6, y=montos6, text=[f"{int(v):,}MM" for v in montos6], textposition='inside', marker_color='#9E7BFF'))
        fig6.update_layout(title="Reservas Internacionales $", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=alt_inf, margin=m_plotly, xaxis=dict(tickfont=dict(color="white", size=8)), yaxis=dict(showticklabels=False), font=dict(color="#2b5dda"))
        st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G6: {e}")
