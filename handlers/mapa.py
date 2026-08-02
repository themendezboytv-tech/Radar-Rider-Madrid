from telegram import Update
from telegram.ext import ContextTypes

from keyboards.mapa_menu import get_mapa_menu
from handlers.menu_principal import mostrar_menu

from database.database import (
    expirar_avisos_vencidos,
    obtener_avisos_activos,
)

from services.mapa_service import (
    generar_mapa_imagen,
    generar_mapa_html,
)


# =====================================================
# SUBMENÚ: ELEGIR TIPO DE MAPA
# =====================================================
# v1.5 ofrece las dos variantes a la vez para que el equipo
# las pruebe y decidamos cuál se queda como definitiva más
# adelante (o si se dejan ambas).

async def mapa(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🗺️ *Mapa de avisos activos*\n\n"
        "¿Qué tipo de mapa quieres ver?",
        parse_mode="Markdown",
        reply_markup=get_mapa_menu(),
    )


# =====================================================
# OPCIÓN A: IMAGEN RÁPIDA
# =====================================================

async def mapa_imagen(update: Update, context: ContextTypes.DEFAULT_TYPE):

    expirar_avisos_vencidos()
    avisos = obtener_avisos_activos()

    if not avisos:

        await update.message.reply_text(
            "✅ No hay avisos activos para mostrar en el mapa."
        )

        await mostrar_menu(update, context)
        return

    await update.message.reply_text("🖼️ Generando mapa, un momento...")

    ruta_imagen = generar_mapa_imagen(avisos)

    if ruta_imagen is None:

        await update.message.reply_text(
            "⚠️ No se pudo generar el mapa ahora mismo. "
            "Intenta de nuevo en unos minutos."
        )

        await mostrar_menu(update, context)
        return

    with open(ruta_imagen, "rb") as foto:

        await update.message.reply_photo(
            photo=foto,
            caption=f"🗺️ {len(avisos)} aviso(s) activo(s) en el mapa.",
        )

    await mostrar_menu(update, context)


# =====================================================
# OPCIÓN B: MAPA INTERACTIVO
# =====================================================

async def mapa_html(update: Update, context: ContextTypes.DEFAULT_TYPE):

    expirar_avisos_vencidos()
    avisos = obtener_avisos_activos()

    if not avisos:

        await update.message.reply_text(
            "✅ No hay avisos activos para mostrar en el mapa."
        )

        await mostrar_menu(update, context)
        return

    await update.message.reply_text(
        "🌐 Generando mapa interactivo, un momento..."
    )

    ruta_html = generar_mapa_html(avisos)

    if ruta_html is None:

        await update.message.reply_text(
            "⚠️ No se pudo generar el mapa ahora mismo. "
            "Intenta de nuevo en unos minutos."
        )

        await mostrar_menu(update, context)
        return

    with open(ruta_html, "rb") as archivo:

        await update.message.reply_document(
            document=archivo,
            filename="mapa_avisos.html",
            caption=(
                f"🗺️ {len(avisos)} aviso(s) activo(s).\n\n"
                "Descarga el archivo y ábrelo con tu navegador "
                "para ver el mapa interactivo."
            ),
        )

    await mostrar_menu(update, context)
