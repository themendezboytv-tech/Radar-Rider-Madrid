from telegram import Update
from telegram.ext import ContextTypes


async def estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📊 Estadísticas\n\n"
        "🚧 Esta función estará disponible próximamente."
    )