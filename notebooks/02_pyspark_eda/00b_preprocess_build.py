# Databricks notebook source
# MAGIC %md
# MAGIC # **🎯 Objetivo del notebook**
# MAGIC
# MAGIC Leer los CSV crudos `(cortes “latest” o “hist”)`, normalizar tipos básicos `(fechas y métricas numéricas)`, y producir un DataFrame pandas unificado que servirá como insumo del resto del preprocesamiento `(joins con diccionarios, encoding, etc)`.

# COMMAND ----------

# MAGIC %md
# MAGIC # 1. Librerías y Contexto

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.1 Parametrización de ambiente

# COMMAND ----------

# ========= Parametrización de entorno =========
import os

ENTORNOS_VALIDOS = ["dev", "qa", "prod"]

def _fail(msg: str):
    # Sale limpiamente si estamos en Databricks; si no, lanza excepción estándar.
    if "dbutils" in globals() and hasattr(dbutils, "notebook"):
        dbutils.notebook.exit(msg)
    raise RuntimeError(msg)

# 1) Intenta leer de widget (si existe); si no existe, créalo con el valor de la variable de entorno o vacío.
environment = os.getenv("environment", "").strip()

try:
    # Si el widget no existe, créalo con un default razonable (env var o 'dev')
    _ = dbutils.widgets.get("environment")  # puede fallar si no existe
except Exception:
    if "dbutils" in globals():
        dbutils.widgets.text("environment", environment or "dev", "environment")

# 2) Prioriza el valor del widget si estamos en Databricks
try:
    if "dbutils" in globals():
        environment = dbutils.widgets.get("environment").strip()
except Exception:
    pass  # si no hay dbutils o falla, nos quedamos con el de os.getenv

print(f"environment detectado: {environment or '(vacío)'}")

# 3) Validaciones
if not environment:
    _fail("Error: 'environment' es obligatorio y no se encontró definido (widget ni variable de entorno).")

if environment not in ENTORNOS_VALIDOS:
    _fail(f"Error: 'environment' debe ser uno de: {', '.join(ENTORNOS_VALIDOS)}")

print("environment validado correctamente.")


# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.2 Parametrización de contexto

# COMMAND ----------

# ========= Rutas en Volúmenes de UC (dinámicas por environment) =========
import os
import pandas as pd
import numpy as np
import csv
from typing import List
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.decomposition import PCA
import pickle
import joblib

# ---- Parámetros de naming (ajústalos si tu convención cambia) ----
CATALOG_BASE = "arqanalitica"   # base del catálogo (sin el prefijo de entorno)
SCHEMA       = "stg"            # esquema de trabajo
VOLUME_NAME  = "files"          # nombre del Volume
DATASET_ROOT = "datasets/modelo_cotizaciones"  # raíz de datasets dentro del Volume
RAW_SUBDIR   = "latest"         # "latest" o "hist"

# Mapea el catálogo dependiendo del entorno
CATALOG = f"{environment}_{CATALOG_BASE}"   # p.ej. dev_arqanalitica / qa_arqanalitica / prod_arqanalitica

# BASE: /Volumes/<catalog>/<schema>/<volume>/<dataset_root>
BASE = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME_NAME}/{DATASET_ROOT}"

# Derivadas
RAW_DIR            = f"{BASE}/raw/{RAW_SUBDIR}"
RAW_DIR_HIST       = f"{BASE}/raw/hist"
RAW_DIR_LATEST     = f"{BASE}/raw/latest"
DICTS_DIR_OFFICIAL = f"{BASE}/90_dicts"
MODELS_DIR         = f"{BASE}/models"

# Comprobaciones de existencia (opcionales pero útiles)
def _ensure_dir(path: str, must_exist: bool = True):
    if must_exist and not os.path.isdir(path):
        msg = (
            f"No existe la carpeta: {path}\n"
            f"Revisa que el Volume y ruta existan para el entorno '{environment}'.\n"
            f"Sugerido catálogo: {CATALOG} | esquema: {SCHEMA} | volume: {VOLUME_NAME}"
        )
        if "dbutils" in globals() and hasattr(dbutils, "notebook"):
            dbutils.notebook.exit(msg)
        raise FileNotFoundError(msg)

_ensure_dir(os.path.dirname(BASE), must_exist=True)  # valida hasta /Volumes/<catalog>/<schema>/<volume>
_ensure_dir(RAW_DIR, must_exist=True)

print({
    "ENV": environment,
    "CATALOG": CATALOG,
    "SCHEMA": SCHEMA,
    "VOLUME": VOLUME_NAME,
    "BASE": BASE,
    "RAW_DIR": RAW_DIR,
    "DICTS_DIR_OFFICIAL": DICTS_DIR_OFFICIAL,
    "MODELS_DIR": MODELS_DIR
})


# COMMAND ----------

# MAGIC %md
# MAGIC # 2. Lectura y unión de CSVs crudos

