import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64
from pathlib import Path
from datetime import datetime

# ==========================================
# 1. VARIABLES GLOBALES (CASCADA DE EDICIÓN)
# ==========================================
REFRESH_INT = 600000 
C_FONDO = "#0E1117"
C_AZUL = "#2b5dda"
C_NARANJA = "#FFBB4D"
ALT_SUP = 320
ALT_INF = 350

# ==========================================
# 2. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Administrativo de Riesgo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 3. ESTILOS CSS (SIN INDENTACIÓN PARA EVITAR ERRORES)
# ==========================================
# NOTA: No tabular ni dar espacios al inicio de las líneas de este bloque
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap');
[data-testid="stHeader"], header {{ display: none !important; height: 0px !important; }}
.stApp {{ margin-top: -90px !important; background-color: {C_FONDO} !important; }}
.main .block-container {{ padding: 0px 1rem !important; max-width: 100%; }}
html, body, .main {{ 
font-family: 'Roboto', sans-serif; 
overflow: hidden; 
background-color: {C_FONDO} !important;
color: white;
}}
.header-container {{
display: flex; justify-content: space-between; align-items: center;
padding: 15px 5px; background-color: {C_FONDO}; 
border-bottom: 2px solid #444; height: 8vh; margin-bottom: 30px;
}}
.title-main {{ font-size: 2rem; font-weight: bold; margin: 0; color: {C_AZUL}; }}
.subtitle-sub {{ font-size: 1.2rem; color: #ffffff; margin: 0; }}
.update-text {{ font-size: 1rem; color: {C_NARANJA}; text-align: right; line-height: 1.1; }}
[data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. FUNCIONES Y LÓGICA DE DATOS
# ==========================================
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return ""

st_autorefresh(interval=REFRESH_INT, key="datarefresh")

# Preparación de Encabezado
ahora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
logo_path = Path("assets/logo.png")
logo_b64 = get_base64(logo_path)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:5vh;">' if logo_b64 else ''

# Render de Encabezado (Sin espacios al inicio)
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

# ==========================================
# 5. FILA SUPERIOR
# ==========================================
col_sup_izq, col_sup_der = st.columns(2)

with col_sup_izq: #---------------------------------------------------------------------------TASA OVERNIGHT DIARIA
    try:
        # 1. CARGA Y PROCESAMIENTO DE DATOS
        df1 = pd.read_excel('Datos_Macroeconomicos.xlsx', 
                           sheet_name='Tasa Overnight Diaria', 
                           usecols="A,H")
        
        # Filtramos valores en cero, eliminamos vacíos y tomamos los últimos 7
        df1 = df1[df1.iloc[:, 1] != 0].dropna().tail(7)
        
        # Formateo de fechas
        fechas1 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df1.iloc[:, 0])]
        
        # 2. CONFIGURACIÓN DE LA TRAZA (Línea y Marcadores)
        fig1 = go.Figure(go.Scatter(
            x=fechas1, 
            y=df1.iloc[:, 1], 
            mode='lines+markers+text', 
            text=[f"{val}%" for val in df1.iloc[:, 1]], 
            textposition="top center", 
            cliponaxis=False, 
            line=dict(
                color='#60CCC8', 
                width=4, 
                shape='spline'
            ), 
            marker=dict(
                size=10, 
                color='#FFFFFF', 
                line=dict(width=2, color='#60CCC8')
            ), 
            textfont=dict(
                size=16, 
                color="white"
            )
        ))
        
        # 3. DISEÑO Y ESTÉTICA (Layout)
        fig1.update_layout(
            title="Tasa Overnight Diaria", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_SUP, 
            margin=dict(l=10, r=10, t=30, b=40), 
            xaxis=dict(
                tickangle=-30, 
                tickfont=dict(color="white", size=15)
            ), 
            yaxis=dict(
                gridcolor='#222222', 
                tickfont=dict(color="white")
            ), 
            font=dict(color="#2b5dda") # Aquí es donde definiste el color del título
        )
        
        # 4. RENDERIZADO EN STREAMLIT
        st.plotly_chart(
            fig1, 
            use_container_width=True, 
            config={'displayModeBar': False}
        )
        
    except Exception as e: 
        st.error(f"Error G1: {e}")

with col_sup_der: #-------------------------------------------------------------------------- RESERVAS EXCEDENTARIAS
    try:
        # 1. CARGA Y PROCESAMIENTO DE DATOS
        df2 = pd.read_excel('Datos_Macroeconomicos.xlsx', 
                           sheet_name='Reservas Bancarias Excedentari', 
                           usecols="A,B")
        
        # Limpieza, toma de los primeros 7 y reversión de orden
        df2 = df2.dropna().head(7).iloc[::-1]
        
        # Formateo de fechas
        fechas2 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df2.iloc[:, 0])]
        
        # 2. CONFIGURACIÓN DEL GRÁFICO (Barras)
        fig2 = go.Figure(go.Bar(
            x=fechas2, 
            y=df2.iloc[:, 1]/1000, 
            text=[f"{v/1000:,.3f}MM" for v in df2.iloc[:, 1]], 
            textposition='outside', 
            marker_color=C_AZUL, 
            cliponaxis=False, 
            textfont=dict(
                size=16, 
                color="white"
            )
        ))
        
        # 3. DISEÑO Y ESTÉTICA (Layout)
        fig2.update_layout(
            title="Reservas Bancarias Excedentarias", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_SUP, 
            margin=dict(l=10, r=10, t=30, b=40), 
            xaxis=dict(
                tickangle=-30, 
                tickfont=dict(color="white", size=15)
            ), 
            yaxis=dict(
                gridcolor='#222222', 
                tickfont=dict(color="white")
            ), 
            font=dict(color=C_AZUL)
        )
        
        # 4. RENDERIZADO
        st.plotly_chart(
            fig2, 
            use_container_width=True, 
            config={'displayModeBar': False}
        )
        
    except Exception as e: 
        st.error(f"Error G2: {e}")
