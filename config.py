# =====================================================
# ASR BOT - CONFIGURACIÓN
# =====================================================

import os

from dotenv import load_dotenv

load_dotenv()

# =====================================================
# TOKEN DEL BOT
# =====================================================

TOKEN = os.getenv("TOKEN")

# =====================================================
# GRUPO OFICIAL
# =====================================================

GROUP_ID = int(os.getenv("GROUP_ID"))

# =====================================================
# CANAL OFICIAL
# =====================================================

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Compatibilidad con versiones anteriores
GROUP_CHAT_ID = GROUP_ID

# =====================================================
# ADMIN (comandos restringidos, ej. /chatid)
# =====================================================
# Si se deja vacio, /chatid no responde a nadie.

_admin_user_id = os.getenv("ADMIN_USER_ID")
ADMIN_USER_ID = int(_admin_user_id) if _admin_user_id else None

# =====================================================
# WHATSAPP (OpenWA, gateway self-hosted)
# =====================================================
# Para cambiar de sesion: edita OPENWA_SESSION_ID (y pide una clave
# operador con allowedSessions al UUID nuevo). Si WHATSAPP_ALERT_PHONE
# esta vacio, el envio por WhatsApp simplemente se omite.

OPENWA_BASE_URL = os.getenv("OPENWA_BASE_URL")
OPENWA_API_KEY = os.getenv("OPENWA_API_KEY")
OPENWA_SESSION_ID = os.getenv("OPENWA_SESSION_ID")
WHATSAPP_ALERT_PHONE = os.getenv("WHATSAPP_ALERT_PHONE")

# WHATSAPP_GROUP_ID (formato "1234567890-1234567890@g.us"): si se
# define, el envio usa el grupo en vez del numero personal
# (WHATSAPP_ALERT_PHONE). Vacio por defecto - capacidad lista pero
# sin activar hasta tener el ID real del grupo.
WHATSAPP_GROUP_ID = os.getenv("WHATSAPP_GROUP_ID")

# WHATSAPP_GROUP_ID_TEST: grupo de WhatsApp de pruebas (mientras se
# valida el formato de las alertas antes de activar el grupo real).
# Tiene prioridad MENOR que WHATSAPP_GROUP_ID: en cuanto este ultimo
# tenga valor, se usa el grupo real sin tocar codigo.
WHATSAPP_GROUP_ID_TEST = os.getenv("WHATSAPP_GROUP_ID_TEST")

# =====================================================
# NOMBRE DEL BOT
# =====================================================

BOT_NAME = "Radar Rider Madrid 🛵"

# =====================================================
# VERSIÓN
# =====================================================

VERSION = "1.9.0"