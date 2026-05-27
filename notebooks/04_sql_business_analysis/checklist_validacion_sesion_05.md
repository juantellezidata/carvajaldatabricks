# Checklist de validación — Sesión 5

## Antes de iniciar

- [ ] Existe el catálogo `workspace`.
- [ ] Existe `workspace.control.quality_summary_sesion_04`.
- [ ] Existe `workspace.lumi_silver.orders_clean`.
- [ ] Existe `workspace.lumi_silver.order_items_clean`.
- [ ] Existe `workspace.lumi_silver.payments_clean`.
- [ ] Existe `workspace.lumi_silver.reviews_clean`.
- [ ] Existe `workspace.lumi_silver.products_clean`.
- [ ] Existe `workspace.lumi_silver.sellers_clean`.
- [ ] Existe `workspace.bagazo_silver.operacion_ingenios_clean`.

## Durante la clase

- [ ] Se explica el estado `REVISAR` de `reviews_clean`.
- [ ] Se explica granularidad antes de hacer joins.
- [ ] Se usa `COUNT(DISTINCT order_id)` cuando aplica.
- [ ] Se agregan reviews por `order_id` antes de unir.
- [ ] No se suman pagos después de unir con ítems.
- [ ] No se crea Gold formal.
- [ ] Se diferencia Free Edition de Azure Databricks empresarial.

## Al finalizar

- [ ] Los estudiantes ejecutaron consultas Lumi.
- [ ] Los estudiantes ejecutaron consultas Bagazo.
- [ ] Los estudiantes redactaron al menos un insight ejecutivo.
- [ ] Quedó claro el puente a Sesión 6: Delta Lake, historia y confiabilidad.
