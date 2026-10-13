#E1
from pathlib import Path
import pandas as pd

#Parte 1: Diagnóstico
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR/ "Datos" #Defines la carpeta donde está el fichero que quieres abrir
#Path(__file__).parent obtiene la carpeta donde está guardado el archivo Python que estás ejecutando.
SOLUCIONES_DIR = BASE_DIR / "SolucionesS2"

def cargar_tabla(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el fichero: {path}")
    return pd.read_csv(path)

raw = cargar_tabla(DATA_DIR/ "ventas.csv")
raw

print(raw.shape) #Da 10 filas y seis columnas
print(raw.dtypes) #
print(raw.isna().sum()) #Hay dos filas que tienen un valor nulo en la columna unidades y una en la columna de precio unitario

#Parte 2: Validación

def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    #Recibes un argumento llamado frame, que esperamos que sea un DataFrame de pandas. 
    #La parte del -> solo indica que la función va a devolver una tupla con dos dataframes, uno con las filas válidas y otro con los errores.
    copia = frame.copy() #Copia del DataFrame original para no modificarlo directamente.
    copia["unidades"] = pd.to_numeric(copia["unidades"], errors="coerce") #Convierte la columna "unidades" a tipo numérico, y si hay errores los convierte en NaN.
    copia["precio_unitario"] = pd.to_numeric(copia["precio_unitario"], errors="coerce")
    condicion_validos = (
        copia["unidades"].notna()
        & copia["precio_unitario"].notna()
        & (copia["unidades"] > 0)
        & (copia["precio_unitario"] > 0)
    )
    validos = copia[condicion_validos].copy()
    errores = copia[~condicion_validos].copy()
    validos["importe"] = validos["unidades"] * validos["precio_unitario"]
    return validos, errores

validos, errores = validar_ventas(raw)
print("Válidos:", len(validos))
print("Errores:", len(errores)) #DA LO MISMO QUE EL CHECKPOINT

#Parte 3: Agregaciones
# Convertir fecha de texto a datetime
validos["fecha"] = pd.to_datetime(validos["fecha"])

# 3.0 Importe total por semana 
importe_por_semana = ( #dt permite acceder a cosas propiad de fechas
    validos.groupby(validos["fecha"].dt.to_period("W"))["importe"] #La w convierte cada fecha en la semana a la que pertenece 
    .sum()
    .sort_values(ascending=False)
)

print(importe_por_semana)
#3.1 Importe total por región(ordenado desc)
importe_por_region = validos.groupby("region")["importe"].sum().sort_values(ascending=False)
print(importe_por_region)

#3.2 Top 3 producto por importe
top_productos_importe = validos.groupby("producto")["importe"].sum().sort_values(ascending=False).head(3)
print(top_productos_importe)

#3.3 Cliente_id con más de una compra
# Para saber que clientes tienen más de una compra, no tienes que sumas unidades, porque en una compra puede tener varias unidades. Lo que quieres contar es cuantas filas/compras tiene cada cliente.
compras_por_cliente = validos.groupby("cliente_id").size()#Cuenta cuántas filas tiene cada cliente
clientes_mas_1_compra = compras_por_cliente[compras_por_cliente > 1]
print(clientes_mas_1_compra)

#3.4 Exportación

import json
#Guardar las ventas válidas
validos.to_csv(SOLUCIONES_DIR / "ventas_limpias.csv", index=False)

#Crear resumen de calidad 
calidad_datos = {
    "filas_totales": len(raw),
    "filas_validas": len(validos),
    "filas_invalidas": len(errores),
    "importe_total": validos["importe"].sum()
}

# Guardar el resumen en JSON
with open(SOLUCIONES_DIR / "calidad_datos.json", "w", encoding="utf-8") as f:
    json.dump(calidad_datos, f, indent=4)