# COMMAND ----------

# === Lectura robusta de RAW con fallback de encoding y conteo binario ===
import os, csv
import pandas as pd

def _count_lines_binary(path: str) -> int | None:
    """Cuenta líneas sin decodificar (evita UnicodeDecodeError). Resta 2 de metadata."""
    try:
        with open(path, "rb") as fh:
            return max(sum(1 for _ in fh) - 2, 0)
    except Exception:
        return None

def _read_csv_robust(path: str, cols: list[str]) -> pd.DataFrame:
    """Intenta varias codificaciones típicas; último recurso: reemplaza caracteres inválidos."""
    for enc in ("utf-8-sig", "latin-1", "cp1252"):
        try:
            return pd.read_csv(
                path,
                sep=":",                # separador original
                engine="python",
                skiprows=2,             # salta 2 líneas de metadata
                names=cols,             # imponemos nombres
                dtype=str,              # inicialmente todo como str
                quoting=csv.QUOTE_NONE,
                on_bad_lines="skip",
                encoding=enc,
            )
        except UnicodeDecodeError:
            continue

    # Último recurso: intenta con utf-8 reemplazando caracteres inválidos (si la versión de pandas lo soporta)
    try:
        return pd.read_csv(
            path,
            sep=":",
            engine="python",
            skiprows=2,
            names=cols,
            dtype=str,
            quoting=csv.QUOTE_NONE,
            on_bad_lines="skip",
            encoding="utf-8",
            encoding_errors="replace",  # pandas >= 1.3
        )
    except TypeError:
        # Si la versión de pandas no soporta encoding_errors, vuelve a latin-1 (ya debería haber funcionado)
        return pd.read_csv(
            path,
            sep=":",
            engine="python",
            skiprows=2,
            names=cols,
            dtype=str,
            quoting=csv.QUOTE_NONE,
            on_bad_lines="skip",
            encoding="latin-1",
        )

def leer_unir_csvs(raw_dir: str) -> pd.DataFrame:
    """
    Lee TODOS los CSV de la carpeta `raw_dir`, aplica:
      - parseo de fechas ('%Y-%m-%d') en las 2 primeras columnas,
      - limpieza de miles en las últimas 4 y cast a float (redondeo 1),
    y concatena resultados.
    """
    # columnas esperadas en los crudos
    cols = [
        "Fecha_creacion", "Fecha_modificacion", "Solicitante_nit",
        "Numero_cotizacion", "Numero_pedido", "Grupo_clientes",
        "Estado_cotizacion", "Zona", "Region", "Ciudad",
        "Punto_de_venta", "Representante_ventas_id", "Representante_ventas",
        "Negocio", "Grupo_articulos", "Categoria",
        "Importe_cotizacion", "Cantidad_cotizacion",
        "Precio_cotizacion", "Valor_descuentos",
    ]
    date_cols = cols[:2]   # dos primeras son fechas
    num_cols  = cols[-4:]  # últimas cuatro son métricas

    assert os.path.isdir(raw_dir), f"No existe carpeta: {raw_dir}"

    dfs, total, buenas = [], 0, 0
    for fname in sorted(os.listdir(raw_dir)):
        if not fname.lower().endswith(".csv"):
            continue

        path = os.path.join(raw_dir, fname)

        # Conteo binario (no decodifica → evita UnicodeDecodeError)
        filas = _count_lines_binary(path)

        # Lectura robusta con fallback de encoding
        df = _read_csv_robust(path, cols)
        n  = len(df)

        if filas is not None:
            print(f"{fname}: total={filas}, parseadas={n}, saltadas={max(filas-n, 0)}")
            total  += max(filas, 0)
            buenas += n
        else:
            print(f"{fname}: parseadas={n} (conteo total no disponible)")

        # --- Conversión de fechas ---
        for c in date_cols:
            df[c] = pd.to_datetime(df[c], format="%Y-%m-%d", errors="coerce").dt.date

        # --- Limpieza numérica ---
        df[num_cols] = (
            df[num_cols]
              .replace({",": ""}, regex=True)
              .astype(float)
              .round(1)
        )

        dfs.append(df)

    if not dfs:
        print("No se encontraron CSV válidos en:", raw_dir)
        return pd.DataFrame(columns=cols)

    if total:
        print(f"Global: total={total}, parseadas={buenas}, saltadas={max(total-buenas, 0)}")
    else:
        print("Global: parseadas=", sum(len(x) for x in dfs))

    return pd.concat(dfs, ignore_index=True)

# === Uso típico (requiere que RAW_DIR esté definido arriba en tu notebook) ===
df_raw = leer_unir_csvs(RAW_DIR)
print(df_raw.head())
print("shape:", df_raw.shape)


# COMMAND ----------

# MAGIC %md
# MAGIC # 3. Carga y aplicación de diccionarios CSV

# COMMAND ----------

