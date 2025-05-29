import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from supabase import Client
from datetime import datetime
from src.utils.helpers import calculate_prospect_priority
from src.config.settings import supabase as client

# Cargar variables de entorno desde .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("Faltan variables de entorno SUPABASE_URL o SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_or_update_business(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Inserta un nuevo negocio o actualiza uno existente según su 'place_id'.
    """
    place_id = data.get("place_id")
    if not place_id:
        raise ValueError("Falta 'place_id' en los datos del negocio.")

    # Verificar si ya existe un registro con el mismo place_id
    existing = supabase.table("cdmx_businesses").select("id").eq("place_id", place_id).execute()

    if existing.data:
        # Ya existe, se actualiza
        business_id = existing.data[0]["id"]
        response = supabase.table("cdmx_businesses").update(data).eq("id", business_id).execute()
        print(f"[SUPABASE] Negocio actualizado (ID: {business_id})")
        return response.data[0] if response.data else None
    else:
        # No existe, se inserta nuevo
        response = supabase.table("cdmx_businesses").insert(data).execute()
        print(f"[SUPABASE] Negocio insertado (place_id: {place_id})")
        return response.data[0] if response.data else None

def save_business_to_supabase(business_data: dict) -> dict:
    """
    Inserta o actualiza un negocio en la base de datos Supabase.
    Retorna el resultado de la operación.
    """
    place_id = business_data.get("place_id")
    if not place_id:
        raise ValueError("Falta el 'place_id' del negocio.")

    # Verifica si el negocio ya está en la base de datos
    existing = client.table("cdmx_businesses").select("id").eq("place_id", place_id).execute()

    # Calcula prioridad del prospecto
    business_data["has_website"] = bool(business_data.get("website"))
    business_data["prospect_priority"] = calculate_prospect_priority(business_data)
    business_data["last_updated"] = datetime.utcnow().isoformat()
    business_data["raw_data"] = business_data.copy()  # guarda todo en JSONB

    if existing.data:
        # Actualización
        business_id = existing.data[0]["id"]
        response = client.table("cdmx_businesses") \
            .update({
                "name": business_data.get("name"),
                "phone": business_data.get("phone"),
                "email": business_data.get("email"),
                "website": business_data.get("website"),
                "has_website": business_data.get("has_website"),
                "address": business_data.get("address"),
                "neighborhood": business_data.get("neighborhood"),
                "city": "Ciudad de México",
                "category": business_data.get("category"),
                "rating": business_data.get("rating"),
                "review_count": business_data.get("review_count"),
                "maps_url": business_data.get("maps_url"),
                "prospect_priority": business_data.get("prospect_priority"),
                "last_updated": business_data.get("last_updated"),
                "raw_data": business_data.get("raw_data")
            }) \
            .eq("id", business_id).execute()
    else:
        # Inserción
        response = client.table("cdmx_businesses").insert({
            "place_id": place_id,
            "name": business_data.get("name"),
            "phone": business_data.get("phone"),
            "email": business_data.get("email"),
            "website": business_data.get("website"),
            "has_website": business_data.get("has_website"),
            "address": business_data.get("address"),
            "neighborhood": business_data.get("neighborhood"),
            "city": "Ciudad de México",
            "category": business_data.get("category"),
            "rating": business_data.get("rating"),
            "review_count": business_data.get("review_count"),
            "maps_url": business_data.get("maps_url"),
            "prospect_priority": business_data.get("prospect_priority"),
            "raw_data": business_data.get("raw_data"),
        }).execute()

    return response
