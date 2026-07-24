from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def get_aviso_menu():

    keyboard = [
        ["🚨 Alerta Vial", "🚧 Calle cortada"],
        ["🚦 Tráfico", "🚑 Accidente"],
        ["⚠️ Peligro", "📦 Otro"],
        ["⬅️ Volver"],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Selecciona el tipo de aviso...",
    )


def get_location_menu():

    keyboard = [
        [
            KeyboardButton(
                text="📍 Compartir ubicación",
                request_location=True,
            )
        ],
        [
            KeyboardButton(
                text="❌ Cancelar"
            )
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Comparte tu ubicación...",
    )