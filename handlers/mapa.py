from telegram import Update
from telegram.ext import ContextTypes


async def mapa(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🗺️ Mapa\n\n"
        "🚧 Esta función estará disponible próximamente."
    )