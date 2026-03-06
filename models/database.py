import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

class DatabaseManager:
    def __init__(self):
        try:
            # Leemos el secret que configuraste recién
            url = st.secrets["DATABASE_URL"].strip()
            self.engine = create_engine(
                url,
                pool_pre_ping=True,      # Verifica si la conexión está viva
                pool_recycle=1800,       # Reinicia conexiones viejas
                connect_args={'connect_timeout': 10}
            )
            # Intentamos crear las tablas al iniciar
            self._create_tables()
        except Exception as e:
            st.error(f"🚨 Error de conexión a la base de datos: {str(e)}")
            raise e

    def _get_connection(self):
        return self.engine.connect()

    def _create_tables(self):
        """Crea la estructura inicial en Neon si no existe"""
        with self.engine.begin() as conn:
            # Tabla de Facturas Generales
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
            # Tabla de Detalle por Línea
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
        """Guarda la factura y sus detalles en una sola transacción"""
        with self.engine.begin() as conn:
            af = resultado["auditoria_fiscal"]
            
            # 1. Insertar Factura y obtener el ID generado (RETURNING id)
            query_f = text("""
                INSERT INTO facturas (periodo_mes, periodo_anio, fecha_carga, total_neto_movistar, total_iva, total_final_pdf, markup_porcentaje)
                VALUES (:mes, :anio, :fecha, :neto, :iva, :total, :markup)
                RETURNING id
            """)
            
            result = conn.execute(query_f, {
                "mes": resultado['periodo_mes'], 
                "anio": resultado['periodo_anio'],
                "fecha": resultado['fecha_manual'], 
                "neto": resultado['total_final'],
                "iva": af['iva_pdf'], 
                "total": total_factura_movistar, 
                "markup": margen_aplicado
            })
            
            factura_id = result.scalar()

            # 2. Insertar Detalle de cada línea
            for d in resultado['datos']:
                precio_markup = round(d['total_neto'] * (1 + margen_aplicado / 100), 2)
                conn.execute(text("""
                    INSERT INTO consumos_detalle (factura_id, linea, nombre, grupo, categoria, costo_fijo, costo_variable, costo_juegos, neto_movistar, precio_con_markup)
                    VALUES (:f_id, :linea, :nom, :gru, :cat, :fijo, :var, :jue, :neto, :markup)
                """), {
                    "f_id": factura_id, "linea": d['linea'], "nom": d['nombre'], "gru": d['grupo'],
                    "cat": d['categoria'], "fijo": d['total_fijo'], "var": d['total_variable'],
                    "jue": d['juegos_extra'], "neto": d['total_neto'], "markup": precio_markup
                })
            
            return factura_id

    def get_periodos_disponibles(self):
        """Obtiene la lista de periodos para el selector de consultas"""
        query = "SELECT DISTINCT (periodo_mes || '/' || periodo_anio) as periodo FROM facturas ORDER BY periodo DESC"
        with self._get_connection() as conn:
            df = pd.read_sql(text(query), conn)
        return df['periodo'].tolist()

    def get_datos_consulta(self, periodo_str=None, grupo="TODOS"):
        """Trae los datos cruzados para la tabla histórica"""
        query = """
            SELECT f.periodo_mes || '/' || f.periodo_anio as periodo, f.total_final_pdf, f.markup_porcentaje,
                   c.linea, c.nombre, c.grupo, c.categoria, c.costo_fijo, c.costo_variable, c.costo_juegos, c.neto_movistar, c.precio_con_markup
            FROM consumos_detalle c 
            JOIN facturas f ON c.factura_id = f.id 
            WHERE 1=1
        """
        params = {}
        if periodo_str and periodo_str != "TODOS":
            mes, anio = periodo_str.split('/')
            query += " AND f.periodo_mes = :mes AND f.periodo_anio = :anio"
            params["mes"], params["anio"] = mes, anio
            
        with self._get_connection() as conn:
            return pd.read_sql(text(query), conn, params=params)

    def get_consumos_por_factura(self, factura_id):
        """Usado para generar los PDFs de abonos"""
        query = "SELECT * FROM consumos_detalle WHERE factura_id = :id"
        with self._get_connection() as conn:
            return pd.read_sql(text(query), conn, params={"id": factura_id})
