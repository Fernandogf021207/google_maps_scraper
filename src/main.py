from src.scraping.maps_scraper import init_driver, search_google_maps, scrape_business_details
from src.database.supabase import save_business_to_supabase
from src.utils.logger import logger
import time

def main():
    query = "negocios en Gustavo A. Madero, Ciudad de México"
    max_results = 10  # ajusta esto para más resultados

    logger.info("Inicializando navegador...")
    driver = init_driver()

    try:
        logger.info(f"Buscando: {query}")
        results = search_google_maps(driver, query, max_results=max_results)

        logger.info(f"{len(results)} resultados obtenidos. Extrayendo detalles...")

        for i, result in enumerate(results, 1):
            maps_url = result["maps_url"]
            logger.info(f"[{i}/{len(results)}] Procesando: {maps_url}")

            try:
                details = scrape_business_details(maps_url, driver)
                if not details.get("place_id"):
                    logger.warning("No se encontró place_id, se omite el negocio.")
                    continue

                response = save_business_to_supabase(details)
                logger.info(f"Guardado exitosamente en Supabase: {details['name']}")
                time.sleep(3)

            except Exception as e:
                logger.error(f"Error procesando {maps_url}: {e}")
                continue

    finally:
        driver.quit()
        logger.info("Proceso finalizado.")

if __name__ == "__main__":
    main()
