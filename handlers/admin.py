from telegram import Update
from telegram.ext import ContextTypes


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"ID: {update.effective_chat.id}\n"
        f"Tipo: {update.effective_chat.type}\n"
        f"Nombre: {update.effective_chat.title}"
    )