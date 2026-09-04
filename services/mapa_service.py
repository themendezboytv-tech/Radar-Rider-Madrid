import os
import tempfile
import uuid

# =====================================================
# COLORES POR TIPO DE AVISO
# =====================================================
# Mismo criterio de tipos que database.py (EXPIRACION_MINUTOS),
# para que el color en el mapa sea consistente con el resto
# del bot.

COLOR_POR_TIPO = {
    "🚓 Presencia policial": "#1565C0",
    "🚧 Calle cortada": "#F9A825",
    "🚦 Tráfico": "#EF6C00",
    "🚑 Accidente": "#C62828",
    "⚠️ Peligro": "#6A1B9A",
    "📦 Otro": "#546E7A",
}

COLOR_DEFECTO = "#546E7A"

# =====================================================
# USER-AGENT PARA TILES DE OPENSTREETMAP
# =====================================================
# La politica de uso de tiles de OSM (operations.osmfoundation.org/policies/tiles)
# exige un User-Agent identificable con forma de contactar al operador.
# Sin esto, tile.openstreetmap.org responde 403 "Access blocked" (bloquea el
# User-Agent generico de requests/urllib). Referencia = URL del repo, para no
# exponer un email personal en un repo publico.
OSM_TILE_USER_AGENT = (
    "RadarRiderMadrid/1.5 "
    "(+https://github.com/themendezboytv-tech/Radar-Rider-Madrid)"
)


def _color_para(tipo: str) -> str:
    return COLOR_POR_TIPO.get(tipo, COLOR_DEFECTO)


# =====================================================
# FORMAS POR TIPO DE AVISO (mapa imagen, v1.9.1)
# =====================================================
# staticmap es mas limitado que folium: CircleMarker solo admite
# color/radio, sin iconos. Su IconMarker si admite una imagen
# cualquiera, asi que en vez de agregar una libreria de iconos
# (dependencia pesada) se dibuja una FORMA simple por tipo con PIL
# (ya es dependencia del proyecto) manteniendo el mismo color de
# COLOR_POR_TIPO - el color no se toca, la forma es el diferenciador
# extra.

FORMA_POR_TIPO = {
    "🚓 Presencia policial": "circulo",
    "🚧 Calle cortada": "cuadrado",
    "🚦 Tráfico": "rombo",
    "🚑 Accidente": "cruz",
    "⚠️ Peligro": "triangulo",
    "📦 Otro": "hexagono",
}

FORMA_DEFECTO = "hexagono"

ICONO_TAM = 28


def _generar_icono_marcador(tipo: str) -> str:
    """
    Genera (o reutiliza, si ya existe con ese nombre) un PNG pequeño
    con la forma correspondiente al tipo, relleno con su color de
    COLOR_POR_TIPO. Devuelve la ruta del archivo para pasarla a
    IconMarker.
    """

    import math
    from PIL import Image, ImageDraw

    color = _color_para(tipo)
    forma = FORMA_POR_TIPO.get(tipo, FORMA_DEFECTO)

    ruta = os.path.join(
        tempfile.gettempdir(),
        f"rrm_icono_{forma}_{color.lstrip('#')}.png",
    )

    if os.path.exists(ruta):
        return ruta

    tam = ICONO_TAM
    margen = 2

    img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if forma == "circulo":

        draw.ellipse([margen, margen, tam - margen, tam - margen], fill=color, outline="white", width=2)

    elif forma == "cuadrado":

        draw.rectangle([margen, margen, tam - margen, tam - margen], fill=color, outline="white", width=2)

    elif forma == "rombo":

        centro = tam / 2

        draw.polygon(
            [(centro, margen), (tam - margen, centro), (centro, tam - margen), (margen, centro)],
            fill=color,
            outline="white",
        )

    elif forma == "triangulo":

        draw.polygon(
            [(tam / 2, margen), (tam - margen, tam - margen), (margen, tam - margen)],
            fill=color,
            outline="white",
        )

    elif forma == "cruz":

        ancho = tam * 0.34

        draw.rectangle([tam / 2 - ancho / 2, margen, tam / 2 + ancho / 2, tam - margen], fill=color)
        draw.rectangle([margen, tam / 2 - ancho / 2, tam - margen, tam / 2 + ancho / 2], fill=color)

    else:  # hexágono ("Otro" y cualquier tipo desconocido)

        centro = tam / 2
        radio = centro - margen

        puntos = [
            (
                centro + radio * math.cos(math.radians(60 * i - 30)),
                centro + radio * math.sin(math.radians(60 * i - 30)),
            )
            for i in range(6)
        ]

        draw.polygon(puntos, fill=color, outline="white")

    img.save(ruta)

    return ruta


