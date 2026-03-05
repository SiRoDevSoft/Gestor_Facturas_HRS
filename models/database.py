# import sqlite3
# import pandas as pd
# from datetime import datetime

# class DatabaseManager:
#     def __init__(self, db_path='hierrosan_v2.db'):
#         self.db_path = db_path
#         self._create_tables()

#     def _get_connection(self):
#         return sqlite3.connect(self.db_path)

#     def _create_tables(self):
#         with self._get_connection() as conn:
#             cursor = conn.cursor()
#             # Tabla de Facturas: Información del PDF y totales auditados
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS facturas (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     periodo_mes TEXT,
#                     periodo_anio TEXT,
#                     fecha_carga TIMESTAMP,
#                     total_neto_movistar REAL,
#                     total_iva REAL,
#                     total_final_pdf REAL,
#                     markup_porcentaje REAL
#                 )
#             ''')
#             # Tabla de Consumos: El detalle línea por línea (Atómico)
#             cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS consumos_detalle (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     factura_id INTEGER,
#                     linea TEXT,
#                     nombre TEXT,
#                     grupo TEXT,
#                     costo_fijo REAL,
#                     costo_variable REAL,
#                     costo_juegos REAL,
#                     neto_movistar REAL,
#                     precio_con_markup REAL,
#                     FOREIGN KEY (factura_id) REFERENCES facturas (id)
#                 )
#             ''')
#             conn.commit()

#     def registrar_consolidacion(self, resultado, margen_aplicado):
#         """
#         Guarda la factura y su detalle usando una transacción.
#         """
#         conn = self._get_connection()
#         try:
#             cursor = conn.cursor()
#             # 1. Insertar Cabecera (Usamos datos de la auditoría)
#             af = resultado["auditoria_fiscal"]
#             ahora = datetime.now()
            
#             cursor.execute('''
#                 INSERT INTO facturas (periodo_mes, periodo_anio, fecha_carga, total_neto_movistar, total_iva, total_final_pdf, markup_porcentaje)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             ''', (ahora.strftime("%m"), ahora.strftime("%Y"), ahora, resultado['total_final'], af['iva_pdf'], af['factura_pdf'], margen_aplicado))
            
#             factura_id = cursor.lastrowid

#             # 2. Insertar Detalle (Batch Insert)
#             for d in resultado['datos']:
#                 precio_markup = round(d['total_neto'] * (1 + margen_aplicado/100), 2)
#                 cursor.execute('''
#                     INSERT INTO consumos_detalle (factura_id, linea, nombre, grupo, costo_fijo, costo_variable, costo_juegos, neto_movistar, precio_con_markup)
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#                 ''', (factura_id, d['linea'], d['nombre'], d['categoria'], d['total_fijo'], d['total_variable'], d['juegos_extra'], d['total_neto'], precio_markup))
            
#             conn.commit()
#             return factura_id
#         except Exception as e:
#             conn.rollback() # Si algo falla, no se guarda nada.
#             raise e
#         finally:
#             conn.close()

            
#     def get_consumos_por_factura(self, factura_id):
#         """Trae todos los consumos de una factura específica para armar los boletos."""
#         with self._get_connection() as conn:
#             query = """
#                 SELECT linea, nombre, grupo, costo_fijo, costo_variable, costo_juegos, neto_movistar, precio_con_markup
#                 FROM consumos_detalle
#                 WHERE factura_id = ?
#             """
#             return pd.read_sql_query(query, conn, params=(factura_id,))

################################################################

import sqlite3
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='hierrosan_v2.db'):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tabla de Facturas: Cabecera con datos del PDF auditado
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    periodo_mes TEXT,
                    periodo_anio TEXT,
                    fecha_carga TIMESTAMP,
                    total_neto_movistar REAL,
                    total_iva REAL,
                    total_final_pdf REAL,
                    markup_porcentaje REAL
                )
            ''')
            # Tabla de Consumos: Detalle atómico por línea
            # Agregamos la columna 'categoria' para análisis interno
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consumos_detalle (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    factura_id INTEGER,
                    linea TEXT,
                    nombre TEXT,
                    grupo TEXT,
                    categoria TEXT,
                    costo_fijo REAL,
                    costo_variable REAL,
                    costo_juegos REAL,
                    neto_movistar REAL,
                    precio_con_markup REAL,
                    FOREIGN KEY (factura_id) REFERENCES facturas (id)
                )
            ''')
            conn.commit()
    def registrar_consolidacion(self, resultado, margen_aplicado, total_factura_movistar):
        """Guarda la factura y su detalle usando una transacción."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            af = resultado["auditoria_fiscal"]
            ahora = datetime.now()
            
            # 1. Insertar Cabecera (7 Columnas = 7 Signos de pregunta)
            cursor.execute('''
                INSERT INTO facturas (
                    periodo_mes, 
                    periodo_anio, 
                    fecha_carga, 
                    total_neto_movistar, 
                    total_iva, 
                    total_final_pdf, 
                    markup_porcentaje
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                resultado['periodo_mes'],   # El mes del date_input
                resultado['periodo_anio'], 
                resultado['fecha_manual'], 
                resultado['total_final'], 
                af['iva_pdf'], 
                total_factura_movistar, # Valor del PDF ($1.8M)
                margen_aplicado         # El porcentaje (ej: 21.0)
            ))
            
            factura_id = cursor.lastrowid

            # 2. Insertar Detalle
            for d in resultado['datos']:
                precio_markup = round(d['total_neto'] * (1 + margen_aplicado/100), 2)
                cursor.execute('''
                    INSERT INTO consumos_detalle (
                        factura_id, linea, nombre, grupo, categoria, 
                        costo_fijo, costo_variable, costo_juegos, neto_movistar, precio_con_markup
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (factura_id, d['linea'], d['nombre'], d['grupo'], d['categoria'], 
                    d['total_fijo'], d['total_variable'], d['juegos_extra'], d['total_neto'], precio_markup))
            
            conn.commit()
            return factura_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    

    def get_datos_consulta(self, periodo_str=None, grupo="TODOS"):
        """Trae consumos históricos con filtros aplicados."""
        with self._get_connection() as conn:
            query = """
               SELECT f.periodo_mes || '/' || f.periodo_anio as periodo, 
                   f.total_final_pdf, 
                   f.markup_porcentaje,  -- <--- ESTE ES EL MARGEN HISTÓRICO
                   c.linea, c.nombre, c.grupo, c.categoria, 
                   c.costo_fijo, c.costo_variable, c.costo_juegos, 
                   c.neto_movistar, c.precio_con_markup
            FROM consumos_detalle c
            JOIN facturas f ON c.factura_id = f.id
            WHERE 1=1
            """
            params = []
            
            if periodo_str and periodo_str != "TODOS":
                mes, anio = periodo_str.split('/')
                query += " AND f.periodo_mes = ? AND f.periodo_anio = ?"
                params.extend([mes, anio])
            
            if grupo and grupo != "TODOS":
                query += " AND c.grupo = ?"
                params.append(grupo)
            
            return pd.read_sql_query(query, conn, params=params)


    def get_grupos_unicos(self):
        """Retorna una lista de todos los grupos registrados en consumos_detalle."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT grupo FROM consumos_detalle WHERE grupo IS NOT NULL ORDER BY grupo")
            return [row[0] for row in cursor.fetchall()]

    def get_periodos_disponibles(self):
        """Retorna una lista de períodos (MM/YYYY) disponibles en la DB."""
        with self._get_connection() as conn:
            query = """
                SELECT DISTINCT (periodo_mes || '/' || periodo_anio) as periodo 
                FROM facturas 
                ORDER BY periodo_anio DESC, periodo_mes DESC
            """
            df = pd.read_sql_query(query, conn)
            return df['periodo'].tolist()

    
    def get_consumos_por_factura(self, factura_id):
        """Trae consumos de una factura para la vista de Abonos."""
        with self._get_connection() as conn:
            query = """
                SELECT linea, nombre, grupo, costo_fijo, costo_variable, costo_juegos, neto_movistar, precio_con_markup
                FROM consumos_detalle
                WHERE factura_id = ?
            """
            return pd.read_sql_query(query, conn, params=(factura_id,))