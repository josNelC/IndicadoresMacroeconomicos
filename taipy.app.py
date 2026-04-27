import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64
from pathlib import Path
from datetime import datetime
import inspect

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Administrativo de Riesgo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. VARIABLES DE ESTILO (EDICIÓN RÁPIDA)
# ==========================================
FONDO_OSCURO = "#0E1117"
AZUL_TITULO = "#2b5dda"
NARANJA_TEXTO = "#FFBB4D"
GRIS_BORDE = "#444"
ALT_SUP = 370
ALT_INF = 290
INTERVALO_REFRESCO = 10000 

# ==========================================
# 3. FUNCIONES DE APOYO (BLINDAJE HTML)
# ==========================================
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f: 
            return base64.b64encode(f.read()).decode()
    except: 
        return ""

def render_custom_css():
    # El uso de inspect.cleandoc elimina espacios al inicio que rompen el HTML en Streamlit
    css = inspect.cleandoc(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;400;700;900&display=swap');
            html, body, [data-testid="stAppViewContainer"], .main, .stApp {{
                background-color: {FONDO_OSCURO} !important;
                color: white;
                font-family: 'Roboto', sans-serif;
                overflow: hidden;
            }}
            [data-testid="stHeader"], header, [data-testid="stToolbar"] {{
                display: none !important;
            }}
            .stApp {{ margin-top: -90px !important; }}
            .main .block-container {{ padding: 0px 1rem !important; max-width: 100%; }}
            .header-container {{
                display: flex; justify-content: space-between; align-items: center;
                padding: 10px 5px; background-color: {FONDO_OSCURO} !important; 
                border-bottom: 2px solid {GRIS_BORDE}; height: 8vh; margin-bottom: 10px;
            }}
            .title-main {{ font-size: 1.4rem; font-weight: bold; margin: 0; color: {AZUL_TITULO}; }}
            .subtitle-sub {{ font-size: 0.8rem; color: #ffffff; margin: 0; }}
            .update-text {{ font-size: 0.7rem; color: {NARANJA_TEXTO}; text-align: right; line-height: 1.1; }}
            [data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}
        </style>
    """)
    st.markdown(css, unsafe_allow_html=True)

# ==========================================
# 4. EJECUCIÓN DE INTERFAZ
# ==========================================
st_autorefresh(interval=INTERVALO_REFRESCO, key="datarefresh")
render_custom_css()

# Preparación de datos del encabezado
ahora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
logo_path = Path("assets/logo.png")
logo_b64 = get_base64(logo_path)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:5vh;">' if logo_b64 else ''

# Encabezado en una sola línea para evitar que el intérprete lo lea como código
header_html = inspect.cleandoc(f"""
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
""")
st.markdown(header_html, unsafe_allow_html=True)

# ==========================================
# 5. FILA SUPERIOR
# ==========================================
col_sup_izq, col_sup_der = st.columns(2)

with col_sup_izq:
    try:
        df1 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Tasa Overnight Diaria', usecols="A,H")
        df1 = df1[df1.iloc[:, 1] != 0].dropna().tail(7)
        fechas1 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df1.iloc[:, 0])]
        fig1 = go.Figure(go.Scatter(x=fechas1, y=df1.iloc[:, 1], mode='lines+markers+text', 
                                    text=[f"{val}%" for val in df1.iloc[:, 1]], textposition="top center",
                                    line=dict(color='#60CCC8', width=4, shape='spline'),
                                    marker=dict(size=10, color='#FFFFFF', line=dict(width=2, color='#60CCC8'))))
        fig1.update_layout(title="Tasa Overnight Diaria", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          height=ALT_SUP, margin=dict(l=10, r=10, t=30, b=40),
                          xaxis=dict(tickangle=-30, tickfont=dict(color="white", size=10)),
                          yaxis=dict(gridcolor='#222222', tickfont=dict(color="white")), font=dict(color=AZUL_TITULO))
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G1: {e}")

with col_sup_der:
    try:
        df2 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Reservas Bancarias Excedentari', usecols="A,B")
        df2 = df2.dropna().head(7).iloc[::-1]
        fechas2 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df2.iloc[:, 0])]
        fig2 = go.Figure(go.Bar(x=fechas2, y=df2.iloc[:, 1]/1000, text=[f"{v/1000:,.3f}MM" for v in df2.iloc[:, 1]], 
                                textposition='outside', marker_color=AZUL_TITULO))
        fig2.update_layout(title="Reservas Bancarias Excedentarias", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          height=ALT_SUP, margin=dict(l=10, r=10, t=30, b=40),
                          xaxis=dict(tickangle=-30, tickfont=dict(color="white", size=10)),
                          yaxis=dict(gridcolor='#222222', tickfont=dict(color="white")), font=dict(color=AZUL_TITULO))
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G2: {e}")

# ==========================================
# 6. FILA INFERIOR
# ==========================================
col_inf_1, col_inf_2, col_inf_3, col_inf_4 = st.columns([0.2, 0.2, 0.3, 0.3])

def apply_inf_style(fig, title):
    fig.update_layout(title=title, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                     height=ALT_INF, margin=dict(l=5, r=5, t=30, b=30),
                     xaxis=dict(tickfont=dict(color="white", size=9)),
                     yaxis=dict(showticklabels=False, gridcolor='#222222'),
                     font=dict(color=AZUL_TITULO), showlegend=False)

with col_inf_1:
    try:
        df3 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Tasa Overnight Mensual', usecols="A,D").iloc[0:5]
        fig3 = go.Figure(go.Scatter(x=df3.iloc[:, 0], y=df3.iloc[:, 1], mode='lines+markers+text', 
                                    text=[f"{val}%" for val in df3.iloc[:, 1]], textposition="top center",
                                    line=dict(color=NARANJA_TEXTO, width=3, shape='spline')))
        apply_inf_style(fig3, "Tasa Overnight Mensual")
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G3: {e}")

with col_inf_2:
    try:
        df4 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Base Monetaria', usecols="A,B,C")
        df_f4 = df4.tail(5)
        fechas4 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df_f4.iloc[:, 0])]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=fechas4, y=df_f4.iloc[:, 1]/1000000, marker_color='#4D79FF'))
        apply_inf_style(fig4, "Base Monetaria")
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G4: {e}")

with col_inf_3:
    try:
        df5 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Liquidez Monetaria', usecols="A,G,H")
        df_f5 = df5.tail(5)
        fechas5 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df_f5.iloc[:, 0])]
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(x=fechas5, y=df_f5.iloc[:, 1]/1000000, marker_color='#60CCC8'))
        apply_inf_style(fig5, "Liquidez Monetaria")
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G5: {e}")

with col_inf_4:
    try:
        df6 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Resev. Internacionales $', usecols="A,D,E")
        df_f6 = df6.tail(5)
        fechas6 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df_f6.iloc[:, 0])]
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(x=fechas6, y=df_f6.iloc[:, 1], marker_color='#9E7BFF'))
        apply_inf_style(fig6, "Reservas Internacionales $")
        st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error G6: {e}")
