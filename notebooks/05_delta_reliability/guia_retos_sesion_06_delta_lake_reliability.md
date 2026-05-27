# Guía de retos — Sesión 6: Delta Lake, versionado, historia y confiabilidad

## Propósito

Reforzar el uso de `DESCRIBE HISTORY`, Time Travel, comparación de versiones y checklist de confiabilidad antes de construir Gold.

---

## Reto Nivel 1 — Historia de tabla

**Objetivo:** interpretar la historia de una tabla Delta.

**Tiempo estimado:** 10 minutos  
**Nivel:** básico

### Instrucciones

1. Elige una tabla de laboratorio:
   - `workspace.delta_lab.orders_reliability_lab`
   - `workspace.delta_lab.bagazo_reliability_lab`
2. Ejecuta `DESCRIBE HISTORY`.
3. Identifica:
   - versión inicial;
   - última versión;
   - última operación;
   - usuario o notebook asociado si aparece;
   - métricas de operación disponibles.

### Resultado esperado

```text
Tabla:
Versión inicial:
Última versión:
Última operación:
Evidencia observada:
Conclusión:
```

### Pistas

- Revisa las columnas `version`, `timestamp`, `operation`, `operationParameters` y `operationMetrics`.
- Recuerda que `RESTORE` también aparece como operación.

### Criterios de evaluación

- Identifica correctamente la operación más reciente.
- Diferencia historia técnica de validación de calidad.
- Explica por qué la evidencia importa para un dashboard o KPI.

---

## Reto Nivel 2 — Time Travel y comparación

**Objetivo:** comparar una versión anterior con la versión actual.

**Tiempo estimado:** 15 minutos  
**Nivel:** intermedio

### Instrucciones

1. Elige una tabla lab.
2. Consulta una versión anterior con `VERSION AS OF`.
3. Consulta la versión actual.
4. Compara al menos un registro.
5. Explica qué cambió y qué evidencia usarías para justificarlo.

### Resultado esperado

Una consulta SQL con CTEs y una conclusión breve.

### Pistas

- Para Lumi puedes usar `order_id`.
- Para Bagazo puedes usar `fecha + ingenio`.
- Si no sabes qué versión consultar, revisa primero `DESCRIBE HISTORY`.

### Criterios de evaluación

- Usa correctamente `VERSION AS OF`.
- La comparación evita modificar Silver real.
- La conclusión conecta la diferencia con auditoría o confiabilidad.

---

## Reto consultor — Checklist de confiabilidad pre-Gold

**Objetivo:** decidir si una tabla puede alimentar Gold.

**Tiempo estimado:** 20 minutos  
**Nivel:** consultor

### Instrucciones

Completa el siguiente formato para una tabla Silver o lab.

```text
Tabla:
Propósito analítico:
Última versión revisada:
Operaciones recientes:
Riesgos detectados:
¿Puede alimentar Gold?: Sí / No / Con observaciones
Evidencia SQL usada:
Recomendación:
```

### Resultado esperado

Una recomendación ejecutiva sustentada en evidencia SQL.

### Criterios de evaluación

- Usa evidencia de `DESCRIBE HISTORY` o `DESCRIBE DETAIL`.
- Incluye riesgos de calidad si existen.
- No confunde auditoría técnica con validación de calidad.
- Entrega una recomendación clara para Sesión 7.

---

# Soluciones esperadas

## Solución orientativa — Nivel 1

```sql
DESCRIBE HISTORY workspace.delta_lab.orders_reliability_lab;
```

Lectura esperada:

```text
Tabla: workspace.delta_lab.orders_reliability_lab
Versión inicial: 0
Última versión: depende de la ejecución
Última operación: puede ser UPDATE o RESTORE
Evidencia observada: operation, timestamp, userName, operationMetrics
Conclusión: la tabla permite auditar cambios antes de alimentar Gold.
```

## Solución orientativa — Nivel 2

```sql
WITH actual AS (
  SELECT order_id, order_status, delay_days
  FROM workspace.delta_lab.orders_reliability_lab
  WHERE order_id = (SELECT order_id FROM v_order_lab_candidate)
), inicial AS (
  SELECT order_id, order_status, delay_days
  FROM workspace.delta_lab.orders_reliability_lab VERSION AS OF 0
  WHERE order_id = (SELECT order_id FROM v_order_lab_candidate)
)
SELECT
  a.order_id,
  i.order_status AS order_status_inicial,
  a.order_status AS order_status_actual,
  i.delay_days AS delay_days_inicial,
  a.delay_days AS delay_days_actual
FROM actual a
JOIN inicial i USING(order_id);
```

## Solución orientativa — Reto consultor

```text
Tabla: workspace.lumi_silver.orders_clean
Propósito analítico: alimentar KPIs de pedidos, entregas y demoras.
Última versión revisada: revisar DESCRIBE HISTORY.
Operaciones recientes: creación/carga Silver; sin modificación directa en Sesión 6.
Riesgos detectados: revisar joins con pagos, ítems y reviews para evitar doble conteo.
¿Puede alimentar Gold?: Sí, con observaciones de granularidad.
Evidencia SQL usada: DESCRIBE DETAIL, DESCRIBE HISTORY, quality_summary_sesion_04.
Recomendación: usar como base de fact_orders y fact_delivery en Sesión 7.
```
