# Explicación de plant_clusters.tsv

## Nombre del Dato
plant_clusters.tsv

## Qué es
Archivo TSV que define grupos funcionales de plantas (clusters) para la modelización en la simulación del ecosistema del Alt Pirineu, basado en estrategias ecológicas similares.

## Fuente u origen
Derivado de la documentación biológica del parque, resumiendo la diversidad de más de 1500 especies de plantas en tres grupos funcionales representativos.

## Formato y estructura
- **Tipo de archivo**: TSV
- **Columnas**:
  - `cluster_id`: identificador del cluster (P1, P2, P3)
  - `cluster_description`: nombre descriptivo del grupo
  - `representative_species`: especies clave ejemplo
  - `ecological_function`: rol en el ecosistema
  - `reproduction_type`: modo de reproducción de las plantas
  - `phenology`: patrones de crecimiento estacional
  - `notes`: información ecológica adicional
- **Número de filas/registros**: 3 clusters

## Detalle de los clusters
- **P1**: Plantas entomófilas del suelo forestal y prados con flores (dependientes de polinizadores externos)
- **P2**: Productores independientes (plantas acuáticas, helechos, briofitas)
- **P3**: Pastizales y praderas de rápido crecimiento (recurso base para herbívoros)

## Uso previsto
Estos clusters se usan para:
- Parametrizar la disponibilidad y dinámica de recursos vegetales en la simulación
- Asignar tasas de crecimiento, calidad nutricional y vulnerabilidad al pastoreo
- Modelar interacciones planta-polínizador y planta-herbívoro a nivel funcional
- Reducir la complejidad computacional manteniendo representatividad ecológica

## Limitaciones o notas importantes
- La representación por clusters simplifica la diversidad específica de especies
- Los parámetros deben calibrarse con datos de productividad y fenología local
- No captura variaciones altitudinales específicas dentro de cada cluster

## Enlaces relacionados
- [[../data/plant_clusters.tsv]]
- [[Plantilla_explicación]]
- [[PROJECT_OVERVIEW]]
- [[ecosystem/wiki/vertebrates_explicación|vertebrates_explicación]]
- [[ecosystem/wiki/invertebrate_clusters_explicación|invertebrate_clusters_explicación]]
- [[ecosystem/wiki/trophic_matrix_explicación|trophic_matrix_explicación]]

---
*Explicación generada siguiendo la guía del vault para mantener consistencia en la documentación del proyecto.*
## Enlaces relacionados
- [[../data/plant_clusters.tsv]] – Datos de clusters de plantas
