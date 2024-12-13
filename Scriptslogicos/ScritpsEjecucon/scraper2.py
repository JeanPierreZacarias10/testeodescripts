import os
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

# URL inicial
driver.get("https://miportal.entel.pe/personas/catalogo/liberados")
sleep(5)
pagina = 1
color = "#002EFF"

# Función para extraer productos
def extraer_productos():
    productos = driver.find_elements(By.CLASS_NAME, "card-plp")
    for prd in productos:
        # Verificar si está fuera de stock
        try:
            gris_class_element = prd.find_element(By.CLASS_NAME, "card-plp__gris")
            continue
        except NoSuchElementException:
            pass  # No está agotado

        # Extraer información del producto
        try:
            titulo = prd.find_element(By.CLASS_NAME, "product-name").text
            marca = prd.find_element(By.CLASS_NAME, "product-brand").text
            enlace = prd.find_element(By.TAG_NAME, "a").get_attribute("href")
            precio_texto = prd.find_element(By.CLASS_NAME, "spot-price").text
            precio_num = int(re.sub(r'[^\d.]', '', precio_texto))
            codigo = prd.find_element(By.CLASS_NAME, "check-compare__input").get_attribute("id")
            codigo_corregido = codigo.replace("prod", "")
        except NoSuchElementException:
            continue  # Si algún elemento falla, pasa al siguiente producto

        # Almacenar la información en el diccionario
        producto_info = {
            'Pagina': str(pagina),
            'Plataforma': 'ENTEL',
            'Tipo': 'CELULARES',
            'Fecha': now.date(),
            'Hora': now.time(),
            'Titulo': titulo.upper(),
            'Marca': marca.upper(),
            'Enlace': enlace,
            'Precio Tarjeta': '',
            'Precio Internet': precio_num,
            'Precio Internet2': '',
            'Precio Lista': '',
            'Precio Lista2': '',
            'Envío Gratis': 'No',
            'Cuotas sin Interes': '',
            'Vendedor': 'ENTEL',
            'Codigo': codigo_corregido,
        }
        lista_productos.append(producto_info)

# Navegar por las páginas
while color == "#002EFF":
    extraer_productos()
    wait = WebDriverWait(driver, 20)
    try:
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.pagination-container a.page-right")))
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("window.scrollBy(0, -150);")
        element.click()
        sleep(5)
        pagina += 1
        color = driver.find_element(By.CSS_SELECTOR, "div.pagination-container a.page-right svg path").get_attribute("stroke")
    except TimeoutException:
        print("No se encontraron más páginas.")
        break

if color == "#A4A4A6":
    extraer_productos()

# Guardar los datos en un archivo CSV
output_file = os.path.join(output_folder, f'productos-ENTEL-Celulares-{now.date()}.csv')
df = pd.DataFrame(lista_productos)
df.to_csv(output_file, encoding='latin1', index=False)
print(f"Archivo guardado en: {output_file}")

# Finalizar el driver
driver.quit()
