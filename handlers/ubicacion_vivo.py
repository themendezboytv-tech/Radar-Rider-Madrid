from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from geopy.distance import geodesic

from database.database import obtener_avisos_activos
from handlers.avisos_cerca import RADIO_KM, _formatear_distancia

# =====================================================
# SESIONES DE UBICACIÓN EN VIVO (v1.10)
# =====================================================
# En memoria, no en la BD: son efímeras a propósito. Si el
# contenedor se reinicia a mitad de una sesión, se pierde y el
# usuario debe volver a compartir ubicación (caso raro, aceptado).

_sesiones_vivo: dict[int, dict] = {}


def iniciar_sesion_vivo(user_id: int, chat_id: int, live_period: int):

    _sesiones_vivo[user_id] = {
        "chat_id": chat_id,
        "expira": datetime.utcnow() + timedelta(seconds=live_period),
        "notificados": set(),
    }


async def recibir_ubicacion_vivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Procesa las actualizaciones de una ubicación en vivo (llegan como
    edited_message, no como message). Si el usuario no tiene una sesión
    en vivo activa, no hace nada.
    """

    if not update.edited_message or not update.edited_message.location:
        return

    user_id = update.edited_message.from_user.id

    sesion = _sesiones_vivo.get(user_id)

    if sesion is None:
        return

    if datetime.utcnow() >= sesion["expira"]:
        del _sesiones_vivo[user_id]
        return

    latitud = update.edited_message.location.latitude
    longitud = update.edited_message.location.longitude

    origen = (latitud, longitud)

    for aviso in obtener_avisos_activos():

        if aviso["id"] in sesion["notificados"]:
            continue

        destino = (aviso["latitud"], aviso["longitud"])
        distancia_km = geodesic(origen, destino).km

        if distancia_km > RADIO_KM:
            continue

        sesion["notificados"].add(aviso["id"])

        mensaje = f"🔔 {aviso['tipo']}\n📏 {_formatear_distancia(distancia_km)}"

        if aviso["calle"]:
            mensaje += f"\n📍 {aviso['calle']}"

        try:
            await context.bot.send_message(
                chat_id=sesion["chat_id"],
                text=mensaje,
            )
        except Exception:
            pass
