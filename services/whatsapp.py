# =====================================================
# ENVIO DE ALERTAS POR WHATSAPP (OpenWA)
# =====================================================
# Espejo del patron ya probado en
# ~/servers/wifi-hermano-bot/WiFi Hermano Bot v0.1/bot.py#enviar_whatsapp:
# nunca lanza excepcion, para que un fallo aqui no tumbe la publicacion
# en Telegram, que es el canal principal de este bot.

import requests

from config import (
    OPENWA_BASE_URL,
    OPENWA_API_KEY,
    OPENWA_SESSION_ID,
    WHATSAPP_ALERT_PHONE,
    WHATSAPP_GROUP_ID,
)


def enviar_alerta_whatsapp(mensaje: str) -> bool:
    """Manda `mensaje` por WhatsApp via OpenWA. Si WHATSAPP_GROUP_ID
    esta configurado se usa el grupo (tiene prioridad); si no, se usa
    el numero personal WHATSAPP_ALERT_PHONE. Devuelve False (sin
    lanzar excepcion) si falta configuracion o si el envio falla por
    cualquier motivo."""

    if WHATSAPP_GROUP_ID:
        chat_id = WHATSAPP_GROUP_ID
    elif WHATSAPP_ALERT_PHONE:
        chat_id = f"{WHATSAPP_ALERT_PHONE}@c.us"
    else:
        return False

    url = f"{OPENWA_BASE_URL}/api/sessions/{OPENWA_SESSION_ID}/messages/send-text"

    try:
        r = requests.post(
            url,
            json={"chatId": chat_id, "text": mensaje},
            headers={"X-API-Key": OPENWA_API_KEY},
            timeout=10,
        )
        return r.ok and bool(r.json().get("messageId"))
    except requests.RequestException:
        return False
