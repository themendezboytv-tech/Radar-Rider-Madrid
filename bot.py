from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN

from handlers.start import start
from handlers.menu_principal import mostrar_menu
from handlers.nuevo_aviso import (
    nuevo_aviso,
    pedir_ubicacion,
)
from handlers.ubicacion import recibir_ubicacion
from handlers.comentario import recibir_comentario

from handlers.acerca import acerca
from handlers.normas import normas
from handlers.configuracion import configuracion
from handlers.estadisticas import estadisticas
from handlers.mapa import mapa


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text

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

        await update.message.reply_text(
            "🚧 Disponible próximamente."
        )
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

        await update.message.reply_text(
            "🚧 Esta categoría estará disponible muy pronto.\n\n"
            "Actualmente estamos validando el sistema de Alertas Viales."
        )

        return

    # ==========================================
    # VOLVER
    # ==========================================

    elif texto == "⬅️ Volver":

        context.user_data.clear()

        await mostrar_menu(update, context)

        return

    # ==========================================
    # CANCELAR
    # ==========================================

    elif texto == "❌ Cancelar":

        context.user_data.clear()

        await update.message.reply_text(
            "❌ Aviso cancelado correctamente."
        )

        await mostrar_menu(update, context)

        return

    # ==========================================
    # MENSAJE DESCONOCIDO
    # ==========================================

    await update.message.reply_text(
        "⚠️ Utiliza los botones del menú."
    )


def main():

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