# =====================================================
# MAPA COMO IMAGEN (staticmap)
# =====================================================

def generar_mapa_imagen(avisos):
    """
    Genera un PNG con un marcador por cada aviso activo,
    usando tiles de OpenStreetMap. Devuelve la ruta del
    archivo generado, o None si algo falla (ej. sin internet
    o la librería no está instalada).
    """

    try:
        from staticmap import StaticMap, IconMarker
        from PIL import Image

        # staticmap 0.5.x llama a Image.ANTIALIAS, que Pillow quito en
        # la version 10 (renombrado a Image.LANCZOS). Sin este shim,
        # generar_mapa_imagen() falla siempre con Pillow >= 10.
        if not hasattr(Image, "ANTIALIAS"):
            Image.ANTIALIAS = Image.LANCZOS
    except ImportError:
        return None

    try:

        mapa = StaticMap(
            700,
            500,
            url_template="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            headers={"User-Agent": OSM_TILE_USER_AGENT},
            tile_request_timeout=10,
        )

        iconos_por_tipo = {}

        for aviso in avisos:

            tipo = aviso["tipo"]

            if tipo not in iconos_por_tipo:
                iconos_por_tipo[tipo] = _generar_icono_marcador(tipo)

            marcador = IconMarker(
                (aviso["longitud"], aviso["latitud"]),
                iconos_por_tipo[tipo],
                ICONO_TAM // 2,
                ICONO_TAM // 2,
            )

            mapa.add_marker(marcador)

        imagen = mapa.render()

        ruta = os.path.join(
            tempfile.gettempdir(),
            f"rrm_mapa_{uuid.uuid4().hex}.png",
        )

        imagen.save(ruta)

        return ruta

    except Exception:
        return None


# =====================================================
# ÍCONOS POR TIPO DE AVISO (mapa interactivo, v1.9.1)
# =====================================================
# folium.Icon usa nombres de Font Awesome 4 (prefix="fa") y una
# paleta de colores fija propia (no acepta hex, a diferencia de
# CircleMarker) - por eso es un mapeo aparte de COLOR_POR_TIPO.

ICONO_POR_TIPO = {
    "🚓 Presencia policial": ("car", "blue"),
    "🚧 Calle cortada": ("road", "beige"),
    "🚦 Tráfico": ("car", "orange"),
    "🚑 Accidente": ("ambulance", "red"),
    "⚠️ Peligro": ("exclamation-triangle", "purple"),
    "📦 Otro": ("info-circle", "gray"),
}

ICONO_DEFECTO = ("info-circle", "gray")


def _icono_para(tipo: str) -> tuple:
    return ICONO_POR_TIPO.get(tipo, ICONO_DEFECTO)


# =====================================================
# MAPA INTERACTIVO (folium / Leaflet)
# =====================================================

def generar_mapa_html(avisos):
    """
    Genera un archivo HTML autocontenido con un mapa Leaflet
    (vía folium) y un marcador por cada aviso activo, con
    popup mostrando tipo, calle y comentario al tocarlo.
    Devuelve la ruta del archivo, o None si algo falla.
    """

    try:
        import folium
    except ImportError:
        return None

    try:

        lat_promedio = sum(a["latitud"] for a in avisos) / len(avisos)
        lon_promedio = sum(a["longitud"] for a in avisos) / len(avisos)

        mapa = folium.Map(
            location=[lat_promedio, lon_promedio],
            zoom_start=13,
        )

        for aviso in avisos:

            popup_texto = f"<b>{aviso['tipo']}</b><br>"

            if aviso["calle"]:

                popup_texto += f"{aviso['calle']}"

                if aviso["ciudad"]:
                    popup_texto += f", {aviso['ciudad']}"

                popup_texto += "<br>"

            if aviso["comentario"]:
                popup_texto += f"💬 {aviso['comentario']}"

            icono, color = _icono_para(aviso["tipo"])

            folium.Marker(
                location=[aviso["latitud"], aviso["longitud"]],
                popup=folium.Popup(popup_texto, max_width=250),
                icon=folium.Icon(color=color, icon=icono, prefix="fa"),
            ).add_to(mapa)

        ruta = os.path.join(
            tempfile.gettempdir(),
            f"rrm_mapa_{uuid.uuid4().hex}.html",
        )

        mapa.save(ruta)

        return ruta

    except Exception:
        return None
