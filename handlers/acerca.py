from telegram import Update
from telegram.ext import ContextTypes


async def acerca(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = (
        "🛵 *Radar Rider Madrid*\n\n"
        "Versión: *1.2*\n\n"
        "Una comunidad creada por repartidores,\n"
        "para repartidores.\n\n"
        "Nuestro objetivo es compartir\n"
        "avisos útiles en tiempo real\n"
        "para conducir mejor informados.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "👨‍💻 *Desarrollador*\n"
        "Themendezboy\n\n"
        "📨 Telegram\n"
        "https://t.me/themendezboy\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "💡 ¿Tienes una idea?\n"
        "Escríbeme por Telegram.\n\n"
        "Toda sugerencia ayuda a mejorar\n"
        "*Radar Rider Madrid* 🛵"
    )

    await update.message.reply_text(
        mensaje,
        parse_mode="Markdown",
    )