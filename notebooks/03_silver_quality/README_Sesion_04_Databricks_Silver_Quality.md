# README — Sesión 4 Databricks: Limpieza, calidad y capa Silver

## Objetivo
Construir tablas Silver limpias, tipadas, estandarizadas y validadas para Lumi y Bagazo, partiendo de los hallazgos reales de la Sesión 3.

## Archivos del paquete
| Archivo | Uso |
|---|---|
| `Sesion_04_Databricks_Silver_Quality_iData.pptx` | Presentación principal. |
| `04_estudiante_silver_quality.ipynb` | Notebook guiado para estudiantes. |
| `04_instructor_silver_quality_solucionado.ipynb` | Notebook solucionado con notas y retos resueltos. |
| `Guia_Retos_Sesion_04_Databricks_Silver_Quality.md` | Guía de retos finales. |
| `Referencias_Oficiales_Databricks_Sesion_04.md` | Referencias oficiales Databricks. |
| `Checklist_Instructor_Sesion_04.md` | Preparación del instructor. |
| `Checklist_Estudiante_Sesion_04.md` | Validación del estudiante. |

## Prerrequisitos
Deben existir:

```text
workspace.lumi_bronze.*
workspace.bagazo_bronze.molienda_bagazo_y_lluvias_II
```

## Entregable técnico de la sesión
```text
workspace.lumi_silver.customers_clean
workspace.lumi_silver.orders_clean
workspace.lumi_silver.order_items_clean
workspace.lumi_silver.payments_clean
workspace.lumi_silver.reviews_clean
workspace.lumi_silver.products_clean
workspace.lumi_silver.sellers_clean
workspace.lumi_silver.geolocation_clean
workspace.bagazo_silver.operacion_ingenios_clean
workspace.control.quality_summary_sesion_04
```

## Preparación para la Sesión 5
La Sesión 5 debe partir de estas tablas Silver para construir consultas SQL de negocio y análisis operativo.