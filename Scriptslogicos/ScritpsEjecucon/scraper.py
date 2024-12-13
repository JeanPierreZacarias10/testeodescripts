from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
now = datetime.now()
lista_productos=[]
service_obj = Service("C:\\Program Files\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service_obj)
driver.maximize_window()
for x in range(1,14):
        driver.get("https://www.coolbox.pe/celulares-y-accesorios/celulares?page="+str(x))    
        sleep(2)
        pagina= BeautifulSoup(driver.page_source,'html.parser')
        content = pagina.find_all('div', class_='coolboxpe-search-result-0-x-galleryItem coolboxpe-search-result-0-x-galleryItem--container-galleryProductos coolboxpe-search-result-0-x-galleryItem--normal coolboxpe-search-result-0-x-galleryItem--container-galleryProductos--normal coolboxpe-search-result-0-x-galleryItem--grid coolboxpe-search-result-0-x-galleryItem--container-galleryProductos--grid pa4')
        for property in content:
                titulo= property.find('span', class_='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-productBrand--carrusel-pd-title vtex-product-summary-2-x-brandName vtex-product-summary-2-x-brandName--carrusel-pd-title t-body')
                titulo_corregido= titulo.text if titulo is not None else '' 
                titulo_corregido=titulo_corregido.replace('”','"')
                titulo_corregido=titulo_corregido.replace('“','"')
                enlace=property.find('a', href=True, class_='vtex-product-summary-2-x-clearLink vtex-product-summary-2-x-clearLink--container-carrusel-pd-overlay-effect h-100 flex flex-column')
                enlace_corregido=enlace.get("href") if enlace is not None else '' 
                marca= property.find('span', class_='vtex-store-components-3-x-productBrandName')
                marca_corregido=marca.text if marca is not None else ''
                #precioLista
                precio_p1= property.find_all('span', class_="vtex-product-summary-2-x-currencyContainer vtex-product-summary-2-x-currencyContainer--pd-type2")
                if len(precio_p1) > 0:
                        precio_lista_final=precio_p1[0].text if precio_p1[0] is not None else ''
                        marker1 = 'S/ '
                        precio_lista_final = precio_lista_final.split(marker1,1)[1]
                else:
                        precio_lista_final=''   
                if len(precio_p1) > 1:
                        precio_internet_final=precio_p1[1].text if precio_p1[1] is not None else ''
                        precio_internet_final = precio_internet_final.split(marker1,1)[1]
                else:
                        precio_internet_final=''
               #envio
                envio_gratis= property.find('p', class_='lh-copy vtex-rich-text-0-x-paragraph vtex-rich-text-0-x-paragraph--tag-free-shipping vtex-rich-text-0-x-paragraph--tag-list-mobile')
                envio_gratis_corregido= 'Sí' if envio_gratis is not None else 'No' 
                vendedor=property.find('p', class_='coolboxpe-custom-store-components-0-x-sellerInPLP')
                vendedor_corregido=vendedor.text if vendedor is not None else ''
                vendedor_corregido=vendedor_corregido.split("Vendido por ",1)[1].upper()
                #print("lista" + precio_lista_final , "internet" + precio_internet_final)
                producto_info ={'Pagina': '',
                                'Plataforma': 'COOLBOX',
                                'Tipo': 'CELULARES',
                                'Fecha' : now.date(),
                                'Hora': now.time(),
                                'Titulo' : titulo_corregido.upper(),
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
                                'Codigo':''}
                lista_productos.append(producto_info)
df=pd.DataFrame(lista_productos)
df.to_csv('C:\\Data_Archivos\\'+'productos-COOLBOX-Celulares-' + str(now.date()) + '.csv',encoding='latin1', errors='ignore')
# Cargar el archivo existente "BaseDatosNueva.csv"
try:
    df_existing = pd.read_csv('C:\\Data_Archivos\\BaseDatosNueva.csv', encoding='latin1',delimiter=';')
except FileNotFoundError:
    df_existing = pd.DataFrame()  # Si no existe, crea un DataFrame vacío

# Concatenar los nuevos datos con los existentes
df_combined = pd.concat([df_existing, df], ignore_index=True)

# Guardar el archivo combinado de nuevo en "BaseDatosNueva.csv"
df_combined.to_csv('C:\\Data_Archivos\\BaseDatosNueva.csv', encoding='latin1', index=False, errors='ignore')

driver.quit()
