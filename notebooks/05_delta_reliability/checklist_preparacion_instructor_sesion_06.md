# Checklist de preparación previa — Instructor Sesión 6

## Antes de clase

- Verificar que existe el catálogo `workspace`.
- Verificar que existen los schemas `lumi_silver`, `bagazo_silver`, `control`.
- Verificar que existe `workspace.control.quality_summary_sesion_04`.
- Confirmar que `reviews_clean` sigue en estado `REVISAR` para explicar calidad vs confiabilidad.
- Importar el notebook estudiante en Databricks.
- Tener abierto el notebook instructor como guía.
- Validar que los estudiantes entienden la regla: Silver se consulta, `delta_lab` se modifica.

## Durante clase

- Ejecutar primero `DESCRIBE HISTORY` sobre Silver sin modificarla.
- Crear `workspace.delta_lab`.
- Recrear tablas lab.
- Ejecutar un solo cambio controlado en Lumi.
- Ejecutar un solo cambio controlado en Bagazo.
- Mostrar que `RESTORE` genera una nueva entrada en historia.
- Cerrar con checklist pre-Gold.

## No hacer

- No ejecutar `VACUUM` agresivo.
- No modificar Silver real.
- No crear Gold todavía.
- No prometer capacidades empresariales que Free Edition no soporte.
