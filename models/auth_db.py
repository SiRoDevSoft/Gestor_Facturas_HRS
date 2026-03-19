import sqlite3
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def __init__(self, db_path="seguridad.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS usuarios (username TEXT PRIMARY KEY, password_hash TEXT, pregunta TEXT, respuesta_hash TEXT)")

    def verificar_login(self, user, password):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT password_hash FROM usuarios WHERE username = ?", (user,)).fetchone()
            return pwd_context.verify(password, row[0]) if row else False

    def registrar_usuario(self, user, password, pregunta, respuesta):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?)", 
                        (user, pwd_context.hash(password), pregunta, pwd_context.hash(respuesta.lower().strip())))

    def obtener_pregunta(self, user):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT pregunta FROM usuarios WHERE username = ?", (user,)).fetchone()
            return row[0] if row else None

    def verificar_y_resetear(self, user, resp, nueva_p):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT respuesta_hash FROM usuarios WHERE username = ?", (user,)).fetchone()
            if row and pwd_context.verify(resp.lower().strip(), row[0]):
                conn.execute("UPDATE usuarios SET password_hash = ? WHERE username = ?", (pwd_context.hash(nueva_p), user))
                return True
        return False