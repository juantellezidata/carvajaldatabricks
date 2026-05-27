# Referencias oficiales Databricks — Sesión 6

> Usar estas referencias como soporte técnico de la sesión. Todas son documentación oficial de Databricks.

## 1. Databricks Free Edition limitations

URL: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations

**Uso pedagógico:** explicar que Free Edition no tiene SLA, usa recursos serverless, no permite compute personalizado ni GPU, limita SQL Warehouse y Jobs, y no debe presentarse como un entorno empresarial productivo.

## 2. What is Delta Lake in Databricks?

URL: https://docs.databricks.com/aws/en/delta/

**Uso pedagógico:** introducir Delta Lake como la capa optimizada que fundamenta las tablas del Lakehouse, extendiendo Parquet con transaction log, transacciones ACID y metadata escalable. También soporta la afirmación de que las tablas Databricks son Delta por defecto salvo que se indique otro formato.

## 3. Work with table history

URL: https://docs.databricks.com/aws/en/delta/history

**Uso pedagógico:** explicar que cada operación que modifica una tabla crea una nueva versión y que la historia permite auditoría, rollback y consultas con Time Travel. También permite aclarar que la historia no debe tratarse como backup permanente.

## 4. DESCRIBE HISTORY

URL: https://docs.databricks.com/aws/en/sql/language-manual/delta-describe-history

**Uso pedagógico:** soportar la sintaxis SQL usada en el laboratorio y orientar la lectura de columnas como `version`, `timestamp`, `operation`, `operationParameters` y `operationMetrics`.

## 5. RESTORE

URL: https://docs.databricks.com/aws/en/sql/language-manual/delta-restore

**Uso pedagógico:** explicar la restauración controlada de una tabla Delta a una versión anterior. En clase se usa únicamente sobre tablas de laboratorio.

## 6. VACUUM

URL: https://docs.databricks.com/aws/en/sql/language-manual/delta-vacuum

**Uso pedagógico:** explicar que limpiar archivos puede afectar la capacidad de Time Travel hacia versiones antiguas. No se ejecuta `VACUUM` agresivo en la sesión.

## 7. Medallion architecture

URL: https://docs.databricks.com/aws/en/lakehouse/medallion

**Uso pedagógico:** conectar Bronze, Silver y Gold. La Sesión 6 valida confiabilidad antes de que la Sesión 7 construya Gold.

## 8. Dashboards

URL: https://docs.databricks.com/aws/en/dashboards

**Uso pedagógico:** puente hacia la Sesión 7. Un dashboard requiere tablas Gold confiables y trazables.

## Nota Free Edition vs Azure Databricks empresarial

En Free Edition se trabaja con notebooks, SQL, tablas Delta administradas y prácticas livianas. En Azure Databricks empresarial se agregaría gobierno con Unity Catalog, permisos finos, lineage, auditoría ampliada, almacenamiento empresarial, workflows productivos y CI/CD.
