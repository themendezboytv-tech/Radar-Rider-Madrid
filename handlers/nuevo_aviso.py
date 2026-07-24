from telegram import Update
from telegram.ext import ContextTypes

from keyboards.aviso_menu import (
    get_aviso_menu,
    get_location_menu,
)


async def nuevo_aviso(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🚨 *Nuevo aviso*\n\n"
        "¿Qué deseas reportar?",
        parse_mode="Markdown",
        reply_markup=get_aviso_menu(),
    )


async def pedir_ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tipo = context.user_data.get("tipo_aviso", "Sin definir")

    await update.message.reply_text(
        f"✅ Tipo seleccionado:\n\n"
        f"{tipo}\n\n"
        "📍 Ahora comparte tu ubicación.",
        reply_markup=get_location_menu(),
    )