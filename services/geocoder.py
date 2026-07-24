from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# =====================================================
# GEOCODER
# =====================================================

geolocator = Nominatim(
    user_agent="ASR-Bot"
)


def obtener_direccion(latitud: float, longitud: float):

    """
    Devuelve un diccionario con la dirección obtenida
    desde OpenStreetMap.
    """

    try:

        location = geolocator.reverse(

            (latitud, longitud),

            exactly_one=True,

            language="es",

        )

        if location is None:

            return None

        data = location.raw.get("address", {})

        calle = (
            data.get("road")
            or data.get("pedestrian")
            or data.get("footway")
            or data.get("cycleway")
            or data.get("path")
            or data.get("residential")
            or data.get("suburb")
            or ""
        )

        numero = data.get("house_number", "")

        ciudad = (
            data.get("city")
            or data.get("town")
            or data.get("village")
            or data.get("municipality")
            or ""
        )

        provincia = (
            data.get("state")
            or ""
        )

        codigo_postal = (
            data.get("postcode")
            or ""
        )

        pais = (
            data.get("country")
            or ""
        )

        return {

            "calle": calle,

            "numero": numero,

            "ciudad": ciudad,

            "provincia": provincia,

            "codigo_postal": codigo_postal,

            "pais": pais,

            "maps": f"https://maps.google.com/?q={latitud},{longitud}",

        }

    except (GeocoderTimedOut, GeocoderServiceError):

        return None

    except Exception:

        return None