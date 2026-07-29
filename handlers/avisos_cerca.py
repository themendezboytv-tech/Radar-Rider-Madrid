from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from geopy.distance import geodesic

from keyboards.aviso_menu import get_location_menu
from handlers.menu_principal import mostrar_menu

from database.database import (
    expirar_avisos_vencidos,
    obtener_avisos_activos,
)

# =====================================================
# CONFIGURACIÓN
# =====================================================

RADIO_KM = 5
MAX_RESULTADOS = 10


# =====================================================
# PASO 1: PEDIR UBICACIÓN
# =====================================================

async def avisos_cerca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Pide la ubicación del usuario para poder calcular qué
    avisos activos tiene cerca. La ubicación en sí se procesa
    en handlers/ubicacion.py, que detecta el flag
    "buscando_cerca" y llama a mostrar_avisos_cercanos().
    """

    context.user_data.clear()
    context.user_data["buscando_cerca"] = True

    await update.message.reply_text(
        "📍 Comparte tu ubicación para ver los avisos activos cerca de ti.",
        reply_markup=get_location_menu(),
    )


# =====================================================
# HELPERS DE FORMATO
# =====================================================

def _tiempo_transcurrido(fecha_creacion: str) -> str:
    """Convierte un timestamp ISO en UTC a un texto tipo 'hace 12 min'."""

    try:
        creado = datetime.fromisoformat(fecha_creacion)
    except ValueError:
        return ""

    minutos = int((datetime.utcnow() - creado).total_seconds() // 60)

    if minutos < 1:
        return "hace instantes"
    elif minutos < 60:
        return f"hace {minutos} min"
    else:
        horas = minutos // 60
        return f"hace {horas}h"


def _formatear_distancia(km: float) -> str:

    if km < 1:
        return f"{int(km * 1000)} m"
    else:
        return f"{km:.1f} km"


# =====================================================
# PASO 2: CALCULAR Y MOSTRAR AVISOS CERCANOS
# =====================================================

async def mostrar_avisos_cercanos(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    latitud: float,
    longitud: float,
):
    """
    Recibida la ubicación del usuario, calcula la distancia a
    cada aviso activo y devuelve los más cercanos dentro de
    RADIO_KM, ordenados de más cerca a más lejos.
    """

    # Antes de consultar, se limpian los avisos ya vencidos.
    # obtener_avisos_activos() ya filtra por fecha_expira, así
    # que esto es más higiene de datos que necesidad estricta,
    # pero deja la tabla al día para v1.5/v1.6.
    expirar_avisos_vencidos()

    avisos = obtener_avisos_activos()

    origen = (latitud, longitud)

    cercanos = []

    for aviso in avisos:

        destino = (aviso["latitud"], aviso["longitud"])
        distancia_km = geodesic(origen, destino).km

        if distancia_km <= RADIO_KM:
            cercanos.append((distancia_km, aviso))

    context.user_data.clear()

    # ==========================================
    # SIN RESULTADOS
    # ==========================================

    if not cercanos:

        await update.message.reply_text(
            f"✅ No hay avisos activos en un radio de {RADIO_KM} km.\n\n"
            "¡Todo tranquilo por ahora!"
        )

        await mostrar_menu(update, context)
        return

    # ==========================================
    # CON RESULTADOS
    # ==========================================

    cercanos.sort(key=lambda item: item[0])
    cercanos = cercanos[:MAX_RESULTADOS]

    mensaje = f"📍 Avisos activos cerca de ti (radio {RADIO_KM} km)\n"
    mensaje += "━━━━━━━━━━━━━━\n\n"

    for distancia_km, aviso in cercanos:

        tipo = aviso["tipo"]
        calle = aviso["calle"]
        ciudad = aviso["ciudad"]
        comentario = aviso["comentario"]

        mensaje += f"{tipo}\n"

        mensaje += (
            f"📏 {_formatear_distancia(distancia_km)} · "
            f"{_tiempo_transcurrido(aviso['fecha_creacion'])}\n"
        )

        if calle:

            linea = f"📍 {calle}"

            if ciudad:
                linea += f", {ciudad}"

            mensaje += linea + "\n"

        if comentario:
            mensaje += f"💬 {comentario}\n"

        mensaje += "\n"

    await update.message.reply_text(mensaje)

    await mostrar_menu(update, context)
