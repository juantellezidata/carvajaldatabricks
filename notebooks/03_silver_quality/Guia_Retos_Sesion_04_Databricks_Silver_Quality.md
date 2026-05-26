# Guía de retos — Sesión 4 Databricks: Limpieza, calidad y capa Silver

## Propósito
Estos retos refuerzan la construcción de la capa Silver sin interrumpir el flujo principal de clase.

---

## Reto nivel 1 — Validación adicional Lumi
**Objetivo:** validar que el estudiante entendió el contrato mínimo de calidad.  
**Tiempo:** 10-15 min.  
**Nivel:** básico.

### Instrucciones
Usa `workspace.lumi_silver.products_clean` y crea una validación para detectar productos con peso o dimensiones negativas.

### Resultado esperado
Un conteo de registros problemáticos y una muestra de registros si existen.

### Pistas
Revisa: `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`.

### Criterios de evaluación
- La consulta se ejecuta sin error.
- La condición usa columnas numéricas ya tipadas en Silver.
- El resultado diferencia valor negativo, cero y nulo.

### Solución esperada
```python
products_clean = spark.table("workspace.lumi_silver.products_clean")
products_dimension_issues = products_clean.filter(
    (F.col("product_weight_g") < 0) |
    (F.col("product_length_cm") < 0) |
    (F.col("product_height_cm") < 0) |
    (F.col("product_width_cm") < 0)
)
print("Productos con dimensiones o peso negativo:", products_dimension_issues.count())
display(products_dimension_issues)
```

---

## Reto nivel 2 — Extender la tabla de calidad
**Objetivo:** enriquecer `quality_summary_sesion_04` con una métrica adicional.  
**Tiempo:** 15-20 min.  
**Nivel:** intermedio.

### Instrucciones
Agrega una métrica calculada como porcentaje, por ejemplo `porcentaje_nulos_criticos` o `porcentaje_reglas_fallidas`.

### Resultado esperado
Un DataFrame extendido que permita comparar severidad entre tablas de distinto tamaño.

### Pistas
No compares solo conteos absolutos. Una tabla de 1 millón de filas y otra de 100 filas no deben interpretarse igual.

### Criterios de evaluación
- Evita división por cero.
- Preserva columnas originales.
- El resultado es interpretable para negocio o gobierno de datos.

### Solución esperada
```python
quality_summary_df = spark.table("workspace.control.quality_summary_sesion_04")
quality_summary_extended = (
    quality_summary_df
    .withColumn("porcentaje_nulos_criticos", F.round(F.col("nulos_criticos") / F.greatest(F.col("filas"), F.lit(1)) * 100, 4))
    .withColumn("porcentaje_reglas_fallidas", F.round(F.col("reglas_fallidas") / F.greatest(F.col("filas"), F.lit(1)) * 100, 4))
)
display(quality_summary_extended)
```

---

## Reto consultor — Explicación ejecutiva
**Objetivo:** conectar calidad técnica con riesgo de negocio.  
**Tiempo:** 10 min.  
**Nivel:** consultor.

### Instrucciones
Redacta una explicación para gerencia: ¿por qué no se debe construir un dashboard Gold directamente desde Bronze?

### Resultado esperado
Un párrafo ejecutivo claro, sin tecnicismos innecesarios.

### Criterios de evaluación
- Conecta técnica con negocio.
- Menciona trazabilidad y gobierno.
- Explica el rol de Silver como contrato mínimo de calidad.

### Solución esperada
No conviene construir un dashboard Gold directamente desde Bronze porque Bronze conserva los datos tal como llegaron: pueden tener fechas como texto, pagos duplicados por pedido, categorías sin traducción, formatos numéricos regionales, nulos críticos y señales operativas no estructuradas. Si negocio consume directamente Bronze, los KPIs pueden ser inconsistentes o contradictorios. Silver actúa como contrato mínimo de confianza antes de que los datos se conviertan en métricas ejecutivas.