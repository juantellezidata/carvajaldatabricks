-- Sesión 5 · Salud de Silver
SELECT *
FROM workspace.control.quality_summary_sesion_04
ORDER BY dataset, tabla;

SELECT estado_calidad, COUNT(*) AS tablas
FROM workspace.control.quality_summary_sesion_04
GROUP BY estado_calidad
ORDER BY tablas DESC;

SELECT dataset, tabla, filas, columnas, duplicados_clave, reglas_fallidas, estado_calidad, observaciones
FROM workspace.control.quality_summary_sesion_04
WHERE estado_calidad <> 'OK'
ORDER BY dataset, tabla;


-- Sesión 5 · Consultas Lumi Commerce Lakehouse
-- Nota: usar tablas Silver; no crear Gold formal en esta sesión.

-- 1) Ventas por mes, usando granularidad de ítem
WITH ventas_item AS (
  SELECT
    o.year_month,
    oi.order_id,
    oi.order_item_id,
    oi.total_item_value
  FROM workspace.lumi_silver.order_items_clean oi
  INNER JOIN workspace.lumi_silver.orders_clean o
    ON oi.order_id = o.order_id
  WHERE o.order_status = 'delivered'
)
SELECT
  year_month,
  COUNT(DISTINCT order_id) AS pedidos_entregados,
  COUNT(*) AS items_vendidos,
  ROUND(SUM(total_item_value), 2) AS venta_total_items,
  ROUND(AVG(total_item_value), 2) AS valor_promedio_item
FROM ventas_item
GROUP BY year_month
ORDER BY year_month;

-- 2) Ticket promedio por pedido, usando pagos consolidados por order_id
SELECT
  o.year_month,
  COUNT(DISTINCT o.order_id) AS pedidos_entregados,
  ROUND(SUM(COALESCE(p.total_payment_value, 0)), 2) AS valor_pagado_total,
  ROUND(AVG(COALESCE(p.total_payment_value, 0)), 2) AS ticket_promedio_pedido
FROM workspace.lumi_silver.orders_clean o
LEFT JOIN workspace.lumi_silver.payments_clean p
  ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.year_month
ORDER BY o.year_month;

-- 3) Pedidos por estado
SELECT
  order_status,
  COUNT(*) AS pedidos,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje
FROM workspace.lumi_silver.orders_clean
GROUP BY order_status
ORDER BY pedidos DESC;

-- 4) Ventas por categoría, usando granularidad de ítem
WITH ventas_categoria AS (
  SELECT
    COALESCE(p.product_category_clean, 'sin_categoria') AS categoria,
    oi.order_id,
    oi.order_item_id,
    oi.total_item_value
  FROM workspace.lumi_silver.order_items_clean oi
  INNER JOIN workspace.lumi_silver.orders_clean o
    ON oi.order_id = o.order_id
  LEFT JOIN workspace.lumi_silver.products_clean p
    ON oi.product_id = p.product_id
  WHERE o.order_status = 'delivered'
)
SELECT
  categoria,
  COUNT(DISTINCT order_id) AS pedidos,
  COUNT(*) AS items,
  ROUND(SUM(total_item_value), 2) AS venta_total,
  ROUND(AVG(total_item_value), 2) AS valor_promedio_item
FROM ventas_categoria
GROUP BY categoria
ORDER BY venta_total DESC
LIMIT 20;

-- 5) Métodos de pago y valor total pagado
SELECT
  main_payment_type,
  COUNT(*) AS pedidos,
  ROUND(SUM(total_payment_value), 2) AS valor_total_pagado,
  ROUND(AVG(total_payment_value), 2) AS ticket_promedio
FROM workspace.lumi_silver.payments_clean
GROUP BY main_payment_type
ORDER BY valor_total_pagado DESC;

