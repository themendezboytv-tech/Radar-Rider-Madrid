from telegram import Update
from telegram.ext import ContextTypes

from keyboards.aviso_menu import get_location_menu
from keyboards.configuracion_menu import (
    get_menu_configuracion,
    get_configuracion_menu,
    get_radio_menu,
)
from handlers.menu_principal import mostrar_menu

from database.database import (
    obtener_config_notificaciones,
    activar_notificaciones,
    desactivar_notificaciones as db_desactivar_notificaciones,
)

RADIOS_DISPONIBLES = {"2 km": 2, "5 km": 5, "10 km": 10}


# =====================================================
# SUBMENÚ DE CONFIGURACIÓN (v1.9.2)
# =====================================================
# Punto de entrada desde el menú principal. Notificaciones, Acerca
# de, Ayuda y Normas cuelgan de aquí.

async def menu_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "⚙️ Configuración",
        reply_markup=get_menu_configuracion(),
    )


# =====================================================
# NOTIFICACIONES: ESTADO ACTUAL Y ACTIVAR/DESACTIVAR
# =====================================================

async def configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    fila = obtener_config_notificaciones(update.effective_user.id)

    if fila and fila["radio_notificacion_km"]:
        estado = f"✅ Activadas (radio {fila['radio_notificacion_km']:.0f} km)"
    else:
        estado = "🔕 Desactivadas"

    await update.message.reply_text(
        "⚙️ Configuración\n\n"
        f"📍 Notificaciones cerca de mí: {estado}",
        reply_markup=get_configuracion_menu(),
    )


# =====================================================
# ACTIVAR: PASO 1 - PEDIR UBICACIÓN DE REFERENCIA
# =====================================================

async def pedir_ubicacion_notificacion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()
    context.user_data["configurando_notificaciones"] = True

    await update.message.reply_text(
        "📍 Comparte la ubicación desde la que quieres recibir avisos cerca.",
        reply_markup=get_location_menu(),
    )


# =====================================================
# ACTIVAR: PASO 2 - PEDIR RADIO
# =====================================================

async def pedir_radio_notificacion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    latitud: float,
    longitud: float,
):

    context.user_data["lat_notificacion"] = latitud
    context.user_data["lon_notificacion"] = longitud
    context.user_data["esperando_radio_notificacion"] = True

    await update.message.reply_text(
        "📏 ¿En qué radio quieres recibir avisos?",
        reply_markup=get_radio_menu(),
    )


# =====================================================
# ACTIVAR: PASO 3 - GUARDAR RADIO
# =====================================================

async def recibir_radio_notificacion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = update.message.text.strip()

    if texto not in RADIOS_DISPONIBLES:

        await update.message.reply_text(
            "⚠️ Elige uno de los radios del teclado."
        )

        return

    radio_km = RADIOS_DISPONIBLES[texto]

    lat = context.user_data.get("lat_notificacion")
    lon = context.user_data.get("lon_notificacion")

    usuario = update.effective_user

    activar_notificaciones(
        user_id=usuario.id,
        username=usuario.username or usuario.first_name,
        lat=lat,
        lon=lon,
        radio_km=radio_km,
    )

    context.user_data.clear()

    await update.message.reply_text(
        f"✅ Notificaciones activadas.\n\n"
        f"Te avisaremos de los avisos publicados a menos de {radio_km} km "
        "de tu ubicación de referencia."
    )

    await mostrar_menu(update, context)


# =====================================================
# DESACTIVAR
# =====================================================

async def desactivar_notificaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):

    db_desactivar_notificaciones(update.effective_user.id)

    context.user_data.clear()

    await update.message.reply_text("🔕 Notificaciones desactivadas.")

    await mostrar_menu(update, context)
