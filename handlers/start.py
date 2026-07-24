from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import get_main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "👋 ¡Bienvenido a Radar Rider Madrid! 🛵\n\n"
        "Una comunidad creada por repartidores,\n"
        "para repartidores.\n\n"
        "Comparte avisos útiles en tiempo real\n"
        "y ayuda a toda la comunidad.\n\n"
        "🚨 Actualmente estamos validando\n"
        "el sistema de Alertas Viales.",
        reply_markup=get_main_menu(),
    )