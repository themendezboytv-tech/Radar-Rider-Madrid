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
        from staticmap import StaticMap, CircleMarker
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

        for aviso in avisos:

            marcador = CircleMarker(
                (aviso["longitud"], aviso["latitud"]),
                _color_para(aviso["tipo"]),
                14,
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

            folium.CircleMarker(
                location=[aviso["latitud"], aviso["longitud"]],
                radius=10,
                color=_color_para(aviso["tipo"]),
                fill=True,
                fill_color=_color_para(aviso["tipo"]),
                fill_opacity=0.9,
                popup=folium.Popup(popup_texto, max_width=250),
            ).add_to(mapa)

        ruta = os.path.join(
            tempfile.gettempdir(),
            f"rrm_mapa_{uuid.uuid4().hex}.html",
        )

        mapa.save(ruta)

        return ruta

    except Exception:
        return None
