# Explicación de trophic_matrix.tsv

## Nombre del Dato
trophic_matrix.tsv

## Qué es
Archivo TSV que contiene una matriz de interacciones tróficas máquina-legible para el ecosistema del Parc Natural de l'Alt Pirineu, representando relaciones de consumo entre especies.

## Fuente u origen
Extraída de la misma base de especies e interacciones del proyecto, enfocándose en las relaciones tróficas documentadas con niveles de confianza.

## Formato y estructura
- **Tipo de archivo**: TSV
- **Columnas**:
  - `consumer_taxon`: grupo taxonómico del consumidor
  - `consumer_scientific_name`: nombre científico del consumidor
  - `resource_taxon`: grupo taxonómico del recurso (presa o planta)
  - `resource_scientific_name`: nombre científico del recurso
  - `interaction_type`: tipo de interacción (predación, herbivoría, carroñería, parasitismo, mutualismo, etc.)
  - `confidence`: nivel de confianza (alto, medio, bajo) basado en especificidad de la fuente
  - `notes`: contexto adicional sobre la interacción
- **Número de filas/registros**: más de 60 interacciones tróficas documentadas

## Contenido destacado
La matriz cubre:
- Predación de mamíferos sobre vertebrados e invertebrados
- Herbivoría y frugivoría de mamíferos sobre plantas
- Comportamiento de carroñería en mamíferos
- Predación y herbivoría de aves
- Insectivoría de reptiles y anfibios
- Predación de peces sobre invertebrados y vertebrados
- Herbivoría de invertebrados sobre plantas
- Mutualismo invertebrado (polinización, interacciones áfido-hormiga)
- Parasitismo de invertebrados (avispa parasitoide)
- Predación de invertebrados (arañas, hormigas)

## Uso previsto
Este dataset se utiliza para:
- Construir la red trófica inicial de la simulación
- Asignar probabilidades de interacción entre agentes basado en confianza
- Validar emergentes redes tróficas simuladas contra la estructura documentada
- Parametrizar tasas de consumo y eficiencias de transferencia de energía
- Implementar dietas oportunísticas y selección de presas basado en rentabilidad

## Limitaciones o notas importantes
- Las interacciones documentadas pueden no ser exhaustivas; se basa en fuentes disponibles
- Los niveles de confianza ayudan a ponderar la importancia de cada enlace en la simulación
- La matriz no incluye explícitamente variaciones estacionales en la dieta (aunque algunas están anotadas en `main_diet` de vertebrates.tsv)
- Para uso en simulación, se podría necesario convertir nombres taxonómicos a identificadores de especie interno

## Enlaces relacionados
- [[../data/trophic_matrix.tsv]]
- [[Plantilla_explicación]]
- [[PROJECT_OVERVIEW]]
- [[ecosystem/wiki/vertebrates_explicación|vertebrates_explicación]]
- [[ecosystem/wiki/plant_clusters_explicación|plant_clusters_explicación]]
- [[ecosystem/wiki/invertebrate_clusters_explicación|invertebrate_clusters_explicación]]
- [[ecosystem/wiki/species_data_overview_explicación|species_data_overview_explicación]] (opcional)

---
*Explicación generada siguiendo la guía del vault para mantener consistencia en la documentación del proyecto.*