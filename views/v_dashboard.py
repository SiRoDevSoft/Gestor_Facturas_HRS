import streamlit as st
import pandas as pd
import plotly.express as px
from models.database import DatabaseManager

def render_dashboard():
    db = DatabaseManager()
    
    st.header("Dashboard de Control: Grupo EMPRESA")
    st.markdown("---")

    # 1. Obtención de periodos
    periodos = db.get_periodos_disponibles()
    if not periodos or len(periodos) < 1:
        st.warning("No se encontraron datos suficientes para generar el análisis.")
        return

    # 2. Filtros de visualización
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        mes_sel = st.selectbox("Mes de Análisis", periodos, index=0)
    
    # 3. Carga de datos históricos (Solo lectura)
    # Traemos todos los datos para poder comparar con cualquier mes anterior
    df_raw = db.get_datos_consulta(periodo_str="TODOS")
    
    # Filtrar estrictamente por el grupo EMPRESA
    df_empresa = df_raw[df_raw['grupo'] == 'EMPRESA'].copy()
    
    if df_empresa.empty:
        st.info("No hay registros vinculados al grupo EMPRESA en el histórico.")
        return

    # 4. Lógica de Comparación (Mes Actual vs Mes Anterior)
    # Identificamos el índice del mes seleccionado para hallar el anterior en la lista
    idx_actual = periodos.index(mes_sel)
    df_actual = df_empresa[df_empresa['periodo'] == mes_sel]
    
    # Intentamos obtener el mes anterior cronológico de la lista de periodos
    tiene_comparativa = False
    if idx_actual + 1 < len(periodos):
        mes_ant = periodos[idx_actual + 1]
        df_anterior = df_empresa[df_empresa['periodo'] == mes_ant]
        tiene_comparativa = True
    
    # 5. KPIs Principales
    gasto_total = df_actual['neto_movistar'].sum()
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Gasto Total (Neto)", f"$ {gasto_total:,.2f}")
    
    if tiene_comparativa:
        gasto_ant = df_anterior['neto_movistar'].sum()
        delta_total = gasto_total - gasto_ant
        delta_porc = (delta_total / gasto_ant) * 100 if gasto_ant > 0 else 0
        with m2:
            st.metric("Variación vs Mes Anterior", f"$ {delta_total:,.2f}", f"{delta_porc:.1f}%", delta_color="inverse")
    
    # 6. Gráfico de Ranking de Consumo (Color #0092c1)
    st.subheader("Distribución de Gasto por Línea")
    
    # Top 15 consumidores del mes
    df_ranking = df_actual.sort_values('neto_movistar', ascending=False).head(15)
    
    fig_ranking = px.bar(
        df_ranking,
        x='neto_movistar',
        y='nombre',
        orientation='h',
        labels={'neto_movistar': 'Monto Neto ($)', 'nombre': 'Línea / Usuario'},
        color_discrete_sequence=['#0092c1'],
        template="plotly_white"
    )
    fig_ranking.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_ranking, use_container_width=True)

    # 7. Tabla Detallada con Referencia
    st.subheader("Detalle Comparativo de Líneas")
    
    if tiene_comparativa:
        # Cruzamos datos actuales con anteriores para ver desviación por línea
        df_comp = pd.merge(
            df_actual[['linea', 'nombre', 'neto_movistar']],
            df_anterior[['linea', 'neto_movistar']],
            on='linea',
            how='left',
            suffixes=('_act', '_ant')
        ).fillna(0)
        
        df_comp['Desviación $'] = df_comp['neto_movistar_act'] - df_comp['neto_movistar_ant']
        df_comp = df_comp.rename(columns={
            'nombre': 'Usuario',
            'neto_movistar_act': 'Mes Actual ($)',
            'neto_movistar_ant': 'Mes Anterior ($)'
        })
        
        # Ordenar por los que más aumentaron su consumo
        st.dataframe(
            df_comp.sort_values('Desviación $', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(
            df_actual[['linea', 'nombre', 'categoria', 'neto_movistar']].sort_values('neto_movistar', ascending=False),
            use_container_width=True,
            hide_index=True
        )