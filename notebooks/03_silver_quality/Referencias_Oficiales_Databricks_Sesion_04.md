# Referencias oficiales Databricks — Sesión 4

Este documento reúne referencias oficiales de Databricks usadas para sustentar los conceptos técnicos de la Sesión 4. Se diferencia lo que se ejecuta en **Databricks Free Edition** de lo que se explicaría en **Azure Databricks empresarial**.

## 1. Databricks Free Edition y limitaciones
- Referencia oficial: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Uso pedagógico: explicar que los estudiantes trabajan con cómputo serverless limitado y que no deben depender de configuración personalizada de clusters ni GPU.

## 2. Arquitectura Medallion
- Referencia oficial: https://docs.databricks.com/aws/en/lakehouse/medallion
- Uso pedagógico: justificar Bronze → Silver → Gold y explicar que Silver es la capa de limpieza y validación.

## 3. Delta Lake
- Referencia oficial: https://docs.databricks.com/aws/en/delta/
- Uso pedagógico: explicar que las tablas Databricks usan Delta por defecto y que esto aporta confiabilidad al lakehouse.

## 4. Tablas manejadas y CREATE TABLE
- Referencias oficiales:
  - https://docs.databricks.com/aws/en/tables/managed
  - https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using
- Uso pedagógico: explicar que las tablas Silver se guardan como tablas manejadas para simplificar la práctica.

## 5. Unity Catalog y Volumes
- Referencia oficial: https://docs.databricks.com/aws/en/volumes/
- Uso pedagógico: explicar que los datos crudos están en Volumes y las tablas se organizan por catálogo/esquemas.

## 6. Git folders / repos
- Referencia oficial: https://docs.databricks.com/aws/en/repos/
- Uso pedagógico: conectar esta sesión con buenas prácticas de versionamiento de la Sesión 1.

## 7. PySpark DataFrames
- Referencias oficiales:
  - https://docs.databricks.com/aws/en/pyspark/
  - https://docs.databricks.com/aws/en/getting-started/dataframes
- Uso pedagógico: reforzar transformaciones con `select`, `withColumn`, `join`, `groupBy`, `agg` y `filter`.

## 8. Data quality / expectations
- Referencia oficial: https://docs.databricks.com/aws/en/ldp/expectations
- Uso pedagógico: mostrar que las reglas manuales de esta sesión son una versión educativa de controles de calidad más robustos.

## 9. Databricks SQL y Dashboards
- Referencias oficiales:
  - https://docs.databricks.com/aws/en/dashboards
  - https://docs.databricks.com/aws/en/dashboards/tutorials/create-dashboard
- Uso pedagógico: preparar la Sesión 5, donde Silver se consultará con SQL para análisis de negocio.

## 10. MLflow, Model Registry y MLOps
- Referencias oficiales:
  - https://docs.databricks.com/aws/en/mlflow/
  - https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle/
- Uso pedagógico: conectar Bagazo Silver con sesiones posteriores de entrenamiento, registro e inferencia batch.

## Nota de cautela
No se deben prometer capacidades empresariales como si fueran parte de Free Edition. En esta sesión se ejecuta una práctica educativa y se explica cómo escalaría en Azure Databricks empresarial sin hacerlo obligatorio.