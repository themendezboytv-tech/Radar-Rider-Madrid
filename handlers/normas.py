from telegram import Update
from telegram.ext import ContextTypes


async def normas(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = (
        "📜 *Normas de la comunidad*\n\n"
        "✅ Publica únicamente información real.\n\n"
        "✅ Utiliza comentarios cortos y claros.\n\n"
        "✅ No hagas spam.\n\n"
        "✅ Respeta a todos los miembros.\n\n"
        "✅ Si el aviso desaparece,\n"
        "comunícalo cuando sea posible.\n\n"
        "💙 Gracias por colaborar con\n"
        "*Radar Rider Madrid*."
    )

    await update.message.reply_text(
        mensaje,
        parse_mode="Markdown",
    )