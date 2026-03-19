import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

class DatabaseManager:
    def __init__(self):
        try:
            url = st.secrets["DATABASE_URL"].strip()
            # Optimizamos el pool para que las conexiones siempre estén "calientes"
            self.engine = create_engine(
                url,
                pool_size=10, 
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=1800,
                connect_args={'connect_timeout': 10}
            )
            self._create_tables()
        except Exception as e:
            st.error(f"🚨 Error de conexión: {str(e)}")
            raise e

    def _get_connection(self):
        return self.engine.connect()

    def _create_tables(self):
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS facturas (
                    id SERIAL PRIMARY KEY,
                    periodo_mes TEXT,
                    periodo_anio TEXT,
                    fecha_carga TEXT,
                    total_neto_movistar REAL,
                    total_iva REAL,
                    total_final_pdf REAL,
                    markup_porcentaje REAL
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS consumos_detalle (
                    id SERIAL PRIMARY KEY,
                    factura_id INTEGER REFERENCES facturas(id),
                    linea TEXT,
                    nombre TEXT,
                    grupo TEXT,
                    categoria TEXT,
                    costo_fijo REAL,
                    costo_variable REAL,
                    costo_juegos REAL,
                    neto_movistar REAL,
                    precio_con_markup REAL
                )
            """))

    def registrar_consolidacion(self, resultado, margen_aplicado, total_factura_movistar):
        try:
            with self.engine.begin() as conn:
                af = resultado["auditoria_fiscal"]
                query_f = text("""
                    INSERT INTO facturas (periodo_mes, periodo_anio, fecha_carga, total_neto_movistar, total_iva, total_final_pdf, markup_porcentaje)
                    VALUES (:mes, :anio, :fecha, :neto, :iva, :total, :markup)
                    RETURNING id
                """)
                
                params_f = {
                    "mes": str(resultado['periodo_mes']), "anio": str(resultado['periodo_anio']),
                    "fecha": str(resultado['fecha_manual']), "neto": float(resultado['total_final']),
                    "iva": float(af['iva_pdf']), "total": float(total_factura_movistar), "markup": float(margen_aplicado)
                }
                
                result = conn.execute(query_f, params_f)
                factura_id = result.scalar()

                for d in resultado['datos']:
                    precio_markup = round(float(d['total_neto']) * (1 + float(margen_aplicado) / 100), 2)
                    query_d = text("""
                        INSERT INTO consumos_detalle (factura_id, linea, nombre, grupo, categoria, costo_fijo, costo_variable, costo_juegos, neto_movistar, precio_con_markup)
                        VALUES (:f_id, :linea, :nom, :gru, :cat, :fijo, :var, :jue, :neto, :markup)
                    """)
                    
                    conn.execute(query_d, {
                        "f_id": int(factura_id), "linea": str(d['linea']), "nom": str(d['nombre']), "gru": str(d['grupo']),
                        "cat": str(d['categoria']), "fijo": float(d['total_fijo']), "var": float(d['total_variable']),
                        "jue": float(d['juegos_extra']), "neto": float(d['total_neto']), "markup": float(precio_markup)
                    })
                
                # IMPORTANTE: Limpiamos la caché para que los nuevos datos aparezcan en Consultas
                st.cache_data.clear()
                return factura_id
        except Exception as e:
            st.error(f"❌ Error al guardar en DB: {str(e)}")
            raise e

    # --- CONSULTAS CON CACHÉ (Acelera la navegación) ---

    @st.cache_data(ttl=600)
    def get_periodos_disponibles(_self):
    # Usamos una subconsulta para ordenar sin romper el DISTINCT
        query = """
            SELECT DISTINCT periodo_mes || '/' || periodo_anio as periodo
            FROM facturas
            ORDER BY periodo DESC
        """
        # Si lo anterior sigue dando problemas por el orden de texto (12/2025 vs 02/2026), 
        # la forma infalible es esta:
        query_correcta = """
            SELECT periodo_mes || '/' || periodo_anio as periodo
            FROM facturas
            GROUP BY periodo_mes, periodo_anio
            ORDER BY CAST(periodo_anio AS INTEGER) DESC, CAST(periodo_mes AS INTEGER) DESC
        """
        with _self._get_connection() as conn:
            df = pd.read_sql(text(query_correcta), conn)
        return df['periodo'].tolist()
        
    @st.cache_data(ttl=300)
    def get_datos_consulta(_self, periodo_str=None, grupo="TODOS"):
        query = """
            SELECT f.periodo_mes || '/' || f.periodo_anio as periodo, f.total_final_pdf, f.markup_porcentaje,
                   c.linea, c.nombre, c.grupo, c.categoria, c.costo_fijo, c.costo_variable, c.costo_juegos, c.neto_movistar, c.precio_con_markup
            FROM consumos_detalle c JOIN facturas f ON c.factura_id = f.id WHERE 1=1
        """
        params = {}
        if periodo_str and periodo_str != "TODOS":
            mes, anio = periodo_str.split('/')
            query += " AND f.periodo_mes = :mes AND f.periodo_anio = :anio"
            params["mes"], params["anio"] = mes, anio
            
        with _self._get_connection() as conn:
            return pd.read_sql(text(query), conn, params=params)

    @st.cache_data(ttl=300)
    def get_consumos_por_factura(_self, factura_id):
        query = "SELECT * FROM consumos_detalle WHERE factura_id = :id"
        with _self._get_connection() as conn:
            return pd.read_sql(text(query), conn, params={"id": factura_id})
