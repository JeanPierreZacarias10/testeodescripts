import os
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
from datetime import datetime
from time import sleep

# Fecha y hora actual
now = datetime.now()

# Lista para almacenar los productos
lista_productos = []

# Configuración del driver
service_obj = Service("/usr/bin/chromedriver")  # Ruta adaptada para GitHub Actions
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo headless para entornos sin GUI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service_obj, options=chrome_options)

# Crear carpeta para guardar los resultados
output_folder = "archivosscripts"
os.makedirs(output_folder, exist_ok=True)

# Número de páginas a recorrer
cantidad_paginas = 10

# Scraping de las páginas
for x in range(1, cantidad_paginas + 1):
    driver.get(f"https://www.tiendaclaro.pe/personas/catalogo-celulares/liberados?page={x}")
    sleep(2)
    
    # Scroll para cargar productos
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(1, last_height, 100):  # Incremento ajustado para reducir el tiempo de scroll
        driver.execute_script("window.scrollBy(0, 100);")
        sleep(0.2)

    productos = driver.find_elements(By.CLASS_NAME, "vtex-product-summary-2-x-container")

    for prd in productos:
        # Verificar si el producto está agotado
        try:
            fuera_stock_element = prd.find_element(By.CLASS_NAME, "claroperupoc-claro-product-card-detail-app-0-x-label_texto_agotado").text
        except NoSuchElementException:
            fuera_stock_element = ""

        try:
            gris_class_element = prd.find_element(By.CLASS_NAME, "claroperupoc-claro-product-card-detail-app-0-x-product_stock_container").text
        except NoSuchElementException:
            gris_class_element = ""

        # Extraer precio
        try:
            precio = prd.find_element(By.CLASS_NAME, "claroperupoc-claro-product-card-detail-app-0-x-product_normal_price").text
            precio_texto_corregido = precio.replace("S/", "").strip()
        except (NoSuchElementException, StaleElementReferenceException):
            precio_texto_corregido = ""

        # Filtrar productos no disponibles
        if fuera_stock_element == "AGOTADO" or gris_class_element == "Quedan 0 unidades" or precio_texto_corregido == "":
            continue

        # Extraer información del producto
        enlace = prd.find_element(By.TAG_NAME, "a").get_attribute("href")
        codigo = enlace.split('skuId=')[1]
        titulo = prd.find_element(By.CLASS_NAME, "claroperupoc-claro-product-card-detail-app-0-x-product_name_container").text
        marca = prd.find_element(By.CLASS_NAME, "claroperupoc-claro-product-card-detail-app-0-x-product_brand_content").text

        # Almacenar la información en el diccionario
        producto_info = {
            'Pagina': str(x),
            'Plataforma': 'CLARO',
            'Tipo': 'CELULARES',
            'Fecha': now.date(),
            'Hora': now.time(),
            'Titulo': titulo.upper(),
            'Marca': marca.upper(),
            'Enlace': enlace,
            'Precio Tarjeta': '',
            'Precio Internet': precio_texto_corregido,
            'Precio Internet2': '',
            'Precio Lista': '',
            'Precio Lista2': '',
            'Envío Gratis': 'No',
            'Cuotas sin Interes': '',
            'Vendedor': 'CLARO',
            'Codigo': codigo
        }
        lista_productos.append(producto_info)

# Guardar los datos en un archivo CSV
output_file = os.path.join(output_folder, f'productos-CLARO-Celulares-{now.date()}.csv')
df = pd.DataFrame(lista_productos)
df.to_csv(output_file, encoding='latin1', index=False)
print(f"Archivo guardado en: {output_file}")

# Finalizar el driver
driver.quit()
