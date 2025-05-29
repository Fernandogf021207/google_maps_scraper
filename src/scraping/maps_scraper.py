from typing import List, Dict
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from src.scraping.utils import clean_text

GOOGLE_MAPS_URL = "https://www.google.com/maps"

def init_driver(headless: bool = True):
    """Inicializa el navegador con Selenium."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    return driver


def search_google_maps(driver, query: str) -> List[Dict]:
    """Realiza una búsqueda en Google Maps y devuelve resultados básicos."""
    driver.get(GOOGLE_MAPS_URL)
    time.sleep(3)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    scroll_results_panel(driver)

    businesses = []

    listings = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")

    for listing in listings:
        try:
            name = listing.find_element(By.CSS_SELECTOR, "div.qBF1Pd").text
            category = listing.find_element(By.CSS_SELECTOR, "div.W4Efsd span[jscontroller]").text
            maps_url = listing.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            businesses.append({
                "name": clean_text(name),
                "category": clean_text(category),
                "maps_url": maps_url,
            })
        except Exception:
            continue

    return businesses


def scroll_results_panel(driver, scroll_count: int = 10):
    """Simula scroll en la barra lateral de resultados para cargar más negocios."""
    try:
        scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf")
        for _ in range(scroll_count):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(1.5)
    except Exception as e:
        print(f"[ERROR] No se pudo hacer scroll: {e}")

def scrape_business_details(maps_url: str, driver) -> Dict:
    """
    Abre la página de un negocio en Google Maps y extrae detalles clave.
    """
    driver.get(maps_url)
    time.sleep(5)

    business = {
        "maps_url": maps_url,
        "place_id": None,
        "name": None,
        "phone": None,
        "email": None,
        "website": None,
        "address": None,
        "neighborhood": None,
        "category": None,
        "rating": None,
        "review_count": None,
    }

    try:
        # Nombre del negocio
        name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob").text
        business["name"] = clean_text(name)

        # Categoría
        category = driver.find_element(By.CSS_SELECTOR, "button.DkEaL").text
        business["category"] = clean_text(category)

        # Dirección
        address = extract_detail_text(driver, "Dirección:")
        business["address"] = address

        # Teléfono
        phone = extract_detail_text(driver, "Teléfono:")
        business["phone"] = phone

        # Sitio web
        website = extract_detail_text(driver, "Sitio web:")
        business["website"] = website

        # Calificación
        rating = driver.find_element(By.CSS_SELECTOR, "div.F7nice span span").text
        business["rating"] = float(rating.replace(",", "."))

        # Reseñas
        reviews = driver.find_element(By.CSS_SELECTOR, "span.UY7F9").text
        review_count = ''.join(filter(str.isdigit, reviews))
        business["review_count"] = int(review_count)

        # ID de lugar (usamos URL como fuente indirecta)
        if "placeid=" in maps_url:
            business["place_id"] = maps_url.split("placeid=")[1].split("&")[0]

    except Exception as e:
        print(f"[!] Error al extraer detalles: {e}")

    return business


def extract_detail_text(driver, label: str) -> str:
    """
    Busca el texto asociado a un ícono específico como Teléfono, Dirección, Sitio web.
    """
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "div.QSFF4-text.gm2-body-2")
        for el in elements:
            if label in el.text:
                return el.text.replace(label, '').strip()
    except Exception:
        return None