def cargar_diccionarios(dicts_dir: str) -> dict:
    """
    Lee todos los CSV de diccionarios en `dicts_dir`.
    Se asume el formato: <col_texto> y 'Id_<col_texto>'.
      - Detecta cuál es la columna de texto (no empieza por 'Id_')
      - Lee como string para no perder ceros a la izquierda.
      - Ignora archivos vacíos o con formato inesperado.
    Retorna: { nombre_columna_texto : {texto -> id} }
    """
    assert os.path.isdir(dicts_dir), f"No existe carpeta de diccionarios: {dicts_dir}"
    archivos = sorted([f for f in os.listdir(dicts_dir) if f.lower().endswith(".csv")])
    diccionarios = {}

    for archivo in archivos:
        path = os.path.join(dicts_dir, archivo)
        try:
            # utf-8-sig por si hay BOM; todo como str para estabilidad
            df_dict = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
        except Exception as e:
            print(f"[WARN] No pude leer {archivo}: {e}")
            continue

        # Saltar vacíos o con menos de 2 columnas
        if df_dict.empty or df_dict.shape[1] < 2:
            print(f"[SKIP] Archivo inválido/vacío: {archivo}")
            continue

        # Detectar la columna de texto (la que no es Id_)
        text_cols = [c for c in df_dict.columns if not c.startswith("Id_")]
        if not text_cols:
            print(f"[SKIP] No hallé columna de texto en: {archivo}")
            continue
        col_txt = text_cols[0]
        col_id  = f"Id_{col_txt}"
        if col_id not in df_dict.columns:
            print(f"[SKIP] No hallé columna id esperada '{col_id}' en: {archivo}")
            continue

        # Construir mapping texto->id (dropna por si hay filas incompletas)
        map_df = df_dict[[col_txt, col_id]].dropna()
        diccionarios[col_txt] = dict(zip(map_df[col_txt].astype(str), map_df[col_id].astype(str)))

    print(f"✓ Cargados {len(diccionarios)} diccionario(s) desde: {dicts_dir}")
    return diccionarios


def aplicar_diccionarios(df: pd.DataFrame, diccionarios: dict) -> pd.DataFrame:
    """
    Aplica los mapeos en las columnas presentes del DataFrame.
    - Convierte la columna a string, aplica map() y
      deja el valor original si no se encuentra en el diccionario.
    - Devuelve un nuevo DataFrame (no modifica df in-place).
    """
    out = df.copy()
    for col, mapping in diccionarios.items():
        if col in out.columns:
            # map produce NaN cuando no encuentra clave; usamos where() para conservar original
            mapped = out[col].astype(str).map(mapping)
            out[col] = mapped.where(mapped.notna(), out[col])
    return out


def validar_nulos_y_no_mapeados(df: pd.DataFrame, diccionarios: dict, sample=5):
    """
    Reporte rápido:
      - Cuántos 'no mapeados' quedaron (valores que siguen siendo texto original).
      - Cuántos nulos hay (debería ser 0 si la entrada no tenía nulos).
    """
    for col, mapping in diccionarios.items():
        if col not in df.columns:
            continue

        serie = df[col]
        # 'no mapeados' = valores que no quedaron exactamente en el rango de IDs
        ids_set = set(mapping.values())
        # como guardamos ids como str, comparamos como str
        still_text_mask = ~serie.astype(str).isin(ids_set)

        n_unmapped = int(still_text_mask.sum())
        n_nulls    = int(serie.isna().sum())

        if n_unmapped > 0 or n_nulls > 0:
            print(f"[INFO] Columna '{col}': no mapeados={n_unmapped}, nulos={n_nulls}")
            if n_unmapped > 0 and sample > 0:
                muestra = serie[still_text_mask].astype(str).head(sample).tolist()
                print("       Ejemplos no mapeados:", muestra)


# --- Uso con las rutas centralizadas de la celda 1 ---
# Si quisieras comparar vs los diccionarios recién generados en 00a, cambia
# DICTS_DIR_OFFICIAL -> f"{BASE}/90_dicts"
diccionarios = cargar_diccionarios(DICTS_DIR_OFFICIAL)

df_categ = aplicar_diccionarios(df_raw, diccionarios)
print(df_categ.head(5))

# Reporte de salud post-mapeo
validar_nulos_y_no_mapeados(df_categ, diccionarios, sample=3)


# COMMAND ----------

# MAGIC %md
# MAGIC # 4. Target engineering + limpieza puntual

# COMMAND ----------

