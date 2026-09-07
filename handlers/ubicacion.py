from telegram import Update
from telegram.ext import ContextTypes

from services.geocoder import obtener_direccion
from handlers.avisos_cerca import mostrar_avisos_cercanos, RADIO_KM
from handlers.configuracion import pedir_radio_notificacion
from handlers.comentario import publicar_aviso
from handlers.ubicacion_vivo import iniciar_sesion_vivo


async def recibir_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.location:
        return

    latitud = update.message.location.latitude
    longitud = update.message.location.longitude

    # ==========================================
    # FLUJO: BUSCANDO AVISOS CERCA (v1.4)
    # ==========================================

    if context.user_data.get("buscando_cerca"):

        live_period = update.message.location.live_period

        if live_period:

            iniciar_sesion_vivo(
                update.effective_user.id,
                update.effective_chat.id,
                live_period,
            )

            context.user_data.clear()

            await update.message.reply_text(
                "🔴 Ubicación en vivo activada.\n\n"
                f"Te avisaré si aparece algo nuevo cerca (radio {RADIO_KM} km) "
                "mientras compartas tu ubicación."
            )

            return

        await mostrar_avisos_cercanos(update, context, latitud, longitud)
        return

    # ==========================================
    # FLUJO: ACTIVANDO NOTIFICACIONES (v1.8)
    # ==========================================

    if context.user_data.get("configurando_notificaciones"):

        await pedir_radio_notificacion(update, context, latitud, longitud)
        return

    # ==========================================
    # ¿HAY UN AVISO EN CURSO?
    # ==========================================

    if "tipo_aviso" not in context.user_data:

        await update.message.reply_text(
            "ℹ️ No hay ningún aviso en curso.\n\n"
            "Pulsa «🚨 Nuevo aviso» para comenzar."
        )

        return

    # ==========================================
    # FLUJO: CREANDO UN AVISO NUEVO
    # ==========================================

    context.user_data["latitud"] = latitud
    context.user_data["longitud"] = longitud

    direccion = obtener_direccion(latitud, longitud)

    if direccion is None:

        direccion = {
            "calle": "",
            "numero": "",
            "ciudad": "",
            "provincia": "",
            "codigo_postal": "",
            "pais": "",
        }

    context.user_data["direccion"] = direccion

    # ==========================================
    # ACCIDENTE / CALLE CORTADA: se publican directo, sin pedir comentario
    # ==========================================

    if context.user_data.get("tipo_aviso") in ["🚑 Accidente", "🚧 Calle cortada"]:

        await publicar_aviso(update, context, comentario="")

        return

    context.user_data["esperando_comentario"] = True

    calle = direccion.get("calle", "")
    numero = direccion.get("numero", "")
    ciudad = direccion.get("ciudad", "")

    mensaje = "✅ Ubicación recibida correctamente.\n\n"

    if calle:

        if numero:
            mensaje += f"📍 {calle}, {numero}\n"
        else:
            mensaje += f"📍 {calle}\n"

        if ciudad:
            mensaje += f"🏙️ {ciudad}\n"

    mensaje += (
        "\n💬 Escribe un comentario.\n\n"
        "Ejemplo:\n"
        "• Control de alcoholemia\n"
        "• Radar móvil\n"
        "• Vehículo detenido\n\n"
        "Si no deseas añadir un comentario escribe:\n"
        "-"
    )

    await update.message.reply_text(mensaje)
