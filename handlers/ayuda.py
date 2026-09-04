from telegram import Update
from telegram.ext import ContextTypes


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = (
        "❓ CÓMO FUNCIONA RADAR RIDER MADRID\n\n"
        "🚨 Nuevo aviso\n"
        "Para avisar a los demás de algo en la calle (control policial, calle "
        "cortada, tráfico, accidente, peligro u otra cosa). Eliges el tipo, "
        "compartes tu ubicación, escribes un comentario corto (o pones \"-\" si no "
        "quieres escribir nada), y se publica automáticamente en el grupo/canal.\n\n"
        "📍 Avisos cerca\n"
        "Te muestra los avisos activos que hay cerca de ti ahora mismo, "
        "compartiendo tu ubicación. Útil antes de salir a la calle.\n\n"
        "🗺️ Ver mapa\n"
        "Ve todos los avisos activos en un mapa. Puedes elegir una imagen rápida "
        "(se ve directo en el chat) o un mapa interactivo con zoom (se abre en tu "
        "navegador).\n\n"
        "📊 Estadísticas\n"
        "Muestra cuántos avisos has publicado tú, cuál es el tipo que más "
        "reportas, y cuántos avisos hay activos en total ahora mismo.\n\n"
        "⚙️ Configuración\n"
        "Activa notificaciones para que el bot te avise por privado cuando alguien "
        "publique algo cerca de un lugar que tú elijas (por ejemplo, tu casa o tu "
        "zona de trabajo).\n\n"
        "👎 No es real / ✅ Confirmado\n"
        "Debajo de cada aviso publicado hay dos botones. Si ves que el aviso ya no "
        "aplica o es falso, toca \"👎 No es real\". Si confirmas que sí es cierto (lo "
        "viste con tus propios ojos), toca \"✅ Confirmado\". Ayuda a que la "
        "información sea confiable para todos.\n\n"
        "ℹ️ Acerca de / 📜 Normas\n"
        "Información sobre el proyecto y las reglas de uso de la comunidad."
    )

    await update.message.reply_text(mensaje)
