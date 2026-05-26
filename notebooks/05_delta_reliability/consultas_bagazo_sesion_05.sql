-- Sesión 5 · Consultas Bagazo: lluvia, caña y operación
-- Granularidad: una fila por fecha e ingenio.

-- 1) Lluvia promedio por mes
SELECT
  year_month,
  ROUND(AVG(lluvia_mm), 2) AS lluvia_promedio_mm,
  ROUND(SUM(lluvia_mm), 2) AS lluvia_total_mm,
  COUNT(*) AS registros
FROM workspace.bagazo_silver.operacion_ingenios_clean
GROUP BY year_month
ORDER BY year_month;

-- 2) Bagazo promedio por mes
SELECT
  year_month,
  ROUND(AVG(bagazo_entregado_ton), 2) AS bagazo_promedio_ton,
  ROUND(SUM(bagazo_entregado_ton), 2) AS bagazo_total_ton,
  COUNT(*) AS registros
FROM workspace.bagazo_silver.operacion_ingenios_clean
GROUP BY year_month
ORDER BY year_month;

-- 3) Caña molida por ingenio
SELECT
  ingenio,
  ROUND(SUM(cana_molida_ton), 2) AS cana_total_ton,
  ROUND(AVG(cana_molida_ton), 2) AS cana_promedio_ton,
  COUNT(*) AS dias
FROM workspace.bagazo_silver.operacion_ingenios_clean
GROUP BY ingenio
ORDER BY cana_total_ton DESC;

-- 4) Bagazo entregado por ingenio
SELECT
  ingenio,
  ROUND(SUM(bagazo_entregado_ton), 2) AS bagazo_total_ton,
  ROUND(AVG(bagazo_entregado_ton), 2) AS bagazo_promedio_ton,
  SUM(CASE WHEN riesgo_bajo_bagazo THEN 1 ELSE 0 END) AS dias_riesgo_bajo
FROM workspace.bagazo_silver.operacion_ingenios_clean
GROUP BY ingenio
ORDER BY bagazo_total_ton DESC;

-- 5) Días con lluvia alta
SELECT
  fecha,
  ingenio,
  lluvia_mm,
  cana_molida_ton,
  bagazo_entregado_ton,
  comentario
FROM workspace.bagazo_silver.operacion_ingenios_clean
WHERE lluvia_alta = true
ORDER BY lluvia_mm DESC, fecha
LIMIT 50;

-- 6) Días con bajo bagazo
SELECT
  fecha,
  ingenio,
  lluvia_mm,
  cana_molida_ton,
  bagazo_entregado_ton,
  riesgo_bajo_bagazo,
  tiene_comentario_operativo,
  comentario
FROM workspace.bagazo_silver.operacion_ingenios_clean
WHERE riesgo_bajo_bagazo = true
ORDER BY fecha, ingenio
LIMIT 50;

-- 7) Promedio de bagazo en días secos vs lluviosos
SELECT
  ingenio,
  CASE WHEN lluvia_alta THEN 'Día con lluvia alta' ELSE 'Día sin lluvia alta' END AS tipo_dia,
  COUNT(*) AS dias,
  ROUND(AVG(lluvia_mm), 2) AS lluvia_promedio_mm,
  ROUND(AVG(cana_molida_ton), 2) AS cana_promedio_ton,
  ROUND(AVG(bagazo_entregado_ton), 2) AS bagazo_promedio_ton
FROM workspace.bagazo_silver.operacion_ingenios_clean
GROUP BY ingenio, CASE WHEN lluvia_alta THEN 'Día con lluvia alta' ELSE 'Día sin lluvia alta' END
ORDER BY ingenio, tipo_dia;

-- 8) Correlación simple por ingenio
SELECT
  ingenio,
  COUNT(*) AS observaciones,
  ROUND(CORR(lluvia_mm, bagazo_entregado_ton), 4) AS corr_lluvia_bagazo,
  ROUND(CORR(cana_molida_ton, bagazo_entregado_ton), 4) AS corr_cana_bagazo,
  ROUND(CORR(lluvia_mm, cana_molida_ton), 4) AS corr_lluvia_cana
FROM workspace.bagazo_silver.operacion_ingenios_clean
GROUP BY ingenio
ORDER BY ingenio;

-- 9) Comparación mensual lluvia vs bagazo
SELECT
  year_month,
  ingenio,
  ROUND(AVG(lluvia_mm), 2) AS lluvia_promedio_mm,
  ROUND(AVG(cana_molida_ton), 2) AS cana_promedio_ton,
  ROUND(AVG(bagazo_entregado_ton), 2) AS bagazo_promedio_ton,
  SUM(CASE WHEN riesgo_bajo_bagazo THEN 1 ELSE 0 END) AS dias_riesgo_bajo
FROM workspace.bagazo_silver.operacion_ingenios_clean
GROUP BY year_month, ingenio
ORDER BY year_month, ingenio;

-- 10) Días críticos explicados por comentarios operativos
SELECT
  fecha,
  ingenio,
  lluvia_mm,
  cana_molida_ton,
  bagazo_entregado_ton,
  es_mantenimiento,
  es_falta_cana_por_lluvia,
  es_paro,
  es_sin_recepcion_bagazo,
  comentario
FROM workspace.bagazo_silver.operacion_ingenios_clean
WHERE riesgo_bajo_bagazo = true
  AND tiene_comentario_operativo = true
ORDER BY fecha, ingenio
LIMIT 50;
