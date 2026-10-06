# Explicación de vertebrates.tsv

## Nombre del Dato
vertebrates.tsv

## Qué es
Archivo TSV que contiene datos estructurados de especies de vertebrados del Parc Natural de l'Alt Pirineu, incluyendo información taxonómica, trófica, reproductiva y morfológica.

## Fuente u origen
Extraído de la base de especies del proyecto (ver `biodata/` y el documento maestro "Base d'espècies i interaccions tròfiques per a una simulació agent-based al Parc Natural de l'Alt Pirineu").

## Formato y estructura
- **Tipo de archivo**: TSV (valores separados por tabulaciones)
- **Columnas**:
  - `taxon_group`: clase taxonómica (Mammalia, Aves, Reptilia, Amphibia, Actinopterygii)
  - `scientific_name`: nombre científico latino
  - `common_name_ca`: nombre común en catalán
  - `trophic_level`: nivel trófico general (Herbívoro, Carnívoro, Omnívoro, etc.)
  - `main_diet`: fuentes principales de alimento descritas en catalán
  - `main_predators`: principales depredadores de la especie
  - `reproduction_summary`: información clave de biología reproductiva
  - `body_mass_kg_approx`: rango aproximado de masa corporal en kilogramos
- **Número de filas/registros**: 38 entradas (28 especies individuals + 6 clústers funcionals de vertebrats + 4 clústers de plantes/invertebrats)

## Uso previsto
Este dataset se utiliza para parametrizar agentes vertebrados en la simulación agent-based del ecosistema, proporcionando:
- Información trófica para construir redes de alimentación
- Parámetros de masa corporal para modelos de metabolismo y energía
- Detalles de reproducción para ciclos poblacionales
- Relaciones depredador-presa para dinámicas tróficas

## Limitaciones o notas importantes
- Las masas corporales son estimaciones aproximadas de la literatura
- El nivel trófico es una clasificación general; las dietas pueden ser más específicas y estacionales
- La lista incluye especies representativas pero no todas las 277 especies vertebradas documentadas en el parque (ver nota en el README sobre modelado mediante grupos funcionales)

## Enlaces relacionados
- [[../data/vertebrates.tsv]] (enlace al dato en la carpeta data)
- [[Plantilla_explicación]] (plantilla utilizada)
- [[PROJECT_OVERVIEW]] (visión general del proyecto)
- [[ecosystem/wiki/Plantilla_explicación|Plantilla de Explicación]] (enlace alternativo)

---
*Explicación generada siguiendo la guía del vault para mantener consistencia en la documentación del proyecto.*
## Enlaces relacionados
- [[../data/vertebrates.tsv]] – Datos de vertebrados fuente
