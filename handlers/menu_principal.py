from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import get_main_menu


async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "🏠 Menú principal\n\n"
        "¿Qué deseas hacer?",
        reply_markup=get_main_menu(),
    )