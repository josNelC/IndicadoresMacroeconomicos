import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. Configuración de página
st.set_page_config(page_title="Sala Situacional - UIAR", layout="wide")

# Refresco automático cada 5 minutos
st_autorefresh(interval=300000, key="datarefresh")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;} 
    .stAppDeployButton {display:none;}
    
    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
        max-width: 100%; 
        background-color: #f2f2f2; 
    }

    html, body, [class*="css"], .main { 
        font-family: 'Poppins', sans-serif; 
        background-color: #f8f9fc; 
    }
    
    .titulo-principal { color: #1a202c; font-size: 32px; font-weight: 600; margin: 0; line-height: 1.1; }
    .subtitulo-principal { color: #2B5DDA; font-size: 24px; font-weight: 300; margin: 0; }
    
    .contenedor-titulos { margin-bottom: 10px; padding-left: 10px; }
    .grafico-titulo { 
        color: #2b5dda; 
        font-family: 'Poppins', sans-serif; 
        font-size: 28px; 
        font-weight: 400; 
        margin: 0; 
    }
    .grafico-subtitulo { 
        color: #333; 
        font-family: 'Poppins', sans-serif; 
        font-size: 24px; 
        font-weight: 300; 
        margin: 0; 
    }
    
    [data-testid="stMetricValue"] { font-size: 22px !important; font-family: 'Poppins', sans-serif !important; }
    [data-testid="stMetricLabel"] { font-size: 13px !important; }
    
    .stMetric { 
        background-color: white; 
        padding: 8px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }

    /* --- NUEVA REGLA PARA BORDES DE GRÁFICOS --- */
    .stPlotlyChart {
        border: 1px solid #2b5dda;
        border-radius: 15px;
        overflow: hidden; /* Asegura que el gráfico no se salga de las esquinas redondeadas */
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
col_logo, col_titulo = st.columns([2, 8])
with col_logo:
    try: 
        st.image("assets/logo.png", width=400) 
    except: 
        st.info("Logo UIAR")

with col_titulo:
    st.markdown('<p class="titulo-principal">Sala Situacional</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo-principal">Unidad Integral de Administración de Riesgo</p>', unsafe_allow_html=True)

st.markdown("<hr style='margin:10px 0px'>", unsafe_allow_html=True)

ruta = r"C:\Monitor_test\Data_Situacional_Ejemplo.xlsx"

# --- FUNCIONES DE FORMATO ---
def format_mm(valor):
    try:
        if pd.isna(valor): return "0"
        if abs(valor) >= 1_000_000: return f"{valor/1_000_000:.1f}MM"
        return f"{valor:,.0f}"
    except: return "0"

def fix_percent(x):
    if pd.isna(x): return "0.00%"
    try:
        if abs(x) < 1.0: return f"{x*100:.2f}%"
        return f"{x:.2f}%"
    except: return "0.00%"

# ==========================================
# GRAFICO 1: LIQUIDEZ MONETARIA (CORREGIDO)
# ==========================================
try:
    df_liq = pd.read_excel(ruta, sheet_name='Liquidez Monetaria')
    
    # 1. Limpiamos filas que estén totalmente vacías o donde la columna de Liquidez sea NaN
    # Usamos la columna en el índice 6 (Liquidez) para validar que haya datos reales
    df_liq = df_liq.dropna(subset=[df_liq.columns[6]])
    
    # 2. Ahora sí tomamos las últimas 6 filas reales
    data_liq = df_liq.tail(6).reset_index(drop=True) 
    
    # Seleccionamos columnas y renombramos
    data_liq = data_liq.iloc[:, [0, 6, 7]] 
    data_liq.columns = ['Semana', 'Liquidez', 'Variacion']
    
    # Convertimos la columna Semana a string para evitar el error "NaT" en el eje X
    data_liq['Semana_Txt'] = data_liq['Semana'].dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_any_dtype(data_liq['Semana']) else data_liq['Semana'].astype(str)
    
    data_liq['Liquidez_Label'] = data_liq['Liquidez'].apply(format_mm)
    data_liq['Var_Label'] = data_liq['Variacion'].apply(lambda x: f"<b>{fix_percent(x)}</b>")

    col_graf, col_met = st.columns([8, 2])

    with col_graf:
        st.markdown('<div class="contenedor-titulos"><p class="grafico-titulo">Liquidez Monetaria</p></div>', unsafe_allow_html=True)
        
        fig1 = go.Figure()

        # Serie Principal
        fig1.add_trace(go.Scatter(
            x=data_liq['Semana_Txt'], y=data_liq['Liquidez'], 
            mode='lines+markers+text', 
            text=data_liq['Liquidez_Label'], textposition="top center",
            line=dict(color='#5a67d8', width=3),
            marker=dict(size=8, color="#fd941c", line=dict(width=2, color='white')),
            textfont=dict(family="Poppins", size=11, color="#2b5dda"),
            name="Liquidez"
        ))
        
        # Variación % (se mantiene igual...)
        pos = data_liq[data_liq['Variacion'] >= 0]
        fig1.add_trace(go.Scatter(
            x=pos['Semana_Txt'], y=pos['Variacion'], yaxis="y2",
            mode='markers+text',
            text=pos['Var_Label'], textposition="bottom center",
            textfont=dict(family="Poppins", size=10, color="#2F855A"), 
            marker=dict(opacity=0), showlegend=False
        ))

        neg = data_liq[data_liq['Variacion'] < 0]
        fig1.add_trace(go.Scatter(
            x=neg['Semana_Txt'], y=neg['Variacion'], yaxis="y2",
            mode='markers+text',
            text=neg['Var_Label'], textposition="bottom center",
            textfont=dict(family="Poppins", size=10, color="#C53030"), 
            marker=dict(opacity=0), showlegend=False
        ))

        fig1.add_trace(go.Scatter(
            x=data_liq['Semana_Txt'], y=data_liq['Variacion'], yaxis="y2",
            mode='lines', line=dict(color='#A0AEC0', width=1, dash='dot'),
            hoverinfo='skip', showlegend=False
        ))

        fig1.update_layout(
            plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', height=300, 
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(type='category', showgrid=False, tickfont=dict(family="Poppins", size=10, color="#000000")),
            yaxis=dict(showgrid=True, gridcolor='#edf2f7', tickfont=dict(family="Poppins", size=10, color="#000000")),
            yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False),
            showlegend=False, hovermode="x unified"
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    with col_met:
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.metric("Actual", f"Bs. {data_liq['Liquidez'].iloc[-1]:,.0f}", delta=fix_percent(data_liq['Variacion'].iloc[-1]))
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.metric("Promedio", f"Bs. {data_liq['Liquidez'].mean():,.0f}")

except Exception as e:
    st.error(f"Error en Liquidez: {e}")

# ==========================================
# FILA 2: BASES Y RESERVAS (EJES OPTIMIZADOS)
# ==========================================
col_inf_izq, col_inf_der = st.columns([2, 2]) 

with col_inf_izq:
    try:
        df_bases = pd.read_excel(ruta, sheet_name='Bases Monetarias', usecols="A:C")
        data_bases = df_bases.dropna(how='all').tail(6).copy()
        data_bases.columns = ['Fecha', 'Monto', 'Variacion']
        data_bases['Fecha_Eje'] = pd.to_datetime(data_bases['Fecha']).dt.strftime('%Y-%m-%d')
        
        st.markdown('<div class="contenedor-titulos"><p class="grafico-titulo">Bases Monetarias BS.</p> <p class="grafico-subtitulo">Últimas seis (6) Semanas</p></div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        
        # 1. Barras con Montos HORIZONTALES
        fig2.add_trace(go.Bar(
            x=data_bases['Fecha_Eje'], y=data_bases['Monto'], 
            text=data_bases['Monto'].apply(format_mm), 
            textposition='inside', 
            insidetextanchor='middle',
            textangle=0, 
            textfont=dict(family="Poppins", size=11, color="white"), 
            marker_color="#90A4AE", name="Monto"
        ))

        # 2. Línea de tendencia
        fig2.add_trace(go.Scatter(
            x=data_bases['Fecha_Eje'], y=data_bases['Variacion'], yaxis="y2",
            mode='lines', 
            line=dict(color="#E0F7FA", width=2, dash='dot'),
            hoverinfo='skip', showlegend=False
        ))

        # 3. Puntos Naranja + Variación %
        for i, row in data_bases.iterrows():
            color_texto = "#2F855A" if row['Variacion'] >= 0 else "#C53030"
            fig2.add_trace(go.Scatter(
                x=[row['Fecha_Eje']], y=[row['Variacion']], yaxis="y2",
                mode='markers+text',
                text=[f"<b>{fix_percent(row['Variacion'])}</b>"], 
                textposition="bottom center",
                textfont=dict(family="Poppins", size=11, color=color_texto),
                marker=dict(size=10, color="#fd941c", line=dict(width=1, color='white')),
                showlegend=False
            ))

        fig2.update_layout(
            plot_bgcolor='white', height=300, margin=dict(l=10, r=10, t=10, b=10), 
            barmode='overlay',
            # --- AJUSTE DE TAMAÑO EN EJES ---
            xaxis=dict(type='category', tickfont=dict(color="#000000", size=12), tickangle=0),
            yaxis=dict(showgrid=True, gridcolor='#edf2f7', tickfont=dict(color="#000000", size=12)),
            # -------------------------------
            yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False, range=[-0.5, 1.5]),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error Bases: {e}")

with col_inf_der:
    try:
        df_res_bs = pd.read_excel(ruta, sheet_name='Resev. Internacionales Bs', usecols="A:C")
        data_res_bs = df_res_bs.dropna(how='all').tail(6).copy()
        data_res_bs.columns = ['Fecha', 'Monto', 'Variacion']
        data_res_bs['Fecha_Eje'] = pd.to_datetime(data_res_bs['Fecha']).dt.strftime('%Y-%m-%d')

        st.markdown('<div class="contenedor-titulos"><p class="grafico-titulo">Reservas Internacionales Bs.</p> <p class="grafico-subtitulo">Últimas seis (6) Semanas</p></div>', unsafe_allow_html=True)
        fig3 = go.Figure()
        
        # 1. Barras con Montos HORIZONTALES
        fig3.add_trace(go.Bar(
            x=data_res_bs['Fecha_Eje'], y=data_res_bs['Monto'], 
            text=data_res_bs['Monto'].apply(format_mm), 
            textposition='inside', 
            insidetextanchor='middle',
            textangle=0, 
            textfont=dict(family="Poppins", size=11, color="white"),
            marker_color="#43be95", name="Monto"
        ))

        # 2. Línea de tendencia
        fig3.add_trace(go.Scatter(
            x=data_res_bs['Fecha_Eje'], y=data_res_bs['Variacion'], yaxis="y2",
            mode='lines', 
            line=dict(color="#E0F7FA", width=2, dash='dot'),
            hoverinfo='skip', showlegend=False
        ))

        # 3. Variación %
        for i, row in data_res_bs.iterrows():
            color_texto = "#2F855A" if row['Variacion'] >= 0 else "#C53030"
            fig3.add_trace(go.Scatter(
                x=[row['Fecha_Eje']], y=[row['Variacion']], yaxis="y2",
                mode='markers+text',
                text=[f"<b>{fix_percent(row['Variacion'])}</b>"], 
                textposition="bottom center",
                textfont=dict(family="Poppins", size=11, color=color_texto),
                marker=dict(size=10, color="#fd941c", line=dict(width=1, color='white')),
                showlegend=False
            ))

        fig3.update_layout(
            plot_bgcolor='white', height=300, margin=dict(l=10, r=10, t=10, b=10), 
            barmode='overlay',
            # --- AJUSTE DE TAMAÑO EN EJES ---
            xaxis=dict(type='category', tickfont=dict(color="#000000", size=12), tickangle=0),
            yaxis=dict(showgrid=True, gridcolor='#edf2f7', tickfont=dict(color="#000000", size=12)),
            # -------------------------------
            yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False, range=[-0.5, 1.5]),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    except Exception as e: st.error(f"Error Res Bs: {e}")

# ==========================================
# GRAFICO 4: RESERVAS INTERNACIONALES $ (CORREGIDO)
# ==========================================
try:
    df_usd = pd.read_excel(ruta, sheet_name='Resev. Internacionales $', usecols=[0, 3, 4])
    df_usd = df_usd.dropna(subset=[df_usd.columns[1]]) # Limpia filas sin montos
    df_usd.columns = ['Fecha', 'Monto', 'Variacion']
    df_usd['Fecha_DT'] = pd.to_datetime(df_usd['Fecha'])
    
    hoy = datetime.now()
    
    # --- NUEVA LÓGICA DE FILTRADO: MES ACTUAL Y MES ANTERIOR ---
    # Filtramos por año actual y meses (Mes actual y Mes actual - 1)
    data_usd = df_usd[
        (df_usd['Fecha_DT'].dt.year == hoy.year) & 
        (df_usd['Fecha_DT'].dt.month.isin([hoy.month, hoy.month - 1]))
    ].copy()
    
    data_usd = data_usd.sort_values('Fecha_DT').reset_index(drop=True)
    data_usd['Fecha_Txt'] = data_usd['Fecha_DT'].dt.strftime('%d-%m-%Y')

    # Cálculos para los botones (métricas)
    idx_max = data_usd['Monto'].idxmax()
    idx_min = data_usd['Monto'].idxmin()
    
    monto_alto = data_usd.loc[idx_max, 'Monto']
    var_alto = fix_percent(data_usd.loc[idx_max, 'Variacion'])
    
    monto_bajo = data_usd.loc[idx_min, 'Monto']
    var_bajo = fix_percent(data_usd.loc[idx_min, 'Variacion'])

    # Maquetación 80% Gráfico, 20% Métricas
    col_graf, col_met = st.columns([8, 2])

    with col_graf:
        st.markdown("""
            <div class="contenedor-titulos">
                <p class="grafico-titulo">Reservas Internacionales $</p>
                <p class="grafico-subtitulo">Evolución en divisas (USD) - Rango Reciente</p>
            </div>
        """, unsafe_allow_html=True)

        fig4 = go.Figure()

        # Línea de Montos y etiquetas Púrpuras
        fig4.add_trace(go.Scatter(
            x=data_usd['Fecha_Txt'], y=data_usd['Monto'], 
            mode='lines+markers+text', 
            text=data_usd['Monto'].apply(lambda x: f"<b>{x:,.1f}MM</b>"), 
            textposition="top center",
            line=dict(color='#C5CAE9', width=2), 
            marker=dict(size=8, color="#C5CAE9", line=dict(width=2, color='white')),
            textfont=dict(family="Poppins", size=11, color="#6A1B9A")
        ))

        # Línea de tendencia y Porcentajes
        fig4.add_trace(go.Scatter(
            x=data_usd['Fecha_Txt'], y=data_usd['Variacion'], yaxis="y2",
            mode='lines', line=dict(color='#4A5568', width=1.5, dash='dot'),
            hoverinfo='skip'
        ))

        for i, row in data_usd.iterrows():
            color_var = "#2F855A" if row['Variacion'] >= 0 else "#C53030"
            fig4.add_trace(go.Scatter(
                x=[row['Fecha_Txt']], y=[row['Variacion']], yaxis="y2",
                mode='markers+text',
                text=[f"<b>{fix_percent(row['Variacion'])}</b>"],
                textposition="bottom center",
                textfont=dict(family="Poppins", size=12, color=color_var),
                marker=dict(size=6, color="#A0AEC0"),
                showlegend=False
            ))

        fig4.update_layout(
            plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)', height=350, 
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(type='category', showgrid=False, tickfont=dict(color="#000000", size=12)),
            yaxis=dict(showgrid=True, gridcolor='#edf2f7', tickfont=dict(color="#000000", size=12)),
            yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False),
            showlegend=False, hovermode="x unified"
        )
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

    with col_met:
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        st.metric("Máximo Detectado", f"{monto_alto:,.1f} MM", delta=var_alto)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.metric("Mínimo Detectado", f"{monto_bajo:,.1f} MM", delta=var_bajo, delta_color="inverse")

except Exception as e: 
    st.error(f"Error en Reservas $: {e}")

# ==========================================
# FILA FINAL: GRAFICO 5 Y GRAFICO 6 (50/50)
# ==========================================
col_over_izq, col_over_der = st.columns([2, 2])

# GRAFICO 5: TASA OVERNIGHT DIARIA (FILTRADO SIN CEROS)
with col_over_izq:
    try:
        df_over = pd.read_excel(ruta, sheet_name='Tasa Overnight Diaria', usecols=[0, 7])
        df_over.columns = ['Fecha', 'Promedio']
        df_over['Fecha_DT'] = pd.to_datetime(df_over['Fecha'])
        
        hoy = datetime.now()
        # Filtramos por mes/año actual Y que el valor sea mayor a 0
        data_over = df_over[
            (df_over['Fecha_DT'].dt.month == hoy.month) & 
            (df_over['Fecha_DT'].dt.year == hoy.year) &
            (df_over['Promedio'] > 0)
        ].copy()
        
        data_over = data_over.sort_values('Fecha_DT')

        st.markdown("""
            <div class="contenedor-titulos">
                <p class="grafico-titulo" style="color: #607D8B;">Tasa Overnight Diaria</p>
                <p class="grafico-subtitulo">Promedio diario > 0% (Días hábiles) - Mes Actual</p>
            </div>
        """, unsafe_allow_html=True)
        
        fig5 = go.Figure()
        
        fig5.add_trace(go.Scatter(
            x=data_over['Fecha_DT'].dt.strftime('%d-%m'), 
            y=data_over['Promedio'], 
            mode='lines+markers+text',
            text=data_over['Promedio'].apply(lambda x: f"<b>{x:,.2f}</b>"),
            textposition="top center",
            line=dict(color='#607D8B', width=3), # Nuevo color Gris Azulado
            marker=dict(size=8, color='#fd941c', line=dict(width=1, color='white')),
            textfont=dict(family="Poppins", size=12, color="#607D8B")
        ))

        fig5.update_layout(
            plot_bgcolor='white', 
            paper_bgcolor='rgba(0,0,0,0)',
            height=350, 
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(
                type='category', 
                showgrid=False,
                tickfont=dict(family="Poppins", size=12, color="#000000")
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#edf2f7',
                tickfont=dict(family="Poppins", size=12, color="#000000")
            ),
            showlegend=False,
            hovermode="x unified"
        )
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
        
    except Exception as e:
        st.error(f"Error en Tasa Overnight: {e}")

# GRAFICO 6: TASA OVERNIGHT MENSUAL (CORREGIDO Y OPTIMIZADO)
with col_over_der:
    try:
        df_mensual = pd.read_excel(ruta, sheet_name='Tasa Overnight Mensual', usecols=[0, 1, 2, 3])
        
        # 1. LIMPIEZA DE DATOS: Eliminamos filas donde el 'Monto' sea NaN para evitar las columnas "nan"
        df_mensual = df_mensual.dropna(subset=[df_mensual.columns[1]])
        
        df_mensual.columns = ['Mes', 'Monto', 'Promedio', 'Ponderado']
        
        st.markdown("""
            <div class="contenedor-titulos">
                <p class="grafico-titulo" style="color: #2471A3;">Tasa Overnight Mensual</p>
                <p class="grafico-subtitulo">Monto, Promedio y Ponderado por Mes</p>
            </div>
        """, unsafe_allow_html=True)
        
        fig6 = go.Figure()

        # 1. Serie Montos (#566573)
        fig6.add_trace(go.Bar(
            x=df_mensual['Mes'].astype(str), y=df_mensual['Monto'],
            name='Monto', marker_color='#566573',
            text=df_mensual['Monto'].apply(format_mm), 
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(family="Poppins", size=11, color="white")
        ))

        # 2. Serie Promedio (#2471A3)
        fig6.add_trace(go.Bar(
            x=df_mensual['Mes'].astype(str), y=df_mensual['Promedio'],
            name='Promedio', marker_color='#2471A3',
            text=df_mensual['Promedio'].apply(lambda x: f"<b>{x:,.2f}</b>"), 
            textposition='outside',
            textfont=dict(family="Poppins", size=11, color="#2471A3")
        ))

        # 3. Serie Ponderado (#C4E0F2)
        fig6.add_trace(go.Bar(
            x=df_mensual['Mes'].astype(str), y=df_mensual['Ponderado'],
            name='Ponderado', marker_color='#C4E0F2',
            text=df_mensual['Ponderado'].apply(lambda x: f"<b>{x:,.2f}</b>"), 
            textposition='outside',
            textfont=dict(family="Poppins", size=11, color="#566573")
        ))

        fig6.update_layout(
            plot_bgcolor='white', 
            paper_bgcolor='rgba(0,0,0,0)',
            height=350, 
            margin=dict(l=10, r=10, t=50, b=10),
            
            # --- MEJORA DE ARMONÍA ---
            bargap=0.25,      # Espacio entre grupos de meses
            bargroupgap=0.1,  # Espacio mínimo entre las 3 barras del mes
            
            xaxis=dict(
                showgrid=False, 
                tickfont=dict(family="Poppins", size=12, color="#000000")
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#f0f2f6', # Gris más suave para armonía
                tickfont=dict(family="Poppins", size=12, color="#000000")
            ),
            barmode='group',
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.05, 
                xanchor="center", 
                x=0.5,
                font=dict(family="Poppins", size=11, color="#000000")
            )
        )

        # Cálculo dinámico del rango para que las etiquetas superiores no se corten
        max_val = df_mensual[['Monto', 'Promedio', 'Ponderado']].max().max()
        fig6.update_yaxes(range=[0, max_val * 1.25])
        
        st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})

    except Exception as e:
        st.error(f"Error en Tasa Mensual: {e}")