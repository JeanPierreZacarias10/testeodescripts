import os
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from time import sleep

# Fecha y hora actual
now = datetime.now()

# Lista para almacenar los productos
lista_productos = []

# Configuración del driver
service_obj = Service("/usr/bin/chromedriver")  # Ruta adaptada para GitHub Actions
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service_obj, options=chrome_options)

# Crear carpeta para guardar los resultados
output_folder = "archivosscripts"
os.makedirs(output_folder, exist_ok=True)

# Scraping de las páginas
for x in range(1, 14):
    driver.get(f"https://www.coolbox.pe/celulares-y-accesorios/celulares?page={x}")
    sleep(2)
    pagina = BeautifulSoup(driver.page_source, 'html.parser')
    content = pagina.find_all('div', class_='coolboxpe-search-result-0-x-galleryItem coolboxpe-search-result-0-x-galleryItem--container-galleryProductos coolboxpe-search-result-0-x-galleryItem--normal coolboxpe-search-result-0-x-galleryItem--container-galleryProductos--normal coolboxpe-search-result-0-x-galleryItem--grid coolboxpe-search-result-0-x-galleryItem--container-galleryProductos--grid pa4')
    
    for property in content:
        titulo = property.find('span', class_='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-productBrand--carrusel-pd-title vtex-product-summary-2-x-brandName vtex-product-summary-2-x-brandName--carrusel-pd-title t-body')
        titulo_corregido = titulo.text.replace('”', '"').replace('“', '"') if titulo else ''
        
        enlace = property.find('a', href=True, class_='vtex-product-summary-2-x-clearLink vtex-product-summary-2-x-clearLink--container-carrusel-pd-overlay-effect h-100 flex flex-column')
        enlace_corregido = enlace.get("href") if enlace else ''
        
        marca = property.find('span', class_='vtex-store-components-3-x-productBrandName')
        marca_corregido = marca.text if marca else ''
        
        precio_p1 = property.find_all('span', class_="vtex-product-summary-2-x-currencyContainer vtex-product-summary-2-x-currencyContainer--pd-type2")
        marker1 = 'S/ '
        precio_lista_final = precio_p1[0].text.split(marker1, 1)[1] if len(precio_p1) > 0 else ''
        precio_internet_final = precio_p1[1].text.split(marker1, 1)[1] if len(precio_p1) > 1 else ''
        
        envio_gratis = property.find('p', class_='lh-copy vtex-rich-text-0-x-paragraph vtex-rich-text-0-x-paragraph--tag-free-shipping vtex-rich-text-0-x-paragraph--tag-list-mobile')
        envio_gratis_corregido = 'Sí' if envio_gratis else 'No'
        
        vendedor = property.find('p', class_='coolboxpe-custom-store-components-0-x-sellerInPLP')
        vendedor_corregido = vendedor.text.split("Vendido por ", 1)[1].upper() if vendedor else ''
        
        producto_info = {
            'Pagina': x,
            'Plataforma': 'COOLBOX',
            'Tipo': 'CELULARES',
            'Fecha': now.date(),
            'Hora': now.time(),
            'Titulo': titulo_corregido.upper(),
            'Marca': marca_corregido.upper(),
            'Enlace': 'https://www.coolbox.pe' + enlace_corregido,
            'Precio Tarjeta': '',
            'Precio Internet': precio_internet_final,
            'Precio Internet2': '',
            'Precio Lista': precio_lista_final,
            'Precio Lista2': '',
            'Envío Gratis': envio_gratis_corregido,
            'Cuotas sin Interes': '',
            'Vendedor': vendedor_corregido,
            'Codigo': ''
        }
        lista_productos.append(producto_info)

# Guardar los datos en un archivo CSV
output_file = os.path.join(output_folder, f'productos-COOLBOX-Celulares-{now.date()}.csv')
df = pd.DataFrame(lista_productos)
df.to_csv(output_file, encoding='latin1', index=False)
print(f"Archivo guardado en: {output_file}")

# Finalizar el driver
driver.quit()
