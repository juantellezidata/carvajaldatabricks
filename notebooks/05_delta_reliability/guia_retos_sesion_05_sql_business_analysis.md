# Guía de retos — Sesión 5 Databricks SQL de negocio y análisis operativo

## Propósito

Reforzar SQL aplicado en Databricks sobre tablas Silver, cuidando granularidad, joins y traducción de resultados a insights ejecutivos.

---

## Reto Nivel 1 — Refuerzo SQL

**Objetivo:** practicar filtros, agregaciones y ordenamiento.

**Tiempo estimado:** 10 a 15 minutos.

**Nivel:** básico.

**Instrucciones:** elige una de estas opciones:

1. Identifica los 10 estados con más pedidos entregados.
2. Identifica las 10 categorías con mayor review promedio, considerando solo categorías con al menos 50 pedidos.

**Resultado esperado:** una tabla ordenada con el ranking solicitado.

**Pistas:** usa `COUNT(DISTINCT order_id)`, `GROUP BY`, `ORDER BY` y `LIMIT`.

**Criterios de evaluación:**

- La consulta ejecuta sin errores.
- Usa filtros coherentes.
- Evita contar pedidos duplicados.
- Ordena correctamente el resultado.

---

## Reto Nivel 2 — Análisis cruzado

**Objetivo:** combinar ventas, demora y review por categoría sin duplicar métricas.

**Tiempo estimado:** 20 a 25 minutos.

**Nivel:** intermedio.

**Instrucciones:** crea una consulta con CTEs que entregue, por categoría:

- pedidos,
- venta total,
- demora promedio,
- review promedio.

**Resultado esperado:** una tabla de categorías priorizadas por venta total y satisfacción.

**Pistas:**

- Calcula ventas desde `order_items_clean`.
- Calcula reviews agregando primero por `order_id`.
- Usa `SELECT DISTINCT order_id, categoria` cuando cruces categorías con pedidos.
- No sumes `total_payment_value` después de unir contra ítems.

**Criterios de evaluación:**

- Usa CTEs legibles.
- Respeta la granularidad.
- No duplica pagos ni pedidos.
- Produce una salida interpretable para negocio.

---

## Reto consultor — Insight ejecutivo

**Objetivo:** transformar consultas SQL en recomendaciones accionables.

**Tiempo estimado:** 20 minutos.

**Nivel:** consultor.

**Instrucciones:** cada grupo entrega 3 insights usando el formato:

```text
Insight:
Evidencia:
Impacto operativo o de negocio:
Recomendación:
Consulta SQL usada:
```

**Resultado esperado:** 3 conclusiones ejecutivas sustentadas en SQL.

**Pistas:**

- No basta con decir “la venta sube” o “hay lluvia alta”.
- La evidencia debe venir de una consulta específica.
- La recomendación debe conectar con una acción de negocio u operación.

**Criterios de evaluación:**

- Hay relación clara entre insight y evidencia.
- La consulta es correcta.
- La recomendación es concreta.
- Se evita afirmar causalidad cuando solo hay correlación.

---

# Soluciones esperadas

## Solución Nivel 1 — Estados con más pedidos entregados

```sql
SELECT
  c.customer_state,
  COUNT(DISTINCT o.order_id) AS pedidos_entregados
FROM workspace.lumi_silver.orders_clean o
LEFT JOIN workspace.lumi_silver.customers_clean c
  ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY pedidos_entregados DESC
LIMIT 10;
```

## Solución Nivel 1 — Categorías con mayor review promedio

```sql
WITH reviews_by_order AS (
  SELECT order_id, AVG(review_score) AS review_promedio_pedido
  FROM workspace.lumi_silver.reviews_clean
  GROUP BY order_id
),
category_orders AS (
  SELECT DISTINCT
    oi.order_id,
    COALESCE(p.product_category_clean, 'sin_categoria') AS categoria
  FROM workspace.lumi_silver.order_items_clean oi
  LEFT JOIN workspace.lumi_silver.products_clean p
    ON oi.product_id = p.product_id
)
SELECT
  co.categoria,
  COUNT(DISTINCT co.order_id) AS pedidos,
  ROUND(AVG(r.review_promedio_pedido), 2) AS review_promedio
FROM category_orders co
LEFT JOIN reviews_by_order r
  ON co.order_id = r.order_id
GROUP BY co.categoria
HAVING COUNT(DISTINCT co.order_id) >= 50
ORDER BY review_promedio DESC, pedidos DESC
LIMIT 10;
```

## Solución Nivel 2 — Ventas, demora y review por categoría

```sql
WITH ventas_categoria AS (
  SELECT
    COALESCE(p.product_category_clean, 'sin_categoria') AS categoria,
    COUNT(DISTINCT oi.order_id) AS pedidos,
    SUM(oi.total_item_value) AS venta_total
  FROM workspace.lumi_silver.order_items_clean oi
  INNER JOIN workspace.lumi_silver.orders_clean o
    ON oi.order_id = o.order_id
  LEFT JOIN workspace.lumi_silver.products_clean p
    ON oi.product_id = p.product_id
  WHERE o.order_status = 'delivered'
  GROUP BY COALESCE(p.product_category_clean, 'sin_categoria')
),
reviews_by_order AS (
  SELECT order_id, AVG(review_score) AS review_promedio_pedido
  FROM workspace.lumi_silver.reviews_clean
  GROUP BY order_id
),
category_orders AS (
  SELECT DISTINCT
    oi.order_id,
    COALESCE(p.product_category_clean, 'sin_categoria') AS categoria,
    o.delay_days,
    r.review_promedio_pedido
  FROM workspace.lumi_silver.order_items_clean oi
  INNER JOIN workspace.lumi_silver.orders_clean o
    ON oi.order_id = o.order_id
  LEFT JOIN workspace.lumi_silver.products_clean p
    ON oi.product_id = p.product_id
  LEFT JOIN reviews_by_order r
    ON oi.order_id = r.order_id
  WHERE o.order_status = 'delivered'
),
experiencia_categoria AS (
  SELECT
    categoria,
    AVG(delay_days) AS demora_promedio,
    AVG(review_promedio_pedido) AS review_promedio
  FROM category_orders
  GROUP BY categoria
)
SELECT
  v.categoria,
  v.pedidos,
  ROUND(v.venta_total, 2) AS venta_total,
  ROUND(e.demora_promedio, 2) AS demora_promedio,
  ROUND(e.review_promedio, 2) AS review_promedio
FROM ventas_categoria v
LEFT JOIN experiencia_categoria e
  ON v.categoria = e.categoria
WHERE v.pedidos >= 100
ORDER BY venta_total DESC
LIMIT 20;
```

## Solución Reto consultor — Ejemplo

```text
Insight: Algunas categorías combinan venta alta con satisfacción baja.
Evidencia: La consulta de categorías críticas muestra venta total alta y review promedio menor a 4.0.
Impacto operativo o de negocio: Riesgo de devoluciones, reclamos y pérdida de recompra.
Recomendación: Revisar tiempos de entrega, calidad de producto y desempeño de vendedores asociados a esas categorías.
Consulta SQL usada: Categorías con alta venta y baja satisfacción.
```
