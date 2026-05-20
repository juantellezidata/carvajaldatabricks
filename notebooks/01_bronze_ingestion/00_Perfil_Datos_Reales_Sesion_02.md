# Perfil de datos reales — Sesión 2 Databricks

Este documento resume los archivos reales cargados para ajustar los notebooks y la presentación de la Sesión 2.

## 1. Inventario Lumi Commerce

| Tabla lógica | Archivo | Filas | Columnas | Columnas clave iniciales | Nulos relevantes |
|---|---:|---:|---:|---|---|
| `customers` | `olist_customers_dataset.csv` | 99,441 | 5 | customer_id, customer_unique_id | Sin nulos detectados |
| `orders` | `olist_orders_dataset.csv` | 99,441 | 8 | order_id, customer_id | order_approved_at: 160; order_delivered_carrier_date: 1783; order_delivered_customer_date: 2965 |
| `order_items` | `olist_order_items_dataset.csv` | 112,650 | 7 | order_id, order_item_id, product_id, seller_id | Sin nulos detectados |
| `order_payments` | `olist_order_payments_dataset.csv` | 103,886 | 5 | order_id, payment_sequential | Sin nulos detectados |
| `order_reviews` | `olist_order_reviews_dataset.csv` | 99,224 | 7 | review_id, order_id | review_comment_title: 87656; review_comment_message: 58247 |
| `products` | `olist_products_dataset.csv` | 32,951 | 9 | product_id, product_category_name | product_category_name: 610; product_name_lenght: 610; product_description_lenght: 610; product_photos_qty: 610; product_weight_g: 2; product_length_cm: 2; product_height_cm: 2; product_width_cm: 2 |
| `sellers` | `olist_sellers_dataset.csv` | 3,095 | 4 | seller_id | Sin nulos detectados |
| `geolocation` | `olist_geolocation_dataset.csv` | 1,000,163 | 5 | geolocation_zip_code_prefix | Sin nulos detectados |
| `product_category_translation` | `product_category_name_translation.csv` | 71 | 2 | product_category_name | Sin nulos detectados |

## 2. Inventario Caso Bagazo

- Archivo original: `molienda_bagazo_y_lluvias_II (1).xlsx`
- Hoja: `Base de datos`
- Archivo CSV generado para Databricks: `molienda_bagazo_y_lluvias_II.csv`
- Filas: **798**
- Columnas: **13**
- Rango de fechas: **2024-01-01 a 2026-03-08**

### Columnas
- `Fecha`
- `PROMEDIO LLUVIAS  PROVIDENCIA (mm)`
- `CAÑA MOLIDA PROVIDENCIA (Toneladas)`
- `BAGAZO ENTREGADO PROVIDENCIA (Toneladas)`
- `Comentarios
PROVIDENCIA`
- `PROMEDIO LLUVIAS ILC (mm)`
- `CAÑA MOLIDA ILC (Toneladas)`
- `BAGAZO ENTREGADO ILC (Toneladas)`
- `Comentarios
ILC`
- `PROMEDIO LLUVIAS INCAUCA  (mm)`
- `CAÑA MOLIDA INCAUCA (Toneladas)`
- `BAGAZO ENTREGADO INCAUCA (Toneladas)`
- `Comentarios
INCAUCA`

### Nulos relevantes
- `Comentarios
PROVIDENCIA`: 717
- `Comentarios
ILC`: 700
- `Comentarios
INCAUCA`: 707

### Indicadores iniciales por ingenio
| Ingenio | Lluvia prom. mm | Lluvia máx. mm | Caña prom. | Ceros caña | Bagazo prom. | Ceros bagazo | Comentarios no nulos |
|---|---:|---:|---:|---:|---:|---:|---:|
| PROVIDENCIA | 3.79 | 35.64 | 9,049.27 | 62 | 398.12 | 103 | 81 |
| ILC | 4.89 | 57.97 | 3,268.41 | 158 | 339.58 | 177 | 98 |
| INCAUCA | 4.89 | 57.97 | 9,236.65 | 139 | 572.85 | 155 | 91 |

## 3. Ajustes incorporados a los entregables
- Los notebooks ahora contienen los nombres reales de archivos, columnas esperadas y conteos esperados.
- Se agregó conversión del Excel de Bagazo a CSV para facilitar carga con Spark.
- Se agregaron validaciones contra conteos reales por tabla.
- La presentación se actualizó con inventario y riesgos reales de los datasets.
- La guía de retos usa criterios de evaluación basados en los archivos reales.