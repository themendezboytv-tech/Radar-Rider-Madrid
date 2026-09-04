# =====================================================
# RADAR RIDER MADRID - BASE DE DATOS (SQLite)
# =====================================================
#
# Este módulo centraliza todo el acceso a datos del bot.
# El esquema está pensado no solo para v1.3 (guardar avisos)
# sino para lo que viene después:
#
#   v1.4  -> avisos_cerca / expiración         (lat, lon, expira_en, activo)
#   v1.5  -> mapa interactivo                   (lat, lon, tipo)
#   v1.6  -> estadísticas                       (user_id, tipo, fecha)
#   v1.7  -> sistema de reputación               (user_id, es_falso, puntos)
#   v1.8  -> notificaciones inteligentes         (user_id, zonas_interes)
#
# Por eso el esquema guarda más campos de los estrictamente
# necesarios hoy: así no habrá que hacer migraciones dolorosas
# más adelante.
# =====================================================

import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

# =====================================================
# RUTA DE LA BASE DE DATOS
# =====================================================

# DB_DIR es configurable via variable de entorno para poder apuntar
# a un volumen persistente (ej. /app/data en Docker, mapeado a un
# bind mount del host). Si no se define, se usa la carpeta del propio
# módulo (comportamiento anterior, útil para correr el bot fuera de
# Docker sin configuración extra).
DB_DIR = os.getenv("DB_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "radar_rider_madrid.db")

# Minutos de vigencia por defecto según el tipo de aviso.
# Se usa en v1.4 para el filtro de "avisos cerca" y para
# marcar avisos como expirados automáticamente.
EXPIRACION_MINUTOS = {
    "🚓 Presencia policial": 90,
    "🚧 Calle cortada": 240,
    "🚦 Tráfico": 60,
    "🚑 Accidente": 120,
    "⚠️ Peligro": 180,
    "📦 Otro": 90,
}
EXPIRACION_DEFECTO_MINUTOS = 90


# =====================================================
# CONEXIÓN
# =====================================================

@contextmanager
def get_connection():
    """
    Context manager para obtener una conexión SQLite.
    Usa row_factory=Row para poder acceder a las columnas
    por nombre (fila["campo"]) en vez de por índice.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# =====================================================
# INICIALIZACIÓN DEL ESQUEMA
# =====================================================

def init_db():
    """
    Crea las tablas si no existen. Debe llamarse una vez
    al arrancar el bot (ver bot.py).
    """

    with get_connection() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS avisos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                username        TEXT,
                tipo            TEXT NOT NULL,
                latitud         REAL NOT NULL,
                longitud        REAL NOT NULL,
                calle           TEXT,
                numero          TEXT,
                ciudad          TEXT,
                provincia       TEXT,
                comentario      TEXT,
                fecha_creacion  TEXT NOT NULL,
                fecha_expira    TEXT NOT NULL,
                activo          INTEGER NOT NULL DEFAULT 1,
                es_falso        INTEGER NOT NULL DEFAULT 0,
                votos_falso     INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # Índices para las consultas más frecuentes de v1.4/v1.5/v1.6:
        # "avisos activos cerca de una ubicación" y "avisos por usuario".
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_avisos_activo "
            "ON avisos (activo, fecha_expira)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_avisos_user "
            "ON avisos (user_id)"
        )

        # Tabla de usuarios: base para v1.7 (reputación) y
        # v1.8 (configuración / zonas de interés). Se crea ya
        # para no tener que migrar más adelante.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id             INTEGER PRIMARY KEY,
                username            TEXT,
                puntos_reputacion   INTEGER NOT NULL DEFAULT 0,
                avisos_publicados   INTEGER NOT NULL DEFAULT 0,
                avisos_falsos       INTEGER NOT NULL DEFAULT 0,
                fecha_registro      TEXT NOT NULL
            )
            """
        )

        # Migración v1.8 (notificaciones inteligentes): la tabla
        # usuarios ya existe en producción sin estas columnas, así
        # que se añaden con ALTER TABLE + try/except en vez de
        # tocar el CREATE TABLE (SQLite no soporta "ADD COLUMN IF
        # NOT EXISTS").
        for ddl in (
            "ALTER TABLE usuarios ADD COLUMN radio_notificacion_km REAL",
            "ALTER TABLE usuarios ADD COLUMN lat_referencia REAL",
            "ALTER TABLE usuarios ADD COLUMN lon_referencia REAL",
        ):
            try:
                conn.execute(ddl)
            except sqlite3.OperationalError:
                pass

        # Migración v1.9 (botón "✅ Confirmado"): mismo patrón que la
        # de v1.8, esta vez sobre la tabla avisos.
        try:
            conn.execute(
                "ALTER TABLE avisos ADD COLUMN votos_confirmado INTEGER NOT NULL DEFAULT 0"
            )
        except sqlite3.OperationalError:
            pass


