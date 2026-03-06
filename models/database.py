import pandas as pd
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine, text

class DatabaseManager:

   def __init__(self):
    try:
        DATABASE_URL = st.secrets["DATABASE_URL"]
        self.engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={'connect_timeout': 10}
        )
        # Probamos conexión inmediata
        with self.engine.connect() as conn:
            pass
        self._create_tables()
    except Exception as e:
        st.error(f"Error de conexión real: {str(e)}") # Esto saltará el redactado de Streamlit
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
                    fecha_carga TIMESTAMP,
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

            conn.commit()


    def registrar_consolidacion(self, resultado, margen_aplicado, total_factura_movistar):

        with self.engine.begin() as conn:

            af = resultado["auditoria_fiscal"]

            result = conn.execute(text("""
                INSERT INTO facturas (
                    periodo_mes,
                    periodo_anio,
                    fecha_carga,
                    total_neto_movistar,
                    total_iva,
                    total_final_pdf,
                    markup_porcentaje
                )
                VALUES (
                    :periodo_mes,
                    :periodo_anio,
                    :fecha_carga,
                    :total_neto_movistar,
                    :total_iva,
                    :total_final_pdf,
                    :markup_porcentaje
                )
                RETURNING id
            """), {
                "periodo_mes": resultado['periodo_mes'],
                "periodo_anio": resultado['periodo_anio'],
                "fecha_carga": resultado['fecha_manual'],
                "total_neto_movistar": resultado['total_final'],
                "total_iva": af['iva_pdf'],
                "total_final_pdf": total_factura_movistar,
                "markup_porcentaje": margen_aplicado
            })

            factura_id = result.scalar()

            for d in resultado['datos']:

                precio_markup = round(d['total_neto'] * (1 + margen_aplicado / 100), 2)

                conn.execute(text("""
                    INSERT INTO consumos_detalle (
                        factura_id,
                        linea,
                        nombre,
                        grupo,
                        categoria,
                        costo_fijo,
                        costo_variable,
                        costo_juegos,
                        neto_movistar,
                        precio_con_markup
                    )
                    VALUES (
                        :factura_id,
                        :linea,
                        :nombre,
                        :grupo,
                        :categoria,
                        :costo_fijo,
                        :costo_variable,
                        :costo_juegos,
                        :neto_movistar,
                        :precio_con_markup
                    )
                """), {
                    "factura_id": factura_id,
                    "linea": d['linea'],
                    "nombre": d['nombre'],
                    "grupo": d['grupo'],
                    "categoria": d['categoria'],
                    "costo_fijo": d['total_fijo'],
                    "costo_variable": d['total_variable'],
                    "costo_juegos": d['juegos_extra'],
                    "neto_movistar": d['total_neto'],
                    "precio_con_markup": precio_markup
                })

            return factura_id


    def get_datos_consulta(self, periodo_str=None, grupo="TODOS"):

        query = """
            SELECT 
                f.periodo_mes || '/' || f.periodo_anio as periodo,
                f.total_final_pdf,
                f.markup_porcentaje,
                c.linea,
                c.nombre,
                c.grupo,
                c.categoria,
                c.costo_fijo,
                c.costo_variable,
                c.costo_juegos,
                c.neto_movistar,
                c.precio_con_markup
            FROM consumos_detalle c
            JOIN facturas f ON c.factura_id = f.id
            WHERE 1=1
        """

        params = {}

        if periodo_str and periodo_str != "TODOS":
            mes, anio = periodo_str.split('/')
            query += " AND f.periodo_mes = :mes AND f.periodo_anio = :anio"
            params["mes"] = mes
            params["anio"] = anio

        if grupo and grupo != "TODOS":
            query += " AND c.grupo = :grupo"
            params["grupo"] = grupo

        with self._get_connection() as conn:
            return pd.read_sql(text(query), conn, params=params)


    def get_grupos_unicos(self):

        query = """
            SELECT DISTINCT grupo
            FROM consumos_detalle
            WHERE grupo IS NOT NULL
            ORDER BY grupo
        """

        with self._get_connection() as conn:
            df = pd.read_sql(text(query), conn)

        return df['grupo'].tolist()


    def get_periodos_disponibles(self):

        query = """
            SELECT DISTINCT (periodo_mes || '/' || periodo_anio) as periodo
            FROM facturas
            ORDER BY periodo_anio DESC, periodo_mes DESC
        """

        with self._get_connection() as conn:
            df = pd.read_sql(text(query), conn)

        return df['periodo'].tolist()


    def get_consumos_por_factura(self, factura_id):

        query = """
            SELECT linea, nombre, grupo, costo_fijo, costo_variable,
                   costo_juegos, neto_movistar, precio_con_markup
            FROM consumos_detalle
            WHERE factura_id = :factura_id
        """

        with self._get_connection() as conn:
            return pd.read_sql(text(query), conn, params={"factura_id": factura_id})