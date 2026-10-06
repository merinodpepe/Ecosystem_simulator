# Explicación de ecosystem_graph_standard.json

## Qué es
Archivo JSON que representa el grafo de interacciones tróficas del ecosistema del Parc Natural de l'Alt Pirineu en formato estándar de grafo (nodos y edges como arrays de objetos).

## Fuente u origen
Generado a partir de `trophic_matrix.tsv` procesando las relaciones de consumo entre especies, incluyendo predación, herbivoría, parasitismo y otras interacciones.

## Formato y estructura
- **Tipo de archivo**: JSON
- **Estructura**:
  - `directed`: boolean (true, ya que las relaciones tróficas son direccionales)
  - `multigraph`: boolean (true, permitiendo múltiples tipos de interacción por pareja)
  - `graph`: objeto vacío para metadatos futuros
  - `nodes`: array de objetos, cada uno con:
    - `id`: string (identificador único)
    - `label`: string (nombre común en catalán para visualización)
    - `taxon`: string (clasificación: Mammalia, Aves, Insecta, Plantae, Cluster_Planta, Cluster_Invertebrat, Recurs_General)
    - `title`: string (tooltip con información detallada)
  - `edges`: array de objetos, cada uno con:
    - `source`: string (consumidor)
    - `target`: string (recurso)
    - `type`: string (tipo de interacción: predation, herbivory, entomophagy, clustermember, etc.)
    - `confidence`: string (nivel de confianza: high, medium, low)

## Contenido destacado
- **75 nodos** que incluyen:
  - **31 especies individuals** con nombre científico y nombre común en catalán
  - **11 clústers funcionals**: P1-P3 (plantes), I1-I3 (invertebrats), V-Passeriformes, V-Ratpenats, V-RapinyairesNocturnesGrans, V-RapinyairesNocturnesPetites, V-MicromamífersPetits, V-InsectívorsMitjans
  - **? nodes de recursos generals**: Micromamífers, Aus Petites, Invertebrats Presa, Crustacis, Mol·luscs, Amfibis Diversos, Peixos Petits, Carronya, Detritus, Recursos Vegetals, Fongs, Rèptils Petits
- **220 aristas** que conectan todo el grafo
- Los clústers de plantes (P1, P2, P3) ahora tienen aristas tròfiques des dels animals que se'n alimenten (herbívors → P3, frugívors → P1, aquàtics → P2)
  - Aristas especie→especie, especie→cluster, cluster→especie, cluster→cluster y especie→recursos generals
  - Aristas de membresía de clúster (I1-I3 i P1-P3)
- Cubre múltiples niveles tróficos: productors (plantes), consumidors primaris (herbívors), consumidors secundaris (carnívors), omnívors i descomponedors
- Incluye 13 tipos de interacción tròfica

## Uso previsto
Este dataset se utiliza para:
- Construir y visualizar la red tròfica completa de la simulació
- Algoritmos de análisis de grafos (centralidad, detección de comunitats, etc.)
- Validación de modelos ecològics contra dades empíriques
- Estudios de robustesa i vulnerabilitat de xarxes tròfiques
- Visualització interactiva amb noms comuns i agrupacions funcionals

## Limitaciones o notas importantes
- Les relacions están basades en observacions documentades i poden no ser exhaustives
- Les espècies que al trophic_matrix només interactuen amb "Various" (categoria general) s'han connectat al node de recurs general corresponent
- "Various" representa categories generals de presa/recurs no modelades individualment (ex: "Micromamífers" per a "Mammalia Various")
- El grafo és completament connectat (un sol component de 70+ nodes; P2 i altres clústers sense preses directes però connectats via membresia)
- Algunas interacciones estacionales o ontogénicas pueden no estar completamente representadas
- El grafo asume relaciones binarias y no captura la fuerza o frecuencia de las interacciones
- Para usar en simulaciones dinámicas, se podrían necesitar agregar pesos basados en confianza o frecuencia

## Enlaces relacionados
- [[../data/ecosystem_graph_standard.json]]
- [[../data/trophic_matrix.tsv|trophic_matrix]]
- [[ecosystem/wiki/vertebrates_explicación|vertebrates]]
- [[ecosystem/wiki/plant_clusters_explicación|plant_clusters]]
- [[ecosystem/wiki/invertebrate_clusters_explicación|invertebrate_clusters]]
## Visualizador Interactivo

Para una visualización interactiva de este grafo, utilice el visualizador HTML generado:

- [[ecosystem/wiki/ecosystem_graph_visualizer.html|ecosystem_graph_visualizer.html]]

Este visualizador permite explorar la red trófica de forma interactiva, con opciones para filtrar por tipo de interacción, activar/desactivar la física de simulación y ver estadísticas en tiempo real.
