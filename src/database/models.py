from typing import Dict, Any, Optional
from src.scraping.utils import get_nested_value


def build_business_payload(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte los datos crudos extraídos de Google Maps a un diccionario
    compatible con el modelo de la tabla 'cdmx_businesses'.
    """
    place_id = get_nested_value(raw_data, ["place_id"])
    name = get_nested_value(raw_data, ["name"])
    phone = get_nested_value(raw_data, ["phone"])
    email = get_nested_value(raw_data, ["email"])  # Puede que no siempre exista
    website = get_nested_value(raw_data, ["website"])
    address = get_nested_value(raw_data, ["address"])
    neighborhood = get_nested_value(raw_data, ["neighborhood"]) or extract_neighborhood(address)
    city = "Ciudad de México"
    category = get_nested_value(raw_data, ["category"])
    rating = get_nested_value(raw_data, ["rating"])
    review_count = get_nested_value(raw_data, ["review_count"])
    maps_url = get_nested_value(raw_data, ["maps_url"])

    has_website = bool(website)

    # Prioridad calculada 
    from src.utils.helpers import calculate_prospect_priority
    priority = calculate_prospect_priority({
        "has_website": has_website,
        "phone": phone,
        "email": email,
        "category": category,
        "rating": rating,
        "review_count": review_count,
    })

    return {
        "place_id": place_id,
        "name": name,
        "phone": phone,
        "email": email,
        "website": website,
        "has_website": has_website,
        "address": address,
        "neighborhood": neighborhood,
        "city": city,
        "category": category,
        "rating": rating,
        "review_count": review_count,
        "maps_url": maps_url,
        "prospect_priority": priority,
        "raw_data": raw_data,
    }


def extract_neighborhood(address: Optional[str]) -> Optional[str]:
    """
    Intenta extraer la colonia o barrio desde el texto de dirección.
    Esta función puede mejorarse más adelante con NLP o expresiones regulares.
    """
    if address:
        parts = address.split(",")
        if len(parts) >= 3:
            return parts[-3].strip()
    return None
