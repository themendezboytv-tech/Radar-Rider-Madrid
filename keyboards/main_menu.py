from telegram import ReplyKeyboardMarkup


def get_main_menu():

    keyboard = [
        ["🚨 Nuevo aviso"],
        ["📍 Avisos cerca", "🗺️ Ver mapa"],
        ["📊 Estadísticas", "⚙️ Configuración"],
        ["ℹ️ Acerca de", "📜 Normas"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        input_field_placeholder="Selecciona una opción..."
    )