-- 6) Reviews por categoría: agregar reviews por order_id antes del cruce
WITH reviews_by_order AS (
  SELECT
    order_id,
    ROUND(AVG(review_score), 2) AS review_promedio_pedido,
    MAX(CASE WHEN is_low_review THEN 1 ELSE 0 END) AS tiene_review_bajo
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
  COUNT(DISTINCT co.order_id) AS pedidos_con_categoria,
  ROUND(AVG(r.review_promedio_pedido), 2) AS review_promedio,
  SUM(CASE WHEN r.tiene_review_bajo = 1 THEN 1 ELSE 0 END) AS pedidos_con_review_bajo
FROM category_orders co
LEFT JOIN reviews_by_order r
  ON co.order_id = r.order_id
GROUP BY co.categoria
HAVING COUNT(DISTINCT co.order_id) >= 50
ORDER BY review_promedio ASC, pedidos_con_categoria DESC
LIMIT 20;

-- 7) Entregas tardías
SELECT
  year_month,
  COUNT(*) AS pedidos_entregados,
  SUM(CASE WHEN is_late THEN 1 ELSE 0 END) AS pedidos_tarde,
  ROUND(100.0 * SUM(CASE WHEN is_late THEN 1 ELSE 0 END) / COUNT(*), 2) AS tasa_entrega_tarde,
  ROUND(AVG(delay_days), 2) AS demora_promedio_dias
FROM workspace.lumi_silver.orders_clean
WHERE order_status = 'delivered'
GROUP BY year_month
ORDER BY year_month;

-- 8) Relación entre demora y review
WITH reviews_by_order AS (
  SELECT
    order_id,
    ROUND(AVG(review_score), 2) AS review_promedio_pedido
  FROM workspace.lumi_silver.reviews_clean
  GROUP BY order_id
)
SELECT
  CASE
    WHEN o.delay_days <= 0 THEN 'A tiempo o antes'
    WHEN o.delay_days BETWEEN 1 AND 3 THEN '1 a 3 días tarde'
    WHEN o.delay_days BETWEEN 4 AND 7 THEN '4 a 7 días tarde'
    ELSE 'Más de 7 días tarde'
  END AS tramo_demora,
  COUNT(DISTINCT o.order_id) AS pedidos,
  ROUND(AVG(o.delay_days), 2) AS demora_promedio,
  ROUND(AVG(r.review_promedio_pedido), 2) AS review_promedio
FROM workspace.lumi_silver.orders_clean o
LEFT JOIN reviews_by_order r
  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY tramo_demora
ORDER BY demora_promedio;

-- 9) Ranking de vendedores
SELECT
  s.seller_id,
  s.seller_state,
  COUNT(DISTINCT oi.order_id) AS pedidos,
  COUNT(*) AS items,
  ROUND(SUM(oi.total_item_value), 2) AS venta_total,
  ROUND(AVG(oi.total_item_value), 2) AS valor_promedio_item
FROM workspace.lumi_silver.order_items_clean oi
INNER JOIN workspace.lumi_silver.orders_clean o
  ON oi.order_id = o.order_id
LEFT JOIN workspace.lumi_silver.sellers_clean s
  ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
GROUP BY s.seller_id, s.seller_state
ORDER BY venta_total DESC
LIMIT 20;

-- 10) Categorías con alta venta y baja satisfacción
WITH ventas_categoria AS (
  SELECT
    COALESCE(p.product_category_clean, 'sin_categoria') AS categoria,
    COUNT(DISTINCT oi.order_id) AS pedidos,
    ROUND(SUM(oi.total_item_value), 2) AS venta_total
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
    COALESCE(p.product_category_clean, 'sin_categoria') AS categoria
  FROM workspace.lumi_silver.order_items_clean oi
  LEFT JOIN workspace.lumi_silver.products_clean p
    ON oi.product_id = p.product_id
),
reviews_categoria AS (
  SELECT
    co.categoria,
    ROUND(AVG(r.review_promedio_pedido), 2) AS review_promedio
  FROM category_orders co
  LEFT JOIN reviews_by_order r
    ON co.order_id = r.order_id
  GROUP BY co.categoria
)
SELECT
  v.categoria,
  v.pedidos,
  v.venta_total,
  r.review_promedio,
  CASE
    WHEN v.venta_total >= 100000 AND r.review_promedio < 4.0 THEN 'Alta prioridad'
    WHEN v.venta_total >= 50000 AND r.review_promedio < 4.0 THEN 'Revisar'
    ELSE 'Monitorear'
  END AS prioridad_analitica
FROM ventas_categoria v
LEFT JOIN reviews_categoria r
  ON v.categoria = r.categoria
WHERE v.pedidos >= 100
ORDER BY prioridad_analitica, v.venta_total DESC, r.review_promedio ASC
LIMIT 25;