def transformar_estado_cotizacion(df: pd.DataFrame,
                                  col_estado: str = "Estado_cotizacion",
                                  keep_original: bool = False) -> pd.DataFrame:
    """
    Mantiene SOLO los estados de interés y los mapea a binario.
      'Cotización Ganada'   -> 1
      'Cotización Perdida'  -> 0
      'Cotización Expirada' -> 0

    Parametros:
      col_estado: nombre de la columna con el estado.
      keep_original: si True, conserva una copia '_raw' antes del mapeo.

    Retorna:
      Nuevo DataFrame filtrado y con la columna binarizada (int8).
    """
    if col_estado not in df.columns:
        raise KeyError(f"No existe la columna '{col_estado}' en el DataFrame.")

    # Trabajamos sobre una copia explícita para evitar SettingWithCopyWarning
    out = df.copy()

    estados_validos = {"Cotización Ganada", "Cotización Perdida", "Cotización Expirada"}
    out = out.loc[out[col_estado].isin(estados_validos)].copy()

    if keep_original:
        out[f"{col_estado}_raw"] = out[col_estado]

    mapping = {
        "Cotización Ganada": 1,
        "Cotización Perdida": 0,
        "Cotización Expirada": 0,
    }
    out[col_estado] = out[col_estado].map(mapping).astype("int8")

    return out


def eliminar_columna_representante(df: pd.DataFrame,
                                   col: str = "Representante_ventas") -> pd.DataFrame:
    """
    Elimina la columna de texto libre del representante (si existe).
    Se mantiene 'Representante_ventas_id' como llave numérica ya mapeada.
    """
    out = df.copy()
    return out.drop(columns=[col], errors="ignore")


# --- Aplicación sobre el dataset categorizado ---
df_categ = transformar_estado_cotizacion(df_categ, keep_original=False)
df_categ = eliminar_columna_representante(df_categ)

# -------------------------
# Métricas de control/QA
# -------------------------
total_filas = len(df_categ)

if "Numero_cotizacion" in df_categ.columns:
    n_distintos_total = df_categ["Numero_cotizacion"].nunique()
    n_distintos_por_estado = (
        df_categ.groupby("Estado_cotizacion")["Numero_cotizacion"].nunique().sort_index()
    )
else:
    n_distintos_total = None
    n_distintos_por_estado = None

print(f"Total de filas post-filtrado/binarizado: {total_filas}")
if n_distintos_total is not None:
    print(f"Numero_cotizacion distintos (total): {n_distintos_total}")
    print("Numero_cotizacion distintos por Estado (0=Perdida/Expirada, 1=Ganada):")
    print(n_distintos_por_estado)

print("\nPreview:")
print(df_categ.head())

# COMMAND ----------

# MAGIC %md
# MAGIC # 5. Rutas de trabajo y validaciones

# COMMAND ----------

# Ajuste de latencia
#  - Calcula días entre 'Fecha_modificacion' y 'Fecha_creacion'
#  - Si hay negativos (inconsistencias de origen), los reemplaza por la latencia máxima observada en el dataset.

