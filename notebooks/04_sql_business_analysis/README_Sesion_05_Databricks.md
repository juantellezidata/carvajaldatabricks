# README — Sesión 5 Databricks: SQL de negocio y análisis operativo

## Entregables incluidos

```text
notebooks/04_sql_business_analysis/05_estudiante_sql_business_analysis.ipynb
notebooks/04_sql_business_analysis/05_instructor_sql_business_analysis_solucionado.ipynb
docs/guia_retos_sesion_05_sql_business_analysis.md
docs/referencias_oficiales_databricks_sesion_05.md
sql/04_sql_business_analysis/consultas_lumi_sesion_05.sql
sql/04_sql_business_analysis/consultas_bagazo_sesion_05.sql
deliverables/Presentacion_Sesion_05_Databricks_SQL_Business_Analysis.pptx
```

## Objetivo de la sesión

Usar SQL en Databricks para convertir la capa Silver en evidencia analítica, responder preguntas de negocio de Lumi y preguntas operativas del caso Bagazo, cuidando granularidad, joins, agregaciones y calidad de datos.

## Preparación previa del instructor

- Confirmar que la Sesión 4 fue ejecutada.
- Validar existencia de `workspace.control.quality_summary_sesion_04`.
- Validar existencia de las tablas Silver de Lumi y Bagazo.
- Abrir primero el notebook instructor y luego el estudiante.
- Revisar el estado `REVISAR` de `reviews_clean` para usarlo como conversación pedagógica.
- Tener claro que no se crea Gold formal en esta sesión.

## Checklist para estudiantes

- Abrir Databricks Free Edition.
- Importar el notebook estudiante.
- Verificar acceso al catálogo `workspace`.
- Ejecutar las consultas en orden.
- No saltarse el bloque de granularidad.
- Completar los TODOs pedagógicos y retos al final.

## Flujo recomendado en vivo

1. Presentación: 20 a 25 minutos.
2. Notebook: 75 a 85 minutos.
3. Retos: 25 a 30 minutos.
4. Cierre ejecutivo: 10 minutos.

## Resultado esperado

Al final, los estudiantes deben tener consultas SQL candidatas para futuras tablas Gold y una comprensión clara de por qué la granularidad define la confiabilidad de los KPIs.
