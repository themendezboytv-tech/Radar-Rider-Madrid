from telegram import Update
from telegram.ext import ContextTypes

from database.database import marcar_como_falso


async def votar_falso(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    aviso_id = int(query.data.split(":")[1])

    marcar_como_falso(aviso_id)

    await query.answer("Voto registrado. ¡Gracias por ayudar a mantener el canal fiable!")