def ajustar_latencia(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Convertimos a datetime de forma tolerante (evita fallar por filas raras)
    out["Fecha_creacion"]     = pd.to_datetime(out["Fecha_creacion"],     errors="coerce")
    out["Fecha_modificacion"] = pd.to_datetime(out["Fecha_modificacion"], errors="coerce")

    # Cálculo de latencia cruda en días
    out["Latencia"] = (out["Fecha_modificacion"] - out["Fecha_creacion"]).dt.days

    # Latencia máxima posible usando el rango observado
    # (si todo es NaT, cae en 0 para no romper)
    min_crea = out["Fecha_creacion"].min()
    max_mod  = out["Fecha_modificacion"].max()
    latencia_maxima = int((max_mod - min_crea).days) if pd.notnull(min_crea) and pd.notnull(max_mod) else 0
    latencia_maxima = max(latencia_maxima, 0)

    # Reemplazo de latencias negativas por el máximo observado
    mask_invalidas = out["Latencia"] < 0
    n_invalidas = int(mask_invalidas.sum())
    if n_invalidas > 0:
        print(f"Ajustando {n_invalidas} filas con fechas inválidas -> Latencia={latencia_maxima} días")
        out.loc[mask_invalidas, "Latencia"] = latencia_maxima

    # Para filas con NaT en fechas, si quedaron NaN, las llevamos a 0 (o decide otra política)
    out["Latencia"] = out["Latencia"].fillna(0).astype("int32")

    return out

# Métricas agregadas a nivel de 'Numero_cotizacion'
#  - Sumas de importes/cantidades/precio/descuentos
#  - Proporción de descuentos
#  - Estadísticas de precio (std, min, max, count, rango)

def agregar_metricas(df: pd.DataFrame) -> pd.DataFrame:
    df_sum = (
        df.groupby("Numero_cotizacion")
          .agg({
              "Importe_cotizacion": "sum",
              "Cantidad_cotizacion": "sum",
              "Precio_cotizacion": "sum",
              "Valor_descuentos": "sum",
          })
          .rename(columns={
              "Importe_cotizacion":  "Suma_Importe_cotizacion",
              "Cantidad_cotizacion": "Suma_Cantidad_cotizacion",
              "Precio_cotizacion":   "Suma_Precio_cotizacion",
              "Valor_descuentos":    "Suma_Valor_descuentos",
          })
          .reset_index()
    )

    # Evita división por cero y deja 0 cuando no aplica
    df_sum["Proporcion_descuentos"] = (
        df_sum["Suma_Valor_descuentos"] /
        df_sum["Suma_Importe_cotizacion"].replace(0, np.nan)
    ).fillna(0)

    stats = (
        df.groupby("Numero_cotizacion")["Precio_cotizacion"]
          .agg(["std", "min", "max", "count"])
          .reset_index()
          .rename(columns={
              "std":   "Desviacion_precio",
              "min":   "Min_precio",
              "max":   "Max_precio",
              "count": "Num_items",
          })
    )
    stats["Desviacion_precio"] = stats["Desviacion_precio"].fillna(0)
    stats["Rango_precio"]      = stats["Max_precio"] - stats["Min_precio"]

    return df_sum.merge(stats, on="Numero_cotizacion", how="left")

# Info básica a nivel de cotización (grano 1 fila por Nº)

def seleccionar_columns_basicas(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Numero_cotizacion", "Estado_cotizacion", "Solicitante_nit", "Latencia",
        "Grupo_clientes", "Zona", "Region", "Ciudad",
        "Punto_de_venta", "Representante_ventas_id",
    ]
    # Dejamos una sola fila por 'Numero_cotizacion' (la primera observación)
    return df.drop_duplicates("Numero_cotizacion")[cols]

# Categorías principales por cotización
#  - La categoría principal es la de mayor proporción de Importe
#  - En este flujo ya trabajamos con IDs (mapeo previo), por eso no aplicamos join/mapeo extra aquí.
#  - También calculamos diversidad (# categorías distintas).

def identificar_categorias_principales(df: pd.DataFrame) -> pd.DataFrame:
    df_tot = df.dropna(subset=["Importe_cotizacion"]).copy()

    # Proporción del importe por item dentro de la cotización
    total = df_tot.groupby("Numero_cotizacion")["Importe_cotizacion"].transform("sum")
    df_tot["Proporcion"] = df_tot["Importe_cotizacion"] / total

    # Índice del item con mayor proporción por cotización
    idx = df_tot.groupby("Numero_cotizacion")["Proporcion"].idxmax().dropna().astype(int)

    # Extraemos esas filas y renombramos
    cat_princ = (
        df_tot.loc[idx, ["Numero_cotizacion", "Negocio", "Grupo_articulos", "Categoria"]]
              .rename(columns={
                  "Negocio":         "Negocio_Principal",
                  "Grupo_articulos": "Grupo_Principal",
                  "Categoria":       "Categoria_Principal",
              })
              .copy()
    )

    # En este flujo ya son IDs numéricos
    cat_princ["Negocio_Principal_id"]   = cat_princ["Negocio_Principal"]
    cat_princ["Grupo_Principal_id"]     = cat_princ["Grupo_Principal"]
    cat_princ["Categoria_Principal_id"] = cat_princ["Categoria_Principal"]

    # Diversidad de categorías por cotización
    diversidad = (
        df.groupby("Numero_cotizacion")
          .agg({
              "Negocio":         "nunique",
              "Grupo_articulos": "nunique",
              "Categoria":       "nunique",
          })
          .rename(columns={
              "Negocio":         "Num_Negocios_Distintos",
              "Grupo_articulos": "Num_Grupos_Distintos",
              "Categoria":       "Num_Categorias_Distintas",
          })
          .reset_index()
    )

    return cat_princ.merge(diversidad, on="Numero_cotizacion", how="left")

# Pipeline de armado de dataset a nivel cotización

def procesar_nuevo_df(df: pd.DataFrame) -> pd.DataFrame:
    # 1) Derivados fila-a-fila
    df1     = ajustar_latencia(df)
    # 2) Un valor por cotización (variables “estáticas” y llaves)
    df_info = seleccionar_columns_basicas(df1)
    # 3) Agregados numéricos por cotización
    df_mets = agregar_metricas(df1)
    # 4) Categorías principales y diversidad
    df_cat  = identificar_categorias_principales(df1)

    # 5) Unión final a nivel 'Numero_cotizacion'
    df_final = (
        df_info
        .merge(df_mets, on="Numero_cotizacion", how="left")
        .merge(df_cat,  on="Numero_cotizacion", how="left")
    )
    return df_final

# 11 Ejecución

df_categ_procesado = procesar_nuevo_df(df_categ)

# Si quieres dejar solo IDs (y no los campos descriptivos):
df_categ_procesado = df_categ_procesado.drop(
    ["Negocio_Principal", "Grupo_Principal", "Categoria_Principal"],
    axis=1, errors="ignore"
)

print(df_categ_procesado.head())

# COMMAND ----------

# MAGIC %md
# MAGIC # 6. Carga de históricos (raw/hist)

# COMMAND ----------

def leer_hist_csvs(ruta_base: str) -> pd.DataFrame:
    # 1) Usa la ruta global de la celda 1 si existe
    hist_dir = globals().get("RAW_DIR_HIST")

    # 2) Fallbacks no intrusivos si no estás ejecutando desde el notebook “completo”
    if not hist_dir:
        # Si hay BASE global (celda 1), úsala
        base = globals().get("BASE", ruta_base)
        # Si existe helper _to_local, úsalo; si no, arma el path directo
        to_local = globals().get("_to_local", lambda p: p)
        hist_dir = to_local(os.path.join(base, "raw", "hist"))

    assert os.path.isdir(hist_dir), f"No existe carpeta hist_dir: {hist_dir}"

    columnas_finales = ["Solicitante_nit", "Fecha_pedido", "Pedido", "Valor"]
    dfs = []

    for fname in os.listdir(hist_dir):
        if not fname.lower().endswith(".csv"):
            continue

        path = os.path.join(hist_dir, fname)
        try:
            df = pd.read_csv(
                path,
                sep=":",
                engine="python",
                skiprows=2,
                header=None,
                quoting=csv.QUOTE_NONE,
                on_bad_lines="skip",
                encoding="utf-8",
            )

            if df.shape[1] < 5:
                print(f"{fname} ignorado: tiene {df.shape[1]} columnas (<5) después de skiprows.")
                continue

            df = df.drop(columns=[2])
            df.columns = columnas_finales

            df["Fecha_pedido"] = pd.to_datetime(df["Fecha_pedido"], format="%Y-%m-%d", errors="coerce").dt.date
            df["Valor"] = (
                df["Valor"].astype(str)
                           .str.replace(",", "", regex=False)
            )
            df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").round(1)

            dfs.append(df)

        except Exception as e:
            print(f"Error procesando {fname}: {e}")
            continue

    if not dfs:
        return pd.DataFrame(columns=columnas_finales)

    df_hist_0 = pd.concat(dfs, ignore_index=True)
    df_hist_0 = df_hist_0[~df_hist_0["Solicitante_nit"].isin(["(Vacío)", None])]
    df_hist_0 = df_hist_0.dropna(subset=["Solicitante_nit"]).reset_index(drop=True)
    return df_hist_0

# Uso recomendado: como ya se definio BASE y RAW_DIR_HIST en la celda 1, basta con:
df_hist_0 = leer_hist_csvs(BASE)
print(df_hist_0.head())
print("Filas históricas cargadas:", len(df_hist_0))

# COMMAND ----------

# MAGIC %md
# MAGIC # 7. Generar DF Historico

# COMMAND ----------

def generar_df_hist(df_hist_0: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega métricas históricas por 'Solicitante_nit' a partir de df_hist_0.

    Salida (una fila por Solicitante_nit):
      - Compras_hist:    conteo de pedidos únicos.
      - Monto_hist:      suma de 'Valor'.
      - Latencia_hist:   diferencia en días entre las 2 fechas de pedido más recientes.
                         Si solo hay 1 fecha válida, queda 0 (sin historial).
      - Valor_prom_hist: promedio del valor por pedido (Monto_hist / Compras_hist).

    Notas:
    - La función asume que df_hist_0 ya viene tipado (Fecha_pedido como fecha/ts y Valor numérico).
    - Es tolerante a NaNs en 'Fecha_pedido' y 'Valor'.
    """

    # 0) Validación temprana (fail fast con mensaje claro)
    cols_req = {"Solicitante_nit", "Fecha_pedido", "Pedido", "Valor"}
    faltan = cols_req - set(df_hist_0.columns)
    if faltan:
        raise ValueError(f"Faltan columnas requeridas en df_hist_0: {sorted(faltan)}")

    if df_hist_0.empty:
        # Devuelve DF vacío con el esquema correcto para no romper pipelines downstream
        return pd.DataFrame(columns=[
            "Solicitante_nit", "Compras_hist", "Monto_hist", "Latencia_hist", "Valor_prom_hist"
        ])

    # 1) Por si llegó algo sucio: aseguramos tipos "suaves"
    df = df_hist_0.copy()
    # Pedido a string para que nunique no se confunda con NaNs numéricos
    df["Pedido"] = df["Pedido"].astype(str)
    # Valor a numérico tolerante; NaN donde no se pueda convertir
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    # Fecha a datetime.date/NaT (si ya viene tipado, no pasa nada)
    df["Fecha_pedido"] = pd.to_datetime(df["Fecha_pedido"], errors="coerce").dt.date

    # 2) Agregaciones "fáciles" (todo menos la latencia)
    agg_basic = (
        df.groupby("Solicitante_nit")
          .agg(
              Compras_hist=("Pedido", "nunique"),
              Monto_hist=("Valor", "sum"),
          )
          .reset_index()
    )
    # Promedio por pedido (evita división por cero)
    agg_basic["Valor_prom_hist"] = agg_basic.apply(
        lambda r: (r["Monto_hist"] / r["Compras_hist"]) if r["Compras_hist"] > 0 else 0.0, axis=1
    )

    # 3) Latencia entre las dos fechas más recientes por cliente
    #    (si solo hay una fecha válida, definimos 0 por diseño)
    lat_rows = []
    for nit, g in df[["Solicitante_nit", "Fecha_pedido"]].dropna().groupby("Solicitante_nit"):
        # Fechas válidas ordenadas descendente y únicas (por si hay duplicados)
        fechas = pd.Series(sorted(set(g["Fecha_pedido"]), reverse=True))
        if len(fechas) >= 2:
            delta = (pd.to_datetime(fechas.iloc[0]) - pd.to_datetime(fechas.iloc[1])).days
            lat_rows.append((nit, int(max(delta, 0))))  # no-negativo por seguridad
        else:
            lat_rows.append((nit, 0))

    lat_df = pd.DataFrame(lat_rows, columns=["Solicitante_nit", "Latencia_hist"])

    # 4) Unimos todo
    df_hist = agg_basic.merge(lat_df, on="Solicitante_nit", how="left")
    df_hist["Latencia_hist"] = df_hist["Latencia_hist"].fillna(0).astype(int)

    # 5) Orden y tipos finales (opcional pero prolijo)
    df_hist = df_hist[
        ["Solicitante_nit", "Compras_hist", "Monto_hist", "Latencia_hist", "Valor_prom_hist"]
    ]
    df_hist["Compras_hist"] = df_hist["Compras_hist"].astype(int)
    df_hist["Monto_hist"] = df_hist["Monto_hist"].fillna(0.0).astype(float)
    df_hist["Valor_prom_hist"] = df_hist["Valor_prom_hist"].astype(float)

    return df_hist


# Uso
df_hist = generar_df_hist(df_hist_0)
print(df_hist.head())

# COMMAND ----------

# MAGIC %md
# MAGIC # 8. Unir Categorias e Historico

# COMMAND ----------

def unir_categ_y_hist(df_categ_emb: pd.DataFrame, df_hist: pd.DataFrame) -> pd.DataFrame:
    """
    Une df_categ_emb (características por cotización/cliente) con df_hist (métricas históricas por cliente)
    usando 'Solicitante_nit' como llave.

    - Left join: se preservan todas las filas de df_categ_emb.
    - Rellena faltantes post-join: 0 en métricas; 'Latencia_hist' con su máximo histórico.
    - Tolerante a:
        * Tipos distintos en la llave (castea a string)
        * Duplicados en df_hist (conserva la última ocurrencia por nit)
        * df_hist vacío (en ese caso, todo se rellena con 0)
    """
    # -------- 0) Validaciones de esquema --------
    req_hist = {"Solicitante_nit", "Compras_hist", "Monto_hist", "Latencia_hist", "Valor_prom_hist"}
    if not req_hist.issubset(df_hist.columns):
        faltan = sorted(req_hist - set(df_hist.columns))
        raise ValueError(f"Faltan columnas requeridas en df_hist: {faltan}")
    if "Solicitante_nit" not in df_categ_emb.columns:
        raise ValueError("Falta columna 'Solicitante_nit' en df_categ_emb.")

    # Copias para no mutar los originales
    left = df_categ_emb.copy()
    right = df_hist.copy()

    # -------- 1) Normalización de tipos en llave --------
    # Evita fallos de merge por dtype mismatch (int vs str, etc.)
    left["Solicitante_nit"]  = left["Solicitante_nit"].astype(str)
    right["Solicitante_nit"] = right["Solicitante_nit"].astype(str)

    # -------- 2) Asegurar unicidad en df_hist por Solicitante_nit --------
    # Por diseño df_hist debe tener 1 fila por nit; si hay duplicados, nos quedamos con la última.
    if right.duplicated(subset=["Solicitante_nit"]).any():
        right = right.sort_values("Solicitante_nit").drop_duplicates("Solicitante_nit", keep="last")

    # -------- 3) Tipificación "suave" en métricas (tolerante a entradas sucias) --------
    for c in ["Compras_hist"]:
        right[c] = pd.to_numeric(right[c], errors="coerce").fillna(0).astype(int)
    for c in ["Monto_hist", "Valor_prom_hist"]:
        right[c] = pd.to_numeric(right[c], errors="coerce").fillna(0.0).astype(float)
    right["Latencia_hist"] = pd.to_numeric(right["Latencia_hist"], errors="coerce")  # casteo final tras fill

    # -------- 4) Máximo de latencia para imputar faltantes tras el merge --------
    max_latencia = (
        right["Latencia_hist"].max() if not right["Latencia_hist"].dropna().empty else 0
    )

    # -------- 5) Merge (LEFT) --------
    out = left.merge(right, on="Solicitante_nit", how="left")

    # -------- 6) Relleno de faltantes post-join + tipos finales --------
    out["Compras_hist"]    = pd.to_numeric(out["Compras_hist"],    errors="coerce").fillna(0).astype(int)
    out["Monto_hist"]      = pd.to_numeric(out["Monto_hist"],      errors="coerce").fillna(0.0).astype(float)
    out["Valor_prom_hist"] = pd.to_numeric(out["Valor_prom_hist"], errors="coerce").fillna(0.0).astype(float)

    # Latencia: si no viene del histórico, usar el máximo observado (o 0 si no había histórico)
    out["Latencia_hist"]   = pd.to_numeric(out["Latencia_hist"], errors="coerce").fillna(max_latencia).astype(int)

    return out


# Aplicación
df_cat_hist = unir_categ_y_hist(df_categ_procesado, df_hist)

# Vista rápida
print(df_cat_hist.head())

# COMMAND ----------

# MAGIC %md
# MAGIC # 9. Inferencia de edad con modelo .pkl

# COMMAND ----------

import mlflow, numpy as np, pandas as pd

mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")

CATALOG, SCHEMA_REG, MODEL_NAME = "dev_arqanalitica", "machinelearning", "age_inference_cotiz"
MODEL_URI = f"models:/{CATALOG}.{SCHEMA_REG}.{MODEL_NAME}@champion"  # o '@candidate'

def inferir_edad_uc(df: pd.DataFrame, model_uri: str) -> pd.DataFrame:
    """
    Carga el modelo de UC por alias y predice Edad_inferida.
    - Garantiza input schema: CEDULA (int64) para los válidos
    - Imputa para los inválidos con la media de predicciones
    """
    model = mlflow.pyfunc.load_model(model_uri)
    out = df.copy()

    # 1) Extrae solo dígitos; evita floats/exp notation
    ced = out["Solicitante_nit"].astype(str).str.extract(r"(\d+)", expand=False)

    # 2) Válidos = tienen dígitos; construimos X con dtype int64
    valid_mask = ced.notna()
    X = pd.DataFrame({"CEDULA": ced[valid_mask].astype(np.int64)})

    # 3) Predicción solo para válidos
    preds = pd.Series(index=out.index, dtype="float64")
    if len(X):
        # Sanity check: debe ser int64
        assert X["CEDULA"].dtype == np.int64, f"dtype recibido: {X['CEDULA'].dtype}"
        preds.loc[valid_mask] = model.predict(X)

    # 4) Imputación para inválidos y post-proc
    fill_value = float(np.nanmean(preds)) if np.isfinite(np.nanmean(preds)) else 35.0
    preds = (
        preds.fillna(fill_value)
             .clip(0, 120)
             .round()
             .astype(int)
    )

    out["Edad_inferida"] = preds.values
    return out

# Uso
df_cat_hist_edad = inferir_edad_uc(df_cat_hist, MODEL_URI)
# (si mantienes esta regla)
df_cat_hist_edad = df_cat_hist_edad[df_cat_hist_edad["Latencia"] > 0].copy()

print(df_cat_hist_edad[["Solicitante_nit","Edad_inferida"]].head())


# COMMAND ----------

# MAGIC %md
# MAGIC # 10. Generamos tabla delta con resultado

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "dev_arqanalitica"
SCHEMA_ML = "machinelearning"
TABLE_NAME = "ds_cotiz_train_preproc_v1"   # <- nombre sugerido
FULL_TBL = f"{CATALOG}.{SCHEMA_ML}.{TABLE_NAME}"

# 1) Lleva el Pandas DF -> Spark DF y añade metadatos útiles
sdf = (spark.createDataFrame(df_cat_hist_edad)
          .withColumn("_ingested_at", F.current_timestamp())
          .withColumn("_source_note", F.lit("preprocess pipeline v1")))

# 2) Escritura idempotente (reemplaza versión previa manteniendo el esquema actualizado)
(sdf.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(FULL_TBL))

print(f"✓ Dataset guardado como tabla Delta: {FULL_TBL}")
display(spark.table(FULL_TBL).limit(10))

# chequeos rápidos
print("rows:", spark.table(FULL_TBL).count())
print("cols:", len(spark.table(FULL_TBL).columns))

# COMMAND ----------

# MAGIC %md
# MAGIC # 11. Publicar “artefactos” para downstream

# COMMAND ----------

# nombre final
OUTPUT_TABLE = "dev_arqanalitica.machinelearning.ds_cotiz_train_preproc_v1"
dbutils.jobs.taskValues.set(key="preproc_output_table", value=OUTPUT_TABLE)
rowcount = spark.table(OUTPUT_TABLE).count()
dbutils.jobs.taskValues.set(key="preproc_rowcount", value=str(rowcount))
print(f"[preprocess] escrito {OUTPUT_TABLE} con {rowcount} filas")
