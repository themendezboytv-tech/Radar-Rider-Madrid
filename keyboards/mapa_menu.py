from telegram import ReplyKeyboardMarkup


def get_mapa_menu():

    keyboard = [
        ["🖼️ Mapa rápido", "🌐 Mapa interactivo"],
        ["⬅️ Volver"],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Elige el tipo de mapa...",
    )
