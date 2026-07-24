import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from config import GROUP_ID
from handlers.menu_principal import mostrar_menu


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
    # MENSAJE PARA EL GRUPO
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

    # ==========================================
    # PUBLICAR EN EL GRUPO
    # ==========================================

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=mensaje,
    )

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