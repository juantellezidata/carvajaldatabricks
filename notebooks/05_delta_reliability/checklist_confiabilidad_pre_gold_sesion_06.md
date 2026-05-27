# Checklist de confiabilidad pre-Gold — Sesión 6

Usa este checklist antes de crear tablas Gold en la Sesión 7.

## Formato por tabla

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

## Criterios mínimos

| Criterio | Estado | Evidencia |
|---|---|---|
| La tabla existe y tiene registros | Pendiente | `SELECT COUNT(*)` |
| La tabla tiene historia visible | Pendiente | `DESCRIBE HISTORY` |
| La tabla tiene metadata revisada | Pendiente | `DESCRIBE DETAIL` |
| No hay cambios no explicados | Pendiente | Revisión de `operation` |
| Riesgos de calidad documentados | Pendiente | `quality_summary_sesion_04` |
| Granularidad entendida | Pendiente | Consulta de llaves / negocio |
| Lista para Gold | Pendiente | Recomendación final |

## Tablas recomendadas para revisar antes de Gold

- `workspace.lumi_silver.orders_clean`
- `workspace.lumi_silver.order_items_clean`
- `workspace.lumi_silver.payments_clean`
- `workspace.lumi_silver.reviews_clean`
- `workspace.lumi_silver.products_clean`
- `workspace.bagazo_silver.operacion_ingenios_clean`

## Recordatorio crítico

No modificar tablas Silver reales. La práctica de cambios y restore pertenece únicamente a `workspace.delta_lab`.
