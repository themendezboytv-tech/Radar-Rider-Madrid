from telegram import ReplyKeyboardMarkup


def get_configuracion_menu():

    keyboard = [
        ["📍 Activar notificaciones cerca de mí"],
        ["🔕 Desactivar notificaciones"],
        ["⬅️ Volver"],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Selecciona una opción...",
    )


def get_radio_menu():

    keyboard = [
        ["2 km", "5 km", "10 km"],
        ["❌ Cancelar"],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Elige un radio...",
    )