# =====================================================
# HELPERS INTERNOS
# =====================================================

def _calcular_expiracion(tipo: str, ahora: datetime) -> datetime:
    minutos = EXPIRACION_MINUTOS.get(tipo, EXPIRACION_DEFECTO_MINUTOS)
    return ahora + timedelta(minutes=minutos)


def _asegurar_usuario(conn, user_id: int, username: str | None):
    """
    Crea la fila del usuario si no existe (upsert simple).
    Se llama internamente al guardar un aviso.
    """

    ahora = datetime.utcnow().isoformat()

    conn.execute(
        """
        INSERT INTO usuarios (user_id, username, fecha_registro)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username
        """,
        (user_id, username, ahora),
    )


# =====================================================
# GUARDAR AVISO
# =====================================================

def guardar_aviso(
    user_id: int,
    username: str | None,
    tipo: str,
    latitud: float,
    longitud: float,
    direccion: dict,
    comentario: str,
) -> int:
    """
    Guarda un aviso nuevo en la base de datos y devuelve su id.
    `direccion` es el dict que ya devuelve services/geocoder.py
    (calle, numero, ciudad, provincia, ...).
    """

    ahora = datetime.utcnow()
    expira = _calcular_expiracion(tipo, ahora)

    with get_connection() as conn:

        _asegurar_usuario(conn, user_id, username)

        cursor = conn.execute(
            """
            INSERT INTO avisos (
                user_id, username, tipo,
                latitud, longitud,
                calle, numero, ciudad, provincia,
                comentario,
                fecha_creacion, fecha_expira,
                activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                user_id,
                username,
                tipo,
                latitud,
                longitud,
                direccion.get("calle", ""),
                direccion.get("numero", ""),
                direccion.get("ciudad", ""),
                direccion.get("provincia", ""),
                comentario,
                ahora.isoformat(),
                expira.isoformat(),
            ),
        )

        conn.execute(
            """
            UPDATE usuarios
            SET avisos_publicados = avisos_publicados + 1,
                puntos_reputacion = puntos_reputacion + 1
            WHERE user_id = ?
            """,
            (user_id,),
        )

        return cursor.lastrowid


# =====================================================
# CONSULTAS (base para v1.4, v1.5, v1.6)
# =====================================================

def obtener_avisos_activos() -> list[sqlite3.Row]:
    """
    Devuelve los avisos activos y no expirados.
    Base para v1.4 (avisos cerca) y v1.5 (mapa).
    """

    ahora = datetime.utcnow().isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM avisos
            WHERE activo = 1
              AND fecha_expira > ?
              AND es_falso = 0
            ORDER BY fecha_creacion DESC
            """,
            (ahora,),
        )
        return cursor.fetchall()


def obtener_avisos_por_usuario(user_id: int, limite: int = 20) -> list[sqlite3.Row]:
    """Historial de avisos de un usuario. Base para v1.6 (estadísticas)."""

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM avisos
            WHERE user_id = ?
            ORDER BY fecha_creacion DESC
            LIMIT ?
            """,
            (user_id, limite),
        )
        return cursor.fetchall()


def contar_avisos_usuario(user_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) as total FROM avisos WHERE user_id = ?",
            (user_id,),
        )
        return cursor.fetchone()["total"]


def expirar_avisos_vencidos() -> int:
    """
    Marca como inactivos los avisos cuya fecha_expira ya pasó.
    Se puede llamar periódicamente (JobQueue) o antes de cada
    consulta de avisos activos. Devuelve cuántos se expiraron.
    """

    ahora = datetime.utcnow().isoformat()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE avisos
            SET activo = 0
            WHERE activo = 1 AND fecha_expira <= ?
            """,
            (ahora,),
        )
        return cursor.rowcount


