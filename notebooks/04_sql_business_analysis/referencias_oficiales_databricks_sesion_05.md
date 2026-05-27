# Referencias oficiales Databricks — Sesión 5

> Uso: estas referencias sustentan conceptos técnicos de la sesión. La práctica se ejecuta en Databricks Free Edition y se explica cómo escalaría a Azure Databricks empresarial.

## 1. Databricks Free Edition y limitaciones

- **Databricks Free Edition limitations**  
  https://docs.databricks.com/aws/en/getting-started/free-edition-limitations  
  **Uso pedagógico:** explicar que Free Edition usa compute serverless, tiene un SQL Warehouse limitado a 2X-Small y Jobs con máximo de 5 tareas concurrentes por cuenta. Esto justifica mantener la práctica en notebooks y consultas SQL acotadas.

- **Serverless compute limitations**  
  https://docs.databricks.com/aws/en/compute/serverless/limitations  
  **Uso pedagógico:** explicar por qué no se deben prometer configuraciones avanzadas de compute, GPU o ajustes finos de infraestructura en la clase.

## 2. Databricks SQL y SQL Warehouses

- **Data warehousing on Databricks**  
  https://docs.databricks.com/aws/en/sql  
  **Uso pedagógico:** introducir Databricks SQL como experiencia para consultar, visualizar y analizar datos del Lakehouse.

- **Get started with data warehousing using Databricks SQL**  
  https://docs.databricks.com/aws/en/sql/get-started  
  **Uso pedagógico:** diferenciar SQL exploratorio, SQL Editor, dashboards y SQL Warehouses.

- **Connect to a SQL warehouse**  
  https://docs.databricks.com/aws/en/compute/sql-warehouse  
  **Uso pedagógico:** explicar que un SQL Warehouse es compute para ejecutar consultas SQL sobre Databricks.

- **SQL warehouse sizing, scaling, and queuing behavior**  
  https://docs.databricks.com/aws/en/compute/sql-warehouse/warehouse-behavior  
  **Uso pedagógico:** explicar que en Azure Databricks empresarial se puede gestionar tamaño, escalamiento y concurrencia de SQL Warehouses.

## 3. Notebooks con SQL

- **Develop code in Databricks notebooks**  
  https://docs.databricks.com/aws/en/notebooks/notebooks-code  
  **Uso pedagógico:** justificar el uso de celdas `%sql` dentro del notebook de clase.

- **Notebook compute resources**  
  https://docs.databricks.com/aws/en/notebooks/notebook-compute  
  **Uso pedagógico:** explicar notebooks conectados a compute y, cuando aplique, a SQL Warehouses.

## 4. SQL language reference

- **Databricks SQL language reference**  
  https://docs.databricks.com/aws/en/sql/language-manual  
  **Uso pedagógico:** referencia general para sintaxis SQL.

- **SELECT syntax**  
  https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select  
  **Uso pedagógico:** soportar `SELECT`, filtros, agregaciones, joins, CTEs y ordenamiento.

## 5. Arquitectura Medallion y Delta Lake

- **What is the medallion lakehouse architecture?**  
  https://docs.databricks.com/aws/en/lakehouse/medallion  
  **Uso pedagógico:** conectar Bronze, Silver y Gold. En esta sesión trabajamos desde Silver y dejamos consultas candidatas para Gold.

- **What is Delta Lake in Databricks?**  
  https://docs.databricks.com/aws/en/delta  
  **Uso pedagógico:** preparar la Sesión 6 sobre confiabilidad, transacciones y versionado.

- **What are ACID guarantees on Databricks?**  
  https://docs.databricks.com/aws/en/lakehouse/acid  
  **Uso pedagógico:** explicar que Delta Lake aporta garantías de confiabilidad que no existen igual en archivos planos.

- **DESCRIBE HISTORY**  
  https://docs.databricks.com/aws/en/sql/language-manual/delta-describe-history  
  **Uso pedagógico:** puente directo hacia Sesión 6: historial, auditoría y trazabilidad de tablas Delta.

## 6. Dashboards como puente a Sesión 7

- **Dashboards**  
  https://docs.databricks.com/aws/en/dashboards  
  **Uso pedagógico:** mostrar que las consultas de Sesión 5 pueden convertirse luego en dashboards y KPIs Gold.

## 7. Qué se hará en Free Edition vs Azure Databricks empresarial

| Tema | Free Edition en clase | Azure Databricks empresarial |
|---|---|---|
| Compute | Serverless limitado | Serverless y/o clusters configurables según políticas |
| SQL | Notebooks `%sql` y SQL disponible | SQL Warehouses administrados, escalamiento y concurrencia |
| Gobierno | Uso de catálogo `workspace` y tablas administradas | Unity Catalog, permisos, auditoría, lineage y control por ambientes |
| Dashboards | Prototipos educativos | Dashboards gobernados y compartidos |
| Operación | Ejecución manual o limitada | Jobs, CI/CD, monitoreo y despliegue productivo |
| Seguridad | Básica para aprendizaje | Redes privadas, SSO, políticas, secretos y controles empresariales |
