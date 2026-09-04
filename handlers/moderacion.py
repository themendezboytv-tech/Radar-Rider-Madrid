from telegram import Update
from telegram.ext import ContextTypes

from database.database import marcar_como_falso, confirmar_aviso


async def votar_falso(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    aviso_id = int(query.data.split(":")[1])

    marcar_como_falso(aviso_id)

    await query.answer("Voto registrado. ¡Gracias por ayudar a mantener el canal fiable!")


async def votar_confirmado(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    aviso_id = int(query.data.split(":")[1])

    confirmar_aviso(aviso_id)

    await query.answer("✅ Confirmado, gracias")