# ==========================================
# 6. FILA INFERIOR
# ==========================================
col_inf_1, col_inf_2, col_inf_3, col_inf_4 = st.columns([0.2, 0.2, 0.3, 0.3])

with col_inf_1: #-----------------------------------------------------------------------------------------TASA OVERNIGHT MENSUAL
    try:
        # 1. EXTRACCIÓN Y LIMPIEZA DE DATOS
        df3 = pd.read_excel('Datos_Macroeconomicos.xlsx', 
                           sheet_name='Tasa Overnight Mensual', 
                           usecols="A,D").iloc[0:5]
        
        # 2. CONFIGURACIÓN DE LA TRAZA (Línea y Puntos)
        fig3 = go.Figure(go.Scatter(
            x=df3.iloc[:, 0], 
            y=df3.iloc[:, 1], 
            mode='lines+markers+text', 
            text=[f"{val}%" for val in df3.iloc[:, 1]], 
            textposition="top center", 
            cliponaxis=False, 
            line=dict(
                color=C_NARANJA, 
                width=3, 
                shape='spline'  # Esto mantiene la curvatura suave
            ), 
            textfont=dict(
                size=15, 
                color="white"
            )
        ))
        
        # 3. DISEÑO Y ESTÉTICA (Layout)
        fig3.update_layout(
            title="Tasa Overnight Mensual", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_INF, 
            margin=dict(l=5, r=5, t=30, b=30), 
            xaxis=dict(
                tickfont=dict(color="white", size=15) # Fechas legibles
            ), 
            yaxis=dict(
                showticklabels=False, 
                gridcolor='#222222'
            ), 
            font=dict(color=C_AZUL)
        )
        
        # 4. RENDERIZADO
        st.plotly_chart(
            fig3, 
            use_container_width=True, 
            config={'displayModeBar': False}
        )
        
    except Exception as e: 
        st.error(f"Error G3: {e}")

