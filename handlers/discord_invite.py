import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from services.discord import crear_invitacion_discord


async def discord_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Restringido a ADMIN_USER_ID, igual que /chatid: si no coincide (o
    # no esta configurado), no responde nada - ni siquiera confirma que
    # el comando existe.
    if update.effective_user.id != ADMIN_USER_ID:
        return

    url = await asyncio.to_thread(crear_invitacion_discord)

    if url is None:
        await update.message.reply_text(
            "❌ No pude generar la invitación de Discord. "
            "Revisa manada-bot (puede que falten permisos o esté caído)."
        )
        return

    await update.message.reply_text(
        "🔗 Invitación a Discord (un solo uso, caduca en 24h):\n"
        f"{url}"
    )
