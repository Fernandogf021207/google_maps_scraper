from typing import Dict, Any

def calculate_prospect_priority(data: Dict[str, Any]) -> int:
    """
    Calcula la prioridad del prospecto con base en criterios definidos.
    Retorna un número entre 1 (baja prioridad) y 5 (muy alta prioridad).
    """

    has_website = data.get("has_website", False)
    phone = data.get("phone")
    email = data.get("email")
    category = data.get("category", "").lower()
    rating = data.get("rating", 0)
    review_count = data.get("review_count", 0)

    # Criterios de categoría alta (negocios con presencia digital clave)
    high_value_categories = [
        "restaurante", "cafetería", "clínica", "consultorio", "spa",
        "escuela", "tienda", "boutique", "gimnasio", "salón de belleza", "hotel"
    ]

    score = 0

    # 🕸️ Sitio web
    if not has_website:
        score += 2
    else:
        score += 0

    # 📞 Contacto directo
    if phone or email:
        score += 1

    # 🌟 Relevancia por categoría
    if any(cat in category for cat in high_value_categories):
        score += 1

    # ⭐ Actividad en Google Maps
    if rating and review_count:
        if rating >= 4.0 and review_count >= 10:
            score += 1

    # Escala final de prioridad (máximo 5)
    priority = min(score, 5)
    return max(priority, 1)
