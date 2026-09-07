# =====================================================
# ENVIO DE ALERTAS A DISCORD (manada-bot, salida de voz)
# =====================================================
# Mismo patron que services/whatsapp.py: nunca lanza excepcion, para
# que un fallo aqui no afecte a Telegram (canal principal) ni a
# WhatsApp.

import requests

from config import DISCORD_INGEST_URL, DISCORD_INGEST_TOKEN


def enviar_alerta_discord(
    *,
    tipo: str,
    descripcion: str | None,
    lat: float | None,
    lon: float | None,
    calle: str | None = None,
    ciudad: str | None = None,
    reportado_por: str | None,
    id_rrm: int,
) -> bool:
    """Manda una alerta nueva al servidor de ingesta de manada-bot.
    `calle`/`ciudad` vienen del mismo dict de geocoder.py que ya usa
    handlers/comentario.py — no se vuelve a geocodificar aqui.
    Devuelve False (sin lanzar excepcion) si falta configuracion o si
    el envio falla por cualquier motivo."""

    if not DISCORD_INGEST_URL:
        return False

    url = f"{DISCORD_INGEST_URL}/alerta"

    try:
        r = requests.post(
            url,
            json={
                "tipo": tipo,
                "descripcion": descripcion,
                "lat": lat,
                "lon": lon,
                "calle": calle,
                "ciudad": ciudad,
                "reportado_por": reportado_por,
                "id_rrm": id_rrm,
            },
            headers={"X-Manada-Token": DISCORD_INGEST_TOKEN},
            timeout=5,
        )
        return r.ok
    except requests.RequestException:
        return False


def retirar_alerta_discord(id_rrm: int) -> bool:
    """Avisa a manada-bot de que una alerta ya publicada se retiro
    (caducada o descartada por moderacion). Devuelve False (sin
    lanzar excepcion) si falta configuracion o si el envio falla."""

    if not DISCORD_INGEST_URL:
        return False

    url = f"{DISCORD_INGEST_URL}/retirada"

    try:
        r = requests.post(
            url,
            json={"id_rrm": id_rrm},
            headers={"X-Manada-Token": DISCORD_INGEST_TOKEN},
            timeout=5,
        )
        return r.ok
    except requests.RequestException:
        return False