# =====================================================
# MODERACIÓN (base para v1.7 - reputación)
# =====================================================

def marcar_como_falso(aviso_id: int) -> None:
    """
    Incrementa el contador de votos "falso" de un aviso y,
    a partir de un umbral, lo marca como es_falso=1 (deja de
    salir en obtener_avisos_activos) y penaliza al autor con
    -1 punto de reputación.
    """

    UMBRAL_VOTOS_FALSO = 3

    with get_connection() as conn:

        conn.execute(
            """
            UPDATE avisos
            SET votos_falso = votos_falso + 1
            WHERE id = ?
            """,
            (aviso_id,),
        )

        cursor = conn.execute(
            "SELECT votos_falso, user_id FROM avisos WHERE id = ?",
            (aviso_id,),
        )
        fila = cursor.fetchone()

        if fila and fila["votos_falso"] >= UMBRAL_VOTOS_FALSO:

            conn.execute(
                "UPDATE avisos SET es_falso = 1, activo = 0 WHERE id = ?",
                (aviso_id,),
            )

            conn.execute(
                """
                UPDATE usuarios
                SET avisos_falsos = avisos_falsos + 1,
                    puntos_reputacion = puntos_reputacion - 1
                WHERE user_id = ?
                """,
                (fila["user_id"],),
            )


def confirmar_aviso(aviso_id: int) -> None:
    """
    Incrementa el contador de votos "confirmado" de un aviso.
    Puramente informativo (v1.9): sin umbral ni efecto sobre
    reputación o estado del aviso, a diferencia de marcar_como_falso().
    """

    with get_connection() as conn:
        conn.execute(
            "UPDATE avisos SET votos_confirmado = votos_confirmado + 1 WHERE id = ?",
            (aviso_id,),
        )


# =====================================================
# NOTIFICACIONES INTELIGENTES (v1.8)
# =====================================================

def activar_notificaciones(
    user_id: int,
    username: str | None,
    lat: float,
    lon: float,
    radio_km: float,
) -> None:
    """Activa (o actualiza) las notificaciones de cercanía de un usuario."""

    with get_connection() as conn:

        _asegurar_usuario(conn, user_id, username)

        conn.execute(
            """
            UPDATE usuarios
            SET radio_notificacion_km = ?,
                lat_referencia = ?,
                lon_referencia = ?
            WHERE user_id = ?
            """,
            (radio_km, lat, lon, user_id),
        )


def desactivar_notificaciones(user_id: int) -> None:
    """Desactiva las notificaciones de cercanía de un usuario."""

    with get_connection() as conn:
        conn.execute(
            "UPDATE usuarios SET radio_notificacion_km = NULL WHERE user_id = ?",
            (user_id,),
        )


def obtener_config_notificaciones(user_id: int) -> sqlite3.Row | None:
    """Devuelve la config de notificaciones de un usuario (o None si no existe)."""

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT radio_notificacion_km, lat_referencia, lon_referencia
            FROM usuarios
            WHERE user_id = ?
            """,
            (user_id,),
        )
        return cursor.fetchone()


def obtener_usuarios_con_notificaciones() -> list[sqlite3.Row]:
    """
    Usuarios con notificaciones activas (radio y ubicación de
    referencia guardados). Base para el aviso automático en
    handlers/comentario.py.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT user_id, lat_referencia, lon_referencia, radio_notificacion_km
            FROM usuarios
            WHERE radio_notificacion_km IS NOT NULL
              AND lat_referencia IS NOT NULL
              AND lon_referencia IS NOT NULL
            """
        )
        return cursor.fetchall()
