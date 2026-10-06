# Explicación de invertebrate_clusters.tsv

## Nombre del Dato
invertebrate_clusters.tsv

## Qué es
Archivo TSV que define grupos funcionales de invertebrados para la modelización en la simulación del ecosistema del Alt Pirineu, basado en roles tróficos y ecológicos similares.

## Fuente u origen
Extraído de la documentación biológica del parque, agrupando la diversidad de más de 900 especies de Lepidoptera y otros invertebrados en tres clusters funcionales representativos.

## Formato y estructura
- **Tipo de archivo**: TSV
- **Columnas**:
  - `cluster_id`: identificador del cluster (I1, I2, I3)
  - `cluster_description`: nombre descriptivo del grupo
  - `representative_species`: especies clave ejemplo
  - `ecological_function`: rol en el ecosistema
  - `trophic_role`: guild de alimentación (p. ej., herbívoro, depredador, mutualista)
  - `key_interactions`: principales interacciones ecológicas
  - `notes`: información adicional
- **Número de filas/registros**: 3 clusters

## Detalle de los clusters
- **I1**: Mutualistas polinizadores (Lepidoptera diurnos, abejorros)
- **I2**: Herbívoros/ fitófagos (consumidores de hojas, potenciales plagas)
- **I3**: Depredadores/parasitoides (agentes de control biológico)

## Uso previsto
Estos clusters se usan para:
- Modelar la dinámica de poblaciones de invertebrados en la simulación
- Parametrizar tasas de herbivoría, predación y mutualismo
- Representar servicios ecosistémicos como polinización y control biológico de plagas
- Integrar con las redes tróficas vertebradas y vegetales a través del trophic_matrix
- Simular efectos de cascada trófica a nivel de invertebrados

## Limitaciones o notas importantes
- La agrupación por clusters puede ocultar variaciones específicas de especies
- Los roles tróficos asignados son generales; algunas especies pueden tener dietas mixtas
- No incluye detalladamente etapas de vida (larvas vs adultos) que pueden tener roles diferentes

## Enlaces relacionados
- [[../data/invertebrate_clusters.tsv]]
- [[Plantilla_explicación]]
- [[PROJECT_OVERVIEW]]
- [[ecosystem/wiki/vertebrates_explicación|vertebrates_explicación]]
- [[ecosystem/wiki/plant_clusters_explicación|plant_clusters_explicación]]
- [[ecosystem/wiki/trophic_matrix_explicación|trophic_matrix_explicación]]

---
*Explicación generada siguiendo la guía del vault para mantener consistencia en la documentación del proyecto.*