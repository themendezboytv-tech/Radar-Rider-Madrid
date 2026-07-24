from telegram import Update
from telegram.ext import ContextTypes


async def configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "⚙️ Configuración\n\n"
        "🚧 Esta función estará disponible próximamente."
    )