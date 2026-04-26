import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Monitor Financiero", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=100000, key="datarefresh")

# CSS: Mantenemos tu estilo y agregamos el del encabezado y ocultar menús
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .block-container { padding: 1rem !important; background-color: #f8f9fc; }
    
    /* ESTILO DEL ENCABEZADO TRIPLE CORREGIDO */
    .main-title-container { 
        text-align: center; 
        margin-top: 10px;
        margin-bottom: 30px; 
        font-family: 'Poppins', sans-serif; 
    }
    
    .title-line1 { 
        color: #2b5dda; 
        font-size: 30px !important; /* Tamaño fijo grande para el Título */
        font-weight: 600; 
        line-height: 1.1;
        margin: 0; 
    }
    
    .title-line2 { 
        color: #333333; 
        font-size: 17px !important; /* Tamaño fijo para el Subtítulo */
        font-weight: 300; 
        margin-top: 5px; 
    }
    
    /* Opcional: Para que sea responsivo en móviles pero mantenga buen tamaño */
    @media (max-width: 768px) {
        .title-line1 { font-size: 6vw !important; }
        .title-line2 { font-size: 2vw !important; }
    }

    .grafico-titulo { color: #2b5dda; font-family: 'Poppins'; font-size: 1.2vw; font-weight: 400; margin-bottom: 5px; text-align: center;}
    .chart-box { border: 1px solid #dee2e6; border-radius: 15px; background-color: white; padding: 15px; margin-bottom: 20px; }
    </style>
    
    <div class="main-title-container">
        <p class="title-line1">BANFANB, Banco Universal</p>
        <p class="title-line2">Indicadores Nacionales Macroeconómicos Semanales (BCV)</p>
    </div>
    """, unsafe_allow_html=True)

ruta = "Data_Situacional_Ejemplo.xlsx" #Para la Web
# ruta = r"C:\Monitor_test\Data_Situacional_Ejemplo.xlsx" #local

# CARGA DE DATOS MEJORADA
def load_data(sheet):
    try:
        df = pd.read_excel(ruta, sheet_name=sheet)
        return df.dropna(how='all').reset_index(drop=True)
    except:
        return pd.DataFrame()

# --- FILA 1: GRÁFICOS GRANDES ---
c1, c2 = st.columns(2)

with c1:
    # 1. LIMPIEZA DE DATOS
    df_raw = load_data('Liquidez Monetaria')
    df = df_raw.dropna(subset=[df_raw.columns[6]]).tail(6)
    
    if not df.empty:
        st.markdown('<div style="margin-bottom: 2px;">', unsafe_allow_html=True) 
        
        head_col1, head_col2, head_col3 = st.columns([1.8, 1, 1])
        
        with head_col1:
            st.markdown('<p class="grafico-titulo">Liquidez Monetaria en Bs.</p>', unsafe_allow_html=True)
        
        ultimo_valor = df.iloc[-1, 6]
        var_ultima = df.iloc[-1, 7] if df.shape[1] > 7 else 0
        promedio_valor = df.iloc[:, 6].mean()

        with head_col2:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                    <p style="margin:0; font-size: 0.8vw; color: #666;">Actual</p>
                    <p style="margin:0; font-size: 1.1vw; font-weight: bold; color: #333;">Bs. {ultimo_valor:,.0f}</p>
                    <p style="margin:0; font-size: 0.8vw; color: #28a745;">↑ {var_ultima*100:.2f}%</p>
                </div>
            """, unsafe_allow_html=True)

        with head_col3:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                    <p style="margin:0; font-size: 0.8vw; color: #666;">Promedio</p>
                    <p style="margin:0; font-size: 1.1vw; font-weight: bold; color: #333;">Bs. {promedio_valor:,.0f}</p>
                    <p style="margin:0; font-size: 0.8vw; color: transparent;">-</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y') 
        x_data = df['Fecha_Exacta'] 
        y_data = df.iloc[:, 6] 
        y_var = df.iloc[:, 7] if df.shape[1] > 7 else y_data.pct_change()

        fig = go.Figure()
        
        # Ajusta el 'size' en textfont para las etiquetas de los puntos
        fig.add_trace(go.Scatter(
            x=x_data, y=y_data, mode='lines+markers+text', name='Liquidez',
            text=[f"{v/1e6:,.0f}MM" if v >= 1e6 else f"{v:,.0f}" for v in y_data],
            textposition="top center", 
            textfont=dict(color='#2b5dda', size=16), # <--- AJUSTA ESTE VALOR
            line=dict(color='#2b5dda', width=2), marker=dict(color="#07cdff", size=7),
            cliponaxis=False
        ))
        
        fig.add_trace(go.Scatter(
            x=x_data, y=y_var, mode='lines+markers+text', name='Variación %',
            text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
            textposition="bottom center", 
            textfont=dict(color='black', size=16), # <--- AJUSTA ESTE VALOR
            line=dict(color='#6A1B9A', width=2, dash='dot'), marker=dict(color='#6A1B9A', size=7),
            yaxis='y2',
            cliponaxis=False
        ))

        fig.update_layout(
            plot_bgcolor='white', height=320, showlegend=False,
            autosize=True,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(
                showgrid=True, gridcolor='#eee', 
                tickfont=dict(color='black', size=16), # <--- AJUSTA ESTE VALOR
                linecolor='gray', linewidth=2, zeroline=False
            ),
            xaxis=dict(
                type='category', tickmode='array', tickvals=x_data, 
                showgrid=False, 
                tickfont=dict(color='black', size=16), # <--- AJUSTA ESTE VALOR
                linecolor='gray', linewidth=2
            ),
            yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False, zeroline=False)
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    df_raw = load_data('Resev. Internacionales $')
    df = df_raw.dropna(subset=[df_raw.columns[3]]).tail(6)
    
    if not df.empty:
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        head_col1, head_col2, head_col3 = st.columns([1.8, 1, 1])
        
        with head_col1:
            st.markdown('<p class="grafico-titulo">Reservas Internacionales en Dolares $</p>', unsafe_allow_html=True)
        
        # --- CORRECCIÓN DEL ERROR DE ÍNDICE ---
        idx_max = df.iloc[:, 3].idxmax()
        idx_min = df.iloc[:, 3].idxmin()
        
        max_val = df.loc[idx_max, df.columns[3]]
        min_val = df.loc[idx_min, df.columns[3]]
        
        # Buscamos la variación en la columna 4 usando el índice real detectado
        var_max = df.loc[idx_max, df.columns[4]] if df.shape[1] > 4 else 0
        var_min = df.loc[idx_min, df.columns[4]] if df.shape[1] > 4 else 0
        # ---------------------------------------

        with head_col2:
            st.markdown(f"""
                <div style="background: white; border: 2px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                    <p style="margin:0; font-size: 0.9vw; color: #666;">Máximo Detectado</p>
                    <p style="margin:0; font-size: 0.9vw; font-weight: bold; color: #333;">{max_val:,.1f} MM</p>
                    <p style="margin:0; font-size: 0.9vw; color: #dc3545;">{"↓" if var_max < 0 else "↑"} {abs(var_max*100):.2f}%</p>
                </div>
            """, unsafe_allow_html=True)

        with head_col3:
            st.markdown(f"""
                <div style="background: white; border: 2px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                    <p style="margin:0; font-size: 0.9vw; color: #666;">Mínimo Detectado</p>
                    <p style="margin:0; font-size: 0.9vw; font-weight: bold; color: #333;">{min_val:,.1f} MM</p>
                    <p style="margin:0; font-size: 0.9vw; color: #28a745;">{"↓" if var_min < 0 else "↑"} {abs(var_min*100):.2f}%</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        x_data = df['Fecha_Exacta']
        y_data = df.iloc[:, 3]
        y_var = df.iloc[:, 4] if df.shape[1] > 4 else y_data.pct_change()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_data, y=y_data, fill='tozeroy', mode='lines+markers+text',
            text=[f"{v:,.1f}MM" for v in y_data], 
            textposition="top center", textfont=dict(color='#2b5dda', size=16),
            fillcolor='rgba(0,0,0,0)', line=dict(color='#2b5dda', width=2), marker=dict(color='#07cdff', size=10),
            cliponaxis=False
        ))
        fig.add_trace(go.Scatter(
            x=x_data, y=y_var, mode='lines+markers+text',
            text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
            textposition="bottom center", textfont=dict(color='black', size=16),
            line=dict(color='#6A1B9A', width=2, dash='dot'), marker=dict(color='#6A1B9A', size=10),
            yaxis='y2',
            cliponaxis=False
        ))

        fig.update_layout(
            plot_bgcolor='white', height=320, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(color='black', size=16), linecolor='gray', linewidth=1, zeroline=False),
            xaxis=dict(type='category', showgrid=False, tickfont=dict(color='black', size=16), linecolor='gray', linewidth=1),
            yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False, zeroline=False)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# --- FILA 2: CUADRÍCULA DE 4 ---
c3, c4, c5, c6 = st.columns(4)

with c3:
    st.markdown('<p class="grafico-titulo" style="font-size:1vw; text-align:center;">Base Monetaria en Bs. </p>', unsafe_allow_html=True)
    df = load_data('Bases Monetarias').tail(6)
    
    if not df.empty:
        # VALIDACIÓN OBLIGATORIA
        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        x_data = df['Fecha_Exacta']
        
        y_data = df.iloc[:, 1]
        y_var = df.iloc[:, 2] if df.shape[1] > 2 else y_data.pct_change()

        fig = go.Figure()

        # 1. Trazo Principal: Barras (Montos en la MITAD en BLANCO)
        fig.add_trace(go.Bar(
            x=x_data, 
            y=y_data, 
            name='Base Monetaria en Bs.',
            marker_color="#DB7337",
            # Texto en blanco, delgado (sin negrita), tamaño 10
            text=[f"{v/1e6:,.0f}MM" if v >= 1e6 else f"{v:,.0f}" for v in y_data],
            textposition="inside",
            insidetextanchor="middle", # Lo coloca justo en la mitad de la barra
            textfont=dict(color='white', size=16),
        ))

        # 2. Línea de Tendencia: Variación % (Cyan y Gris Dash)
        #fig.add_trace(go.Scatter(
            #x=x_data, 
            #y=y_var, 
            #mode='lines+markers+text',
            #name='Variación %',
            # Montos en CYAN resaltante
            #text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
            #textposition="bottom center", 
            #textfont=dict(color="#DB7337", size=12), # Cyan eléctrico para resaltar
            #line=dict(color="#DB7337", width=1, dash='dot'), # Gris delgado y entrecortado
            #marker=dict(color="#DB7337", size=10),
            #yaxis='y2'
        #))

        # 3. Configuración de Ejes Negro Intenso
        fig.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=13),
                linecolor='gray',
                linewidth=2,
                zeroline=False
            ),
            xaxis=dict(
                type='category',
                showgrid=False, 
                tickfont=dict(color='black', size=13),
                linecolor='gray',
                linewidth=2
            ),
            yaxis2=dict(
                overlaying='y',
                side='right',
                showgrid=False,
                showticklabels=False,
                zeroline=False
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
with c4:
    st.markdown('<p class="grafico-titulo" style="font-size:1vw; text-align:center;">Reservas Internacionales en Bs.</p>', unsafe_allow_html=True)
    # Cargamos la hoja de Liquidez pero enfocada en Reservas Bs.
    df = load_data('Liquidez Monetaria').tail(6)
    
    if not df.empty:
        # VALIDACIÓN OBLIGATORIA: Fechas exactas del Excel
        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        x_data = df['Fecha_Exacta']
        
        # Asumimos que los montos de Reservas Bs. están en la columna 6
        y_data = df.iloc[:, 6]
        # Variación (Columna 7 o cálculo)
        y_var = df.iloc[:, 7] if df.shape[1] > 7 else y_data.pct_change()

        fig = go.Figure()

        # 1. Trazo Principal: Barras Verdes (Montos en la MITAD en BLANCO)
        fig.add_trace(go.Bar(
            x=x_data, 
            y=y_data, 
            name='Reservas Bs.',
            marker_color="#42698d", # Tu verde original
            # Texto blanco, delgado, tamaño 10
            text=[f"{v/1e6:,.0f}MM" if v >= 1e6 else f"{v:,.0f}" for v in y_data],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color='white', size=14),
        ))

        # 2. Línea de Tendencia: Variación % (Cyan y Gris Dash)
        #fig.add_trace(go.Scatter(
        #    x=x_data, 
        #    y=y_var, 
        #    mode='lines+markers+text',
        #    name='Variación %',
        #    # Montos en CYAN resaltante debajo del punto
        #    text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
        #    textposition="bottom center", 
        #    textfont=dict(color='#fd941c', size=12),
        #    line=dict(color='#00FFFF', width=1, dash='dot'), # Gris delgado dash
        #    marker=dict(color='#fd941c', size=8),
        #    yaxis='y2'
        #))

        # 3. Configuración de Ejes Negro Intenso
        fig.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=13),
                linecolor='gray', # Gris intenso
                linewidth=2,
                zeroline=False
            ),
            xaxis=dict(
                type='category',
                showgrid=False, 
                tickfont=dict(color='black', size=13),
                linecolor='gray', # Gris intenso
                linewidth=2
            ),
            yaxis2=dict(
                overlaying='y',
                side='right',
                showgrid=False,
                showticklabels=False,
                zeroline=False
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c5:
    st.markdown('<p class="grafico-titulo" style="font-size:1vw; text-align:center;">Tasa Overnight (Promedio Diario)</p>', unsafe_allow_html=True)
    # Cargamos los últimos 10 registros
    df = load_data('Tasa Overnight Diaria').tail(10)
    
    if not df.empty:
        # VALIDACIÓN OBLIGATORIA: Columna A para el eje X (Fechas exactas)
        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        x_data = df['Fecha_Exacta']
        
        # OBLIGATORIO: Columna H para el eje Y (Valores de la tasa)
        # Usamos .iloc[:, 7] ya que la columna H es la octava columna (índice 7)
        y_data = df.iloc[:, 7]

        fig = go.Figure()

        # 1. Trazo Principal: Línea Azul con Valores idénticos a Columna H
        fig.add_trace(go.Scatter(
            x=x_data, 
            y=y_data, 
            mode='lines+markers+text',
            name='Tasa Overnight',
            # Se usa el valor de la columna H tal cual viene en el Excel
            text=[f"{v}%" for v in y_data],
            textposition="top center",
            textfont=dict(color='black', size=10),
            line=dict(color='#2b5dda', width=2), 
            marker=dict(color='#2b5dda', size=6)
        ))

        # 2. Configuración de Ejes NEGRO INTENSO
        fig.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=13),
                linecolor='gray',
                linewidth=2,
                zeroline=False,
                # Margen dinámico para que las etiquetas de la Columna H no choquen
                range=[y_data.min() * 0.7, y_data.max() * 1.3]
            ),
            xaxis=dict(
                type='category', 
                showgrid=False, 
                tickfont=dict(color='black', size=13),
                linecolor='gray',
                linewidth=2
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    # TÍTULO
    st.markdown('<p class="grafico-titulo" style="font-size:1vw; text-align:center;">Tasa Overnight (Promedio Mensual)</p>', unsafe_allow_html=True)
    
    # 1. CARGA DE DATOS
    df_raw = load_data('Tasa Overnight Mensual')
    
    if df_raw is not None and not df_raw.empty:
        # 2. LIMPIEZA Y FILTRADO
        df_c6 = df_raw.dropna(subset=[df_raw.columns[3]]).tail(3).copy()
        
        x_data_c6 = df_c6.iloc[:, 0]
        y_data_c6 = df_c6.iloc[:, 3] # Si aquí hay 317.51, se usará 317.51

        fig_c6 = go.Figure()

        fig_c6.add_trace(go.Scatter(
            x=x_data_c6, 
            y=y_data_c6, 
            mode='lines+markers+text',
            name='Promedio Ponderado',
            # CORRECCIÓN EN EL GRÁFICO: Usamos f-string para poner el % como texto simple
            text=[f"{v:,.2f}%" for v in y_data_c6],
            textposition="top center",
            cliponaxis=False,
            textfont=dict(color='black', size=14),
            line=dict(color='#2b5dda', width=2), 
            marker=dict(color='#2b5dda', size=7),
        ))

        fig_c6.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=35, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=10),
                linecolor='gray',
                linewidth=2,
                zeroline=False,
                # CORRECCIÓN EN EL EJE Y: 
                # tickformat=".2f" muestra el número tal cual. 
                # ticksuffix="%" agrega el símbolo sin hacer cálculos matemáticos.
                tickformat=".2f", 
                ticksuffix="%", 
                range=[y_data_c6.min() * 0.8, y_data_c6.max() * 1.2]
            ),
            xaxis=dict(
                type='category', 
                showgrid=False, 
                tickfont=dict(color='black', size=14),
                linecolor='gray',
                linewidth=2
            )
        )
        
        # 3. MOSTRAR GRÁFICO
        st.plotly_chart(fig_c6, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("No hay datos disponibles.")