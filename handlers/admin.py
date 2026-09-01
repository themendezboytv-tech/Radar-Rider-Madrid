from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Restringido a ADMIN_USER_ID: si no coincide (o no esta
    # configurado), no responde nada - ni siquiera confirma que el
    # comando existe.
    if update.effective_user.id != ADMIN_USER_ID:
        return

    await update.message.reply_text(
        f"ID: {update.effective_chat.id}\n"
        f"Tipo: {update.effective_chat.type}\n"
        f"Nombre: {update.effective_chat.title}"
    )
