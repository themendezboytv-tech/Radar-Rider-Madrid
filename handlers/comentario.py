import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from geopy.distance import geodesic

from config import GROUP_ID, CHANNEL_ID
from handlers.menu_principal import mostrar_menu
from database.database import guardar_aviso, obtener_usuarios_con_notificaciones
from services.whatsapp import enviar_alerta_whatsapp


async def recibir_comentario(update: Update, context: ContextTypes.DEFAULT_TYPE):

    comentario = update.message.text.strip()

    if comentario == "-":
        comentario = ""

    tipo = context.user_data.get("tipo_aviso", "Sin definir")

    latitud = context.user_data.get("latitud")
    longitud = context.user_data.get("longitud")

    direccion = context.user_data.get("direccion", {})

    calle = direccion.get("calle", "")
    numero = direccion.get("numero", "")
    ciudad = direccion.get("ciudad", "")

    # ==========================================
    # GUARDAR EN BASE DE DATOS
    # ==========================================
    # Se guarda ANTES de publicar en Telegram: si algo falla
    # al enviar el mensaje, el aviso no se pierde igualmente.

    usuario = update.effective_user

    aviso_id = guardar_aviso(
        user_id=usuario.id,
        username=usuario.username or usuario.first_name,
        tipo=tipo,
        latitud=latitud,
        longitud=longitud,
        direccion=direccion,
        comentario=comentario,
    )

    # ==========================================
    # CONSTRUIR DIRECCIÓN
    # ==========================================

    if calle:

        if numero:
            linea_direccion = f"📍 {calle}, {numero}"
        else:
            linea_direccion = f"📍 {calle}"

    else:

        linea_direccion = f"📍 {latitud:.6f}, {longitud:.6f}"

    # ==========================================
    # MENSAJE
    # ==========================================

    mensaje = (
        "🚨 ALERTA VIAL\n"
        "━━━━━━━━━━━━━━\n\n"
    )

    mensaje += f"{tipo}\n\n"

    mensaje += linea_direccion + "\n"

    if ciudad:
        mensaje += f"🏙️ {ciudad}\n"

    if comentario:
        mensaje += f"\n💬 {comentario}\n"

    mensaje += (
        f"\n🗺️ Abrir en Google Maps\n"
        f"https://maps.google.com/?q={latitud},{longitud}"
    )

    mensaje += f"\n\n👤 Reportado por: {usuario.username or usuario.first_name}"

    # ==========================================
    # BOTONES DE MODERACIÓN (v1.7 falso / v1.9 confirmado)
    # ==========================================

    botones = InlineKeyboardMarkup([[
        InlineKeyboardButton("👎 No es real", callback_data=f"falso:{aviso_id}"),
        InlineKeyboardButton("✅ Confirmado", callback_data=f"confirmado:{aviso_id}"),
    ]])

    # ==========================================
    # PUBLICAR EN EL GRUPO
    # ==========================================

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=mensaje,
        reply_markup=botones,
    )

    # ==========================================
    # PUBLICAR EN EL CANAL
    # ==========================================

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=mensaje,
        reply_markup=botones,
    )

    # ==========================================
    # ENVIAR TAMBIÉN POR WHATSAPP (best-effort)
    # ==========================================
    # No debe afectar al flujo de Telegram: si OpenWA falla o no hay
    # destino configurado, la alerta ya está publicada igualmente.

    await asyncio.to_thread(enviar_alerta_whatsapp, mensaje)

    # ==========================================
    # NOTIFICAR A USUARIOS CERCA (v1.8, best-effort)
    # ==========================================
    # No debe afectar al flujo si algo falla: el aviso ya está
    # guardado y publicado igualmente.

    try:
        await _notificar_usuarios_cerca(context, tipo, latitud, longitud, calle)
    except Exception:
        pass

    # ==========================================
    # LIMPIAR SESIÓN
    # ==========================================

    context.user_data.clear()

    # ==========================================
    # CONFIRMACIÓN
    # ==========================================

    await update.message.reply_text(
        "✅ ¡Gracias!\n\n"
        "Tu alerta ha sido publicada correctamente."
    )

    # ==========================================
    # ESPERAR 3 SEGUNDOS
    # ==========================================

    await asyncio.sleep(3)

    # ==========================================
    # MENÚ PRINCIPAL
    # ==========================================

    await mostrar_menu(update, context)


# =====================================================
# NOTIFICACIONES INTELIGENTES (v1.8)
# =====================================================

async def _notificar_usuarios_cerca(
    context: ContextTypes.DEFAULT_TYPE,
    tipo: str,
    latitud: float,
    longitud: float,
    calle: str,
):
    """
    Avisa por privado a los usuarios con notificaciones activas
    cuya ubicación de referencia está dentro de su radio respecto
    al aviso recién publicado. Un fallo al enviar a un usuario
    concreto no debe impedir avisar al resto.
    """

    origen = (latitud, longitud)

    for usuario in obtener_usuarios_con_notificaciones():

        destino = (usuario["lat_referencia"], usuario["lon_referencia"])
        distancia_km = geodesic(origen, destino).km

        if distancia_km > usuario["radio_notificacion_km"]:
            continue

        mensaje = (
            "🔔 Aviso cerca de tu zona\n\n"
            f"{tipo}\n"
            f"📏 {distancia_km:.1f} km"
        )

        if calle:
            mensaje += f"\n📍 {calle}"

        try:
            await context.bot.send_message(
                chat_id=usuario["user_id"],
                text=mensaje,
            )
        except Exception:
            pass
