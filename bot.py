from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN

from database.database import init_db

from handlers.start import start
from handlers.menu_principal import mostrar_menu
from handlers.nuevo_aviso import (
    nuevo_aviso,
    pedir_ubicacion,
)
from handlers.ubicacion import recibir_ubicacion
from handlers.avisos_cerca import avisos_cerca
from handlers.comentario import recibir_comentario

from handlers.acerca import acerca
from handlers.normas import normas
from handlers.configuracion import configuracion
from handlers.estadisticas import estadisticas
from handlers.mapa import mapa


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text

    # ==========================================
    # CANCELAR / VOLVER
    # ==========================================
    # Estas dos opciones deben cortar cualquier flujo en curso
    # (incluido "esperando_comentario"), así que se comprueban
    # ANTES de mirar si estamos esperando un comentario. Si no,
    # pulsar "Cancelar" mientras se espera el comentario se
    # guardaba y publicaba como si "❌ Cancelar" fuera el
    # comentario real (bug detectado en las pruebas de v1.3).

    if texto == "❌ Cancelar":

        context.user_data.clear()

        await update.message.reply_text(
            "❌ Aviso cancelado correctamente."
        )

        await mostrar_menu(update, context)

        return

    elif texto == "⬅️ Volver":

        context.user_data.clear()

        await mostrar_menu(update, context)

        return

    # ==========================================
    # ESPERANDO COMENTARIO
    # ==========================================

    if context.user_data.get("esperando_comentario"):

        await recibir_comentario(update, context)
        return

    # ==========================================
    # MENÚ PRINCIPAL
    # ==========================================

    if texto == "🚨 Nuevo aviso":

        await nuevo_aviso(update, context)
        return

    elif texto == "📍 Avisos cerca":

        await avisos_cerca(update, context)
        return

    elif texto == "🗺️ Ver mapa":

        await mapa(update, context)
        return

    elif texto == "📊 Estadísticas":

        await estadisticas(update, context)
        return

    elif texto == "⚙️ Configuración":

        await configuracion(update, context)
        return

    elif texto == "ℹ️ Acerca de":

        await acerca(update, context)
        return

    elif texto == "📜 Normas":

        await normas(update, context)
        return

    # ==========================================
    # TIPOS DE AVISO
    # ==========================================

    elif texto == "🚨 Alerta Vial":

        context.user_data["tipo_aviso"] = "🚓 Presencia policial"

        await pedir_ubicacion(update, context)

        return

    elif texto in [

        "🚧 Calle cortada",
        "🚦 Tráfico",
        "🚑 Accidente",
        "⚠️ Peligro",
        "📦 Otro",

    ]:

        context.user_data["tipo_aviso"] = texto

        await pedir_ubicacion(update, context)

        return

    # ==========================================
    # MENSAJE DESCONOCIDO
    # ==========================================

    await update.message.reply_text(
        "⚠️ Utiliza los botones del menú."
    )


def main():

    # ==========================================
    # INICIALIZAR BASE DE DATOS
    # ==========================================
    # Crea las tablas si no existen. Idempotente: se puede
    # llamar en cada arranque sin problema.

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.LOCATION,
            recibir_ubicacion,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu,
        )
    )

    print("========================================")
    print("   RADAR RIDER MADRID INICIADO")
    print("========================================")

    app.run_polling()


if __name__ == "__main__":
    main()
