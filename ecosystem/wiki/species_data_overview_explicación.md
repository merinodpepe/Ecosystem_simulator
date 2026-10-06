# Explicación General del Conjunto de Datos Especies (species_data)

## Nombre del Dato
Carpeta completa `species_data/` (contenida en `ecosystem/data/` después de la integración al vault)

## Qué es
Conjunto de archivos TSV que representan datos biológicos estructurados extraídos del Parc Natural de l'Alt Pirineu para uso en la simulación agent-based del ecosistema. Incluye información sobre vertebrados, grupos funcionales de plantas e invertebrados, y una matriz de interacciones tróficas.

## Fuente u origen
Derivado de la documentación biológica del proyecto ubicada en `/home/pepe/proyectos/ecosystem_simulator/biodata/`, específicamente del archivo maestro "Base d'espècies i interaccions tròfiques per a una simulació agent-based al Parc Natural de l'Alt Pirineu".

## Contenido del conjunto
- **vertebrates.tsv** → 38 entradas (28 especies individuals + 6 clústers funcionals de vertebrats + 4 de invertebrats/plantes al sistema complet) con datos taxonómicos, tróficos, reproductivos y morfológicos
- **plant_clusters.tsv** → 3 grupos funcionales de plantas (P1-P3) basado en strategies ecológicas
- **invertebrate_clusters.tsv** → 3 grupos funcionales de invertebrados (I1-I3) basado en roles tróficos
- **trophic_matrix.tsv** → Más de 190 interacciones tróficas documentadas con niveles de confianza
- **README.md** → Descripción extensiva de cada archivo, fuentes, notas de uso y próximos pasos (ver copia en `ecosystem/wiki/README_species_data_explicación.md` opcional)

## Uso previsto
Este conjunto de datos proporciona la base empírica para:
- Parametrizar agentes individuales y grupos funcionales en la simulación
- Construir redes tróficas iniciales y validar dinámicas emergentes
- Representar la biodiversidad del parque mediante agregaciones funcionalides cuando el detalle de especies es inviable computacionalmente
- Estudiar efectos de cascada trófica, impacto de especies clave y respuestas a cambios ambientales

## Limitaciones o notas importantes
- Los datos representan un subconjunto representativo; la simulación puede emplear procesos estocásticos o modelos de crecimiento para escalar a la diversidad total registrada (~277 vertebrados, 1500+ plantas, 900+ Lepidoptera)
- Se recomienda cruzar estos datos con capas espaciales (DEM, mapas de vegetación) y datos climáticos para una modelización más realista
- Los usuarios deben considerar el nivel de confianza al asignar fuerza de interacción en la matriz trófica

## Enlaces relacionados
- [[ecosystem/wiki/vertebrates_explicación|vertebrates_explicación]]
- [[ecosystem/wiki/plant_clusters_explicación|plant_clusters_explicación]]
- [[ecosystem/wiki/invertebrate_clusters_explicación|invertebrate_clusters_explicaciones]]
- [[ecosystem/wiki/trophic_matrix_explicación|trophic_matrix_explicación]]
- [[PROJECT_OVERVIEW]] (visión geral del proyecto)
- [[biodata/]] (carpeta fuente original de datos biológicos)
- [[ecosystem/data/]] (ubicación actual de los archivos TSV dentro del vault)

---
*Explicación generada siguiendo la guía del vault para mantener consistencia en la documentación del proyecto.*