with col_inf_2: #------------------------------------------------------------------------------------------BASE MONETARIA
    try:
        df4 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Base Monetaria', usecols="A,B,C")
        df4['Fecha_DT'] = pd.to_datetime(df4.iloc[:, 0])
        hoy = datetime.now()
        
        # Filtrado de datos
        df_f4 = df4[(df4['Fecha_DT'].dt.month == hoy.month) & (df4['Fecha_DT'].dt.year == hoy.year)]
        if df_f4.empty:
            m, a = (hoy.month-1, hoy.year) if hoy.month > 1 else (12, hoy.year-1)
            df_f4 = df4[(df4['Fecha_DT'].dt.month == m) & (df4['Fecha_DT'].dt.year == a)]
        
        df_f4 = df_f4.sort_values('Fecha_DT')
        fechas4 = [d.strftime('%d/%m/%Y') for d in df_f4['Fecha_DT']]
        montos4, var4 = df_f4.iloc[:, 1] / 1000000, df_f4.iloc[:, 2]
        
        fig4 = go.Figure()

        # 1. BARRAS: Aumenté el tamaño del texto a 12
        fig4.add_trace(go.Bar(
            x=fechas4, 
            y=montos4, 
            text=[f"{v:,.1f}MM" for v in montos4], 
            textposition='outside', 
            marker_color='#4D79FF', 
            textfont=dict(color="white", size=15) 
        ))

        # 2. LÍNEA DE VARIACIÓN: Agregué 'spline' para curvatura y subí el texto
        escala4 = montos4.max() / (var4.abs().max() if var4.abs().max() != 0 else 1)
        fig4.add_trace(go.Scatter(
            x=fechas4, 
            y=var4 * escala4 * 0.7, # Subí un poco la posición para que no choque con la base
            mode='lines+markers+text', 
            text=[f"{v:.2f}%" for v in var4], 
            textposition="top center", # Cambiado a top para mejor visibilidad
            line=dict(color=C_NARANJA, width=3, shape='spline'), # Línea curva
            marker=dict(size=8, color='white'), 
            textfont=dict(color=C_NARANJA, size=15),
            cliponaxis=False # Evita que el texto se corte en los bordes
        ))

        # 3. LAYOUT: Eje X más grande y ajuste de rango Y para que quepa todo
        fig4.update_layout(
            title="Base Monetaria", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_INF, 
            margin=dict(l=5, r=5, t=30, b=40), 
            xaxis=dict(tickfont=dict(color="white", size=15)), # Fechas más grandes
            yaxis=dict(
                showticklabels=False, 
                gridcolor='#222222',
                range=[montos4.min()*-0.4, montos4.max()*1.4] # Margen extra arriba y abajo
            ), 
            font=dict(color=C_AZUL), 
            showlegend=False
        )
        
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: 
        st.error(f"Error G4: {e}") #FIN BASE MONETARIA

with col_inf_3: #--------------------------------------------------------------------------------------------------LIQUIDEZ MONETARIA
    try:
        # 1. CARGA Y FILTRADO DE DATOS
        df5 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Liquidez Monetaria', usecols="A,G,H")
        df5['Fecha_DT'] = pd.to_datetime(df5.iloc[:, 0])
        hoy = datetime.now()
        
        # Lógica de filtrado (Mes actual o anterior)
        df_f5 = df5[(df5['Fecha_DT'].dt.month == hoy.month) & (df5['Fecha_DT'].dt.year == hoy.year)]
        if df_f5.empty:
            m, a = (hoy.month-1, hoy.year) if hoy.month > 1 else (12, hoy.year-1)
            df_f5 = df5[(df5['Fecha_DT'].dt.month == m) & (df5['Fecha_DT'].dt.year == a)]
            
        df_f5 = df_f5.sort_values('Fecha_DT')
        fechas5 = [d.strftime('%d/%m/%Y') for d in df_f5['Fecha_DT']]
        montos5, var5 = df_f5.iloc[:, 1] / 1000000, df_f5.iloc[:, 2]

        # 2. INICIALIZACIÓN DEL GRÁFICO
        fig5 = go.Figure()

        # 3. TRAZA DE BARRAS (Igualado a tamaño 15 como el G4)
        fig5.add_trace(go.Bar(
            x=fechas5, 
            y=montos5, 
            text=[f"{int(v):,}MM" for v in montos5], 
            textposition='outside', 
            marker_color='#60CCC8', 
            textfont=dict(color="white", size=15)
        ))

        # 4. TRAZA DE LÍNEA DE VARIACIÓN (Curva Spline)
        escala5 = montos5.max() / (var5.abs().max() if var5.abs().max() != 0 else 1)
        
        fig5.add_trace(go.Scatter(
            x=fechas5, 
            y=var5 * escala5 * 0.7, # Ajustado igual que G4
            mode='lines+markers+text', 
            text=[f"{v:.2f}%" for v in var5], 
            textposition="top center", 
            cliponaxis=False, 
            line=dict(
                color=C_NARANJA, 
                width=3, 
                shape='spline' # Línea curva suave
            ), 
            marker=dict(size=8, color='white'), 
            textfont=dict(color=C_NARANJA, size=15)
        ))

        # 5. CONFIGURACIÓN DEL DISEÑO (Mismo alto que G4)
        fig5.update_layout(
            title="Liquidez Monetaria", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_INF, # Asegura que el alto sea idéntico al G4
            margin=dict(l=5, r=10, t=35, b=40), 
            xaxis=dict(
                tickfont=dict(color="white", size=15) # Fechas tamaño 15
            ), 
            yaxis=dict(
                showticklabels=False, 
                gridcolor='#222222',
                range=[montos5.min()*-0.4, montos5.max()*1.4] # Rango expandido para visibilidad
            ), 
            font=dict(color=C_AZUL), 
            showlegend=False
        )

        # 6. RENDERIZADO
        st.plotly_chart(
            fig5, 
            use_container_width=True, 
            config={'displayModeBar': False}
        )

    except Exception as e: 
        st.error(f"Error G5: {e}") #FIN LIQUIDEZ MONETARIA

