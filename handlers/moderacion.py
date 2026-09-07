import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from database.database import marcar_como_falso, confirmar_aviso
from services.discord import retirar_alerta_discord


async def votar_falso(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    aviso_id = int(query.data.split(":")[1])

    se_retiro = marcar_como_falso(aviso_id)

    if se_retiro:
        await asyncio.to_thread(retirar_alerta_discord, aviso_id)

    await query.answer("Voto registrado. ¡Gracias por ayudar a mantener el canal fiable!")


async def votar_confirmado(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    aviso_id = int(query.data.split(":")[1])

    confirmar_aviso(aviso_id)

    await query.answer("✅ Confirmado, gracias")
