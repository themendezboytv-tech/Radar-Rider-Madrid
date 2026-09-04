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
)


def enviar_alerta_whatsapp(mensaje: str) -> bool:
    """Manda `mensaje` por WhatsApp al numero WHATSAPP_ALERT_PHONE via
    OpenWA. Devuelve False (sin lanzar excepcion) si falta configuracion
    o si el envio falla por cualquier motivo."""

    if not WHATSAPP_ALERT_PHONE:
        return False

    url = f"{OPENWA_BASE_URL}/api/sessions/{OPENWA_SESSION_ID}/messages/send-text"

    try:
        r = requests.post(
            url,
            json={"chatId": f"{WHATSAPP_ALERT_PHONE}@c.us", "text": mensaje},
            headers={"X-API-Key": OPENWA_API_KEY},
            timeout=10,
        )
        return r.ok and bool(r.json().get("messageId"))
    except requests.RequestException:
        return False
