# Guía de retos — Sesión 3: Exploración de datos con PySpark

## Contexto

Los retos refuerzan lo trabajado durante la sesión sin interrumpir el flujo principal. Se resuelven al final usando las tablas Bronze y los DataFrames creados en el notebook.

---

## Reto Nivel 1 — Inventario Bronze

**Objetivo:** validar que el estudiante entendió cómo inspeccionar tablas y conteos básicos.  
**Tiempo estimado:** 10 minutos.  
**Nivel:** básico.

### Instrucciones

Usa `inventory_df` para identificar:

1. Tabla con más filas.
2. Tabla con menos filas.
3. Tabla con más columnas.

### Resultado esperado

Un DataFrame con columnas similares a:

```text
proyecto | schema | tabla | filas | columnas | observacion
```

### Pistas

- Usa `orderBy(F.desc("filas"))`.
- Usa `limit(1)`.
- Puedes unir resultados con `unionByName`.

### Criterios de evaluación

- Identifica correctamente las tres observaciones.
- Usa operaciones PySpark, no conteos manuales.
- Presenta el resultado en una tabla legible.

### Solución esperada

```python
mas_filas = inventory_df.orderBy(F.desc("filas")).limit(1).withColumn("observacion", F.lit("tabla_con_mas_filas"))
menos_filas = inventory_df.orderBy(F.asc("filas")).limit(1).withColumn("observacion", F.lit("tabla_con_menos_filas"))
mas_columnas = inventory_df.orderBy(F.desc("columnas")).limit(1).withColumn("observacion", F.lit("tabla_con_mas_columnas"))
solucion_reto_1 = mas_filas.unionByName(menos_filas).unionByName(mas_columnas)
display(solucion_reto_1)
```

---

## Reto Nivel 2 — Métricas comerciales Lumi

**Objetivo:** extender el análisis exploratorio de Lumi con métricas de negocio.  
**Tiempo estimado:** 20 minutos.  
**Nivel:** intermedio.

### Instrucciones

Calcula:

1. Ventas por mes.
2. Ticket promedio por pedido.
3. Top 10 categorías.
4. Top 10 estados por ventas.
5. Review promedio general.

### Resultado esperado

Entre 3 y 5 DataFrames listos para discusión.

### Pistas

- Usa `sales_lumi_exploratory`.
- Para estados, une con `customers_bz`.
- Para reviews, usa `order_reviews_bz`.
- Filtra órdenes `delivered` cuando midas ventas.

### Criterios de evaluación

- Usa joins correctamente.
- Calcula agregaciones con `groupBy` y `agg`.
- Diferencia conteo de pedidos de conteo de items.
- Presenta resultados ordenados.

### Solución esperada

```python
ventas_mensuales = (
    sales_lumi_exploratory
    .filter(F.col("order_status") == "delivered")
    .groupBy("year_month")
    .agg(
        F.countDistinct("order_id").alias("pedidos"),
        F.round(F.sum("total_item_value"), 2).alias("ventas_estimadas")
    )
    .orderBy("year_month")
)

ticket_promedio = (
    sales_lumi_exploratory
    .filter(F.col("order_status") == "delivered")
    .groupBy("year_month")
    .agg(F.round(F.sum("total_item_value") / F.countDistinct("order_id"), 2).alias("ticket_promedio_pedido"))
)

top_estados = (
    sales_lumi_exploratory
    .join(customers_bz.select("customer_id", "customer_state"), on="customer_id", how="left")
    .filter(F.col("order_status") == "delivered")
    .groupBy("customer_state")
    .agg(
        F.countDistinct("order_id").alias("pedidos"),
        F.round(F.sum("total_item_value"), 2).alias("ventas_estimadas")
    )
    .orderBy(F.desc("ventas_estimadas"))
)

review_promedio = order_reviews_bz.agg(F.round(F.avg("review_score"), 2).alias("review_promedio"))
```

---

## Reto consultor — Hallazgos ejecutivos

**Objetivo:** conectar la exploración técnica con una conversación de negocio, gobierno y calidad.  
**Tiempo estimado:** 15 minutos.  
**Nivel:** consultor.

### Instrucciones

Construye 3 hallazgos con esta estructura:

```text
Insight:
Evidencia:
Riesgo o impacto:
Recomendación:
Tabla o consulta usada:
```

Incluye al menos:

- 1 hallazgo de Lumi.
- 1 hallazgo de Bagazo.
- 1 hallazgo de calidad o gobierno.

### Resultado esperado

Tres hallazgos ejecutivos claros, sustentados en resultados observables del notebook.

### Pistas

- Evita decir “hay problema” sin evidencia.
- Usa métricas, conteos o rankings como soporte.
- Distingue entre dato observado e inferencia.

### Criterios de evaluación

- El insight es claro.
- La evidencia viene de una tabla o consulta.
- La recomendación es accionable.
- Se conecta con Silver o con decisiones de negocio.

### Solución esperada

```text
Insight: Lumi concentra ventas exploratorias en pocas categorías.
Evidencia: El ranking `categorias_top` muestra concentración en el top 10.
Riesgo o impacto: Categorías nulas o mal traducidas pueden afectar KPIs comerciales.
Recomendación: En Silver, traducir categorías y crear regla para `sin_categoria`.
Tabla o consulta usada: categorias_top.
```

```text
Insight: Bagazo debe pasar a formato largo antes de analítica avanzada.
Evidencia: La tabla Bronze tiene variables separadas por ingenio en columnas distintas.
Riesgo o impacto: El formato ancho dificulta comparar ingenios, generar features y entrenar modelos.
Recomendación: Persistir una tabla Silver con fecha, ingenio, lluvia, caña, bagazo y comentario.
Tabla o consulta usada: bagazo_long_exploratory.
```

```text
Insight: Los ceros operativos no deben tratarse automáticamente como datos inválidos.
Evidencia: Existen días con caña o bagazo cero y comentarios como mantenimiento o paro.
Riesgo o impacto: Eliminar esos registros sin criterio podría borrar eventos reales relevantes.
Recomendación: Crear banderas de calidad y de evento operativo en Silver.
Tabla o consulta usada: metricas_por_ingenio / comentarios_operativos.
```