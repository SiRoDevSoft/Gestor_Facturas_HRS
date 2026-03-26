# import sqlite3
# import hashlib

# class AuthManager:
#     def __init__(self, db_path="seguridad.db"):
#         self.db_path = db_path
#         with sqlite3.connect(self.db_path) as conn:
#             conn.execute("""
#                 CREATE TABLE IF NOT EXISTS usuarios (
#                     username TEXT PRIMARY KEY, 
#                     password_hash TEXT, 
#                     pregunta TEXT, 
#                     respuesta_hash TEXT
#                 )
#             """)

#     def _hash(self, texto):
#         # SHA256 es nativo, rápido y seguro.
#         return hashlib.sha256(texto.encode()).hexdigest()

#     def verificar_login(self, user, password):
#         with sqlite3.connect(self.db_path) as conn:
#             cursor = conn.execute("SELECT password_hash FROM usuarios WHERE username = ?", (user,))
#             row = cursor.fetchone()
#             if row:
#                 return row[0] == self._hash(password)
#         return False

#     def registrar_usuario(self, user, password, pregunta, respuesta):
#         with sqlite3.connect(self.db_path) as conn:
#             # Usamos INSERT OR REPLACE para que si lo corres dos veces no explote
#             conn.execute("INSERT OR REPLACE INTO usuarios VALUES (?, ?, ?, ?)", 
#                         (user, self._hash(password), pregunta, self._hash(respuesta.lower().strip())))
#             conn.commit()

#     def obtener_pregunta(self, user):
#         with sqlite3.connect(self.db_path) as conn:
#             row = conn.execute("SELECT pregunta FROM usuarios WHERE username = ?", (user,)).fetchone()
#             return row[0] if row else None

#     def verificar_y_resetear(self, user, resp, nueva_p):
#         with sqlite3.connect(self.db_path) as conn:
#             row = conn.execute("SELECT respuesta_hash FROM usuarios WHERE username = ?", (user,)).fetchone()
#             if row and row[0] == self._hash(resp.lower().strip()):
#                 conn.execute("UPDATE usuarios SET password_hash = ? WHERE username = ?", (self._hash(nueva_p), user))
#                 conn.commit()
#                 return True
#         return False
    
#     def listar_usuarios(self):
#         """Retorna una lista de todos los nombres de usuario registrados."""
#         with sqlite3.connect(self.db_path) as conn:
#             cursor = conn.execute("SELECT username FROM usuarios")
#             return [row[0] for row in cursor.fetchall()]

#     def eliminar_usuario(self, username):
#         """Elimina un usuario de la base de datos."""
#         with sqlite3.connect(self.db_path) as conn:
#             conn.execute("DELETE FROM usuarios WHERE username = ?", (username,))
#             conn.commit()
#             return True
#############################################################################################################

import streamlit as st
import hashlib
from sqlalchemy import create_engine, text

class AuthManager:
    def __init__(self):
        # 1. Usamos la URL de Neon (San Pablo) que cargamos en Secrets
        try:
            self.url = st.secrets["USER_DATABASE_URL"].strip()
            # Aseguramos el driver psycopg2
            if "postgresql" in self.url and "+psycopg2" not in self.url:
                self.url = self.url.replace("postgresql://", "postgresql+psycopg2://")
            
            self.engine = create_engine(
                self.url,
                pool_size=5, 
                max_overflow=10, 
                pool_pre_ping=True,
                pool_recycle=300 
       )
        except Exception as e:
            st.error(f"🚨 Error en AuthDB: {str(e)}")
            raise e

    def _hash(self, texto):
        return hashlib.sha256(texto.encode()).hexdigest()

    def verificar_login(self, user, password):
        query = text("SELECT password_hash FROM usuarios WHERE nombre = :u")
        with self.engine.connect() as conn:
            row = conn.execute(query, {"u": user}).fetchone()
            if row:
                return row[0] == self._hash(password)
        return False

    def registrar_usuario(self, user, password, pregunta, respuesta):
        query = text("""
            INSERT INTO usuarios (nombre, password_hash, pregunta_seguridad, respuesta_hash)
            VALUES (:u, :p, :pr, :re)
            ON CONFLICT (nombre) DO UPDATE SET 
                password_hash = EXCLUDED.password_hash,
                pregunta_seguridad = EXCLUDED.pregunta_seguridad,
                respuesta_hash = EXCLUDED.respuesta_hash
        """)
        with self.engine.begin() as conn:
            conn.execute(query, {
                "u": user, 
                "p": self._hash(password), 
                "pr": pregunta, 
                "re": self._hash(respuesta.lower().strip())
            })

    def obtener_pregunta(self, user):
        query = text("SELECT pregunta_seguridad FROM usuarios WHERE nombre = :u")
        with self.engine.connect() as conn:
            row = conn.execute(query, {"u": user}).fetchone()
            return row[0] if row else None

    def verificar_y_resetear(self, user, resp, nueva_p):
        query_check = text("SELECT respuesta_hash FROM usuarios WHERE nombre = :u")
        with self.engine.begin() as conn:
            row = conn.execute(query_check, {"u": user}).fetchone()
            if row and row[0] == self._hash(resp.lower().strip()):
                conn.execute(
                    text("UPDATE usuarios SET password_hash = :p WHERE nombre = :u"),
                    {"p": self._hash(nueva_p), "u": user}
                )
                return True
        return False
    
    def listar_usuarios(self):
        query = text("SELECT nombre FROM usuarios")
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return [row[0] for row in result.fetchall()]

    def eliminar_usuario(self, username):
        query = text("DELETE FROM usuarios WHERE nombre = :u")
        with self.engine.begin() as conn:
            conn.execute(query, {"u": username})
            return True