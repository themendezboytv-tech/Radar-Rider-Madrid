from collections import Counter

from telegram import Update
from telegram.ext import ContextTypes

from database.database import (
    contar_avisos_usuario,
    obtener_avisos_por_usuario,
    obtener_avisos_activos,
)


async def estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    total_usuario = contar_avisos_usuario(user_id)

    if total_usuario:
        avisos_usuario = obtener_avisos_por_usuario(user_id, limite=total_usuario)
        tipo_mas_frecuente = Counter(a["tipo"] for a in avisos_usuario).most_common(1)[0][0]
    else:
        tipo_mas_frecuente = "—"

    total_activos = len(obtener_avisos_activos())

    mensaje = (
        "📊 *Tus estadísticas*\n\n"
        f"📝 Avisos publicados por ti: *{total_usuario}*\n"
        f"🏷️ Tipo más frecuente: *{tipo_mas_frecuente}*\n\n"
        f"🚨 Avisos activos ahora mismo: *{total_activos}*"
    )

    await update.message.reply_text(
        mensaje,
        parse_mode="Markdown",
    )