with col_inf_4: #-------------------------------------------------------------------------------------RESERVAS INTERNACIONALES EN DOLARES $
    try:
        # 1. CARGA Y PROCESAMIENTO DE DATOS
        df6 = pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name='Resev. Internacionales $', usecols="A,D,E")
        df6['Fecha_DT'] = pd.to_datetime(df6.iloc[:, 0])
        hoy = datetime.now()
        
        # Lógica de filtrado de fechas
        df_f6 = df6[(df6['Fecha_DT'].dt.month == hoy.month) & (df6['Fecha_DT'].dt.year == hoy.year)]
        if df_f6.empty:
            m, a = (hoy.month-1, hoy.year) if hoy.month > 1 else (12, hoy.year-1)
            df_f6 = df6[(df6['Fecha_DT'].dt.month == m) & (df6['Fecha_DT'].dt.year == a)]
            
        df_f6 = df_f6.sort_values('Fecha_DT')
        fechas6 = [d.strftime('%d/%m/%Y') for d in df_f6['Fecha_DT']]
        montos6, var6 = df_f6.iloc[:, 1], df_f6.iloc[:, 2]

        # 2. INICIALIZACIÓN DEL GRÁFICO
        fig6 = go.Figure()

        # 3. TRAZA DE BARRAS (Montos en MM)
        fig6.add_trace(go.Bar(
            x=fechas6, 
            y=montos6, 
            text=[f"{int(v):,}MM" for v in montos6], 
            textposition='outside', 
            marker_color='#9E7BFF', 
            textfont=dict(color="white", size=15)
        ))

        # 4. TRAZA DE LÍNEA (Variación % Curva)
        escala6 = montos6.max() / (var6.abs().max() if var6.abs().max() != 0 else 1)
        
        fig6.add_trace(go.Scatter(
            x=fechas6, 
            y=var6 * escala6 * 0.7, 
            mode='lines+markers+text', 
            text=[f"{v:.2f}%" for v in var6], 
            textposition="top center", 
            cliponaxis=False, 
            line=dict(
                color=C_NARANJA, 
                width=3, 
                shape='spline' # Línea con curvatura suave
            ), 
            marker=dict(size=8, color='white'), 
            textfont=dict(color=C_NARANJA, size=16)
        ))

        # 5. CONFIGURACIÓN DEL DISEÑO (Layout consistente)
        fig6.update_layout(
            title="Reservas Internacionales $", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_INF, 
            margin=dict(l=5, r=10, t=35, b=40), 
            xaxis=dict(
                tickfont=dict(color="white", size=16)
            ), 
            yaxis=dict(
                showticklabels=False, 
                gridcolor='#222222',
                range=[montos6.min()*-0.4, montos6.max()*1.4]
            ), 
            font=dict(color=C_AZUL), 
            showlegend=False
        )

        # 6. RENDERIZADO
        st.plotly_chart(
            fig6, 
            use_container_width=True, 
            config={'displayModeBar': False}
        )

    except Exception as e: 
        st.error(f"Error G6: {e}")
