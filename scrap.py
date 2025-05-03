import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import random

def extraer_datos_de_tabla(url):
    """
    Extrae datos de una tabla de calorías de la web especificada.
    
    Args:
        url (str): URL de la página web que contiene la tabla de calorías
    
    Returns:
        DataFrame: Tabla con los datos de alimentos y sus calorías
    """
    # Añadir headers para simular un navegador real (evitar bloqueos)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        # Realizar la petición GET a la URL
        print(f"Accediendo a {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Comprobar si hay errores HTTP
        
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la tabla de calorías (esto dependerá de la estructura de la web)
        # Esta parte necesitará ajustes según la estructura real de la página
        
        # Método 1: Buscar por etiquetas específicas
        print("Buscando datos en la tabla...")
        
        # Lista para almacenar los datos extraídos
        datos = []
        
        # Buscar elementos que podrían contener los datos
        # Esto es un ejemplo y deberá adaptarse a la estructura real de la web
        # Opción 1: Buscar filas de tabla
        filas_tabla = soup.find_all('tr')
        
        if filas_tabla:
            print(f"Encontradas {len(filas_tabla)} filas en tabla(s)")
            for fila in filas_tabla:
                celdas = fila.find_all(['td', 'th'])
                if len(celdas) >= 3:  # Asumimos al menos 3 columnas (alimento, porción, calorías)
                    try:
                        alimento = celdas[0].text.strip()
                        porcion = celdas[1].text.strip()
                        calorias_text = celdas[2].text.strip()
                        
                        # Extraer el número de calorías usando expresiones regulares
                        calorias_match = re.search(r'(\d+)(?:\.\d+)?\s*kcal', calorias_text)
                        if calorias_match:
                            calorias = int(calorias_match.group(1))
                            datos.append({
                                'alimento': alimento,
                                'porcion': porcion,
                                'calorias': calorias
                            })
                    except Exception as e:
                        print(f"Error procesando fila: {e}")

        # Crear DataFrame con los datos extraídos
        if datos:
            df = pd.DataFrame(datos)
            print(f"Se han extraído {len(df)} registros")
            return df
        else:
            print("No se encontraron datos en el formato esperado")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la web: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def extraer_datos_de_multiples_paginas(urls):
    """
    Extrae datos de múltiples páginas y los combina en un único DataFrame
    
    Args:
        urls (list): Lista de URLs a procesar
    
    Returns:
        DataFrame: Datos combinados de todas las páginas
    """
    all_data = []
    
    for url in urls:
        df = extraer_datos_de_tabla(url)
        if df is not None and not df.empty:
            all_data.append(df)
        
        # Esperar un tiempo aleatorio entre peticiones para evitar ser bloqueado
        time.sleep(random.uniform(1, 3))
    
    if all_data:
        # Combinar todos los DataFrames
        df_combinado = pd.concat(all_data, ignore_index=True)
        # Eliminar duplicados
        df_combinado.drop_duplicates(subset=['alimento'], inplace=True)
        return df_combinado
    else:
        return None

def guardar_datos(df, formato='csv'):
    """
    Guarda los datos extraídos en el formato especificado
    
    Args:
        df (DataFrame): DataFrame con los datos a guardar
        formato (str): Formato en el que guardar ('csv', 'excel', 'json')
    """
    if df is None or df.empty:
        print("No hay datos para guardar")
        return
    
    try:
        if formato.lower() == 'csv':
            df.to_csv('tabla_calorias_aceites.csv', index=False, encoding='utf-8-sig')
            print("Datos guardados en 'tabla_calorias_aceites.csv'")
        elif formato.lower() == 'excel':
            df.to_excel('tabla_calorias_aceites.xlsx', index=False)
            print("Datos guardados en 'tabla_calorias_aceites.xlsx'")
        elif formato.lower() == 'json':
            df.to_json('tabla_calorias_aceites.json', orient='records', force_ascii=False)
            print("Datos guardados en 'tabla_calorias_aceites.json'")
        else:
            print(f"Formato '{formato}' no soportado")
    except Exception as e:
        print(f"Error al guardar los datos: {e}")

def mostrar_estadisticas(df):
    """
    Muestra estadísticas básicas sobre los datos extraídos
    
    Args:
        df (DataFrame): DataFrame con los datos extraídos
    """
    if df is None or df.empty:
        print("No hay datos para analizar")
        return
    
    try:
        print("\n--- ESTADÍSTICAS BÁSICAS ---")
        print(f"Total de alimentos: {len(df)}")
        print(f"Calorías promedio: {df['calorias'].mean():.2f} kcal")
        print(f"Calorías mínimas: {df['calorias'].min()} kcal")
        print(f"Calorías máximas: {df['calorias'].max()} kcal")
        
        # Categorizar los alimentos
        df['categoria'] = 'otro'
        df.loc[df['alimento'].str.contains('Aceite', case=False), 'categoria'] = 'aceite'
        df.loc[df['alimento'].str.contains('Grasa|Manteca|Mantequilla|Margarina|Ghee', case=False), 'categoria'] = 'grasa'
        
        # Contar por categoría
        print("\nDistribución por categoría:")
        print(df['categoria'].value_counts())
        
        # Contar por tipo de unidad (g vs ml)
        df['unidad'] = df['porcion'].str.extract(r'([gm]l)')
        print("\nDistribución por unidad de medida:")
        print(df['unidad'].value_counts())
        
    except Exception as e:
        print(f"Error al analizar los datos: {e}")

def main():
    # URL de ejemplo - deberás reemplazarla con la URL real
    urls = ["https://www.tabladecalorias.net/alimento/aceite-grasas", "https://www.tabladecalorias.net/alimento/hierbas-especias-te"]
    
    # Para múltiples páginas, usar una lista
    # urls = ["https://ejemplo.com/pagina1", "https://ejemplo.com/pagina2"]
    
    print("=== EXTRACTOR DE DATOS DE CALORÍAS ===")
    df = extraer_datos_de_multiples_paginas(urls)
    
    if df is not None and not df.empty:
        mostrar_estadisticas(df)
        
        # Preguntar al usuario en qué formato guardar los datos
        print("\n¿En qué formato deseas guardar los datos?")
        print("1. CSV")
        print("2. Excel")
        print("3. JSON")
        opcion = input("Selecciona una opción (1-3): ")
        
        if opcion == '1':
            guardar_datos(df, 'csv')
        elif opcion == '2':
            guardar_datos(df, 'excel')
        elif opcion == '3':
            guardar_datos(df, 'json')
        else:
            print("Opción no válida. Guardando en formato CSV por defecto.")
            guardar_datos(df, 'csv')
    else:
        print("No se pudieron extraer datos. Verifica la URL o la estructura de la página.")

if __name__ == "__main__":
    main()