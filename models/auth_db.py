import sqlite3
import hashlib

class AuthManager:
    def __init__(self, db_path="seguridad.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    username TEXT PRIMARY KEY, 
                    password_hash TEXT, 
                    pregunta TEXT, 
                    respuesta_hash TEXT
                )
            """)

    def _hash(self, texto):
        # SHA256 es nativo, rápido y seguro.
        return hashlib.sha256(texto.encode()).hexdigest()

    def verificar_login(self, user, password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT password_hash FROM usuarios WHERE username = ?", (user,))
            row = cursor.fetchone()
            if row:
                return row[0] == self._hash(password)
        return False

    def registrar_usuario(self, user, password, pregunta, respuesta):
        with sqlite3.connect(self.db_path) as conn:
            # Usamos INSERT OR REPLACE para que si lo corres dos veces no explote
            conn.execute("INSERT OR REPLACE INTO usuarios VALUES (?, ?, ?, ?)", 
                        (user, self._hash(password), pregunta, self._hash(respuesta.lower().strip())))
            conn.commit()

    def obtener_pregunta(self, user):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT pregunta FROM usuarios WHERE username = ?", (user,)).fetchone()
            return row[0] if row else None

    def verificar_y_resetear(self, user, resp, nueva_p):
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT respuesta_hash FROM usuarios WHERE username = ?", (user,)).fetchone()
            if row and row[0] == self._hash(resp.lower().strip()):
                conn.execute("UPDATE usuarios SET password_hash = ? WHERE username = ?", (self._hash(nueva_p), user))
                conn.commit()
                return True
        return False
    
    def listar_usuarios(self):
        """Retorna una lista de todos los nombres de usuario registrados."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT username FROM usuarios")
            return [row[0] for row in cursor.fetchall()]

    def eliminar_usuario(self, username):
        """Elimina un usuario de la base de datos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM usuarios WHERE username = ?", (username,))
            conn.commit()
            return True