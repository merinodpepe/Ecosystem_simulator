# Explicación de ecosystem_graph_optimized.json

## Qué es
Archivo JSON optimizado que representa el grafo de interacciones tróficas del ecosistema del Parc Natural de l'Alt Pirineu en formato eficiente para procesamiento por agentes de IA y algoritmos de grafos.

## Fuente u origen
Generado a partir de `trophic_matrix.tsv` procesando las relaciones de consumo entre especies, con optimizaciones para reducir tamaño y mejorar eficiencia de parseo.

## Formato y estructura
- **Tipo de archivo**: JSON optimizado
- **Estructura**:
  - `directed`: boolean (true)
  - `multigraph`: boolean (true)
  - `nodes`: objeto (diccionario) donde las claves son los IDs de nodos y los valores son los taxons
    - Formato: `{"node_id": "taxon", ...}`
  - `edges`: array de arrays, donde cada array representa una arista como `[source, target, type, confidence]`
    - Formato: `[["source1", "target1", "type1", "confidence1"], ...]`

## Ventajas de este formato para IA
1. **Tamaño reducido**: Significativamente más pequeño que el formato estándar
2. **Parseo más rápido**: Evita claves repetidas en cada objeto edge
3. **Acceso eficiente a nodos**: Búsqueda O(1) para obtener taxon de cualquier node ID
4. **Menor overhead**: Minimiza caracteres redundantes (llaves, comas, etc.)
5. **Compatibilidad**: Sigue siendo JSON válido y fácilmente parseable por todas las bibliotecas standard

## Contenido destacado
Mismo contenido que la versión estándar pero en formato optimizado:
- **71 nodos** (28 especies individuals, 10 clústers funcionals, 11+ recursos generals)
- **216 aristas** (interacciones tròfiques + membresía de clúster)
- **Grafo completamente conectado** en un solo componente
- Múltiples niveles tróficos y tipos de interacción
- Niveles de confianza para ponderar importancia en simulaciones

## Uso previsto
Este dataset optimizado se utiliza para:
- Procesamiento masivo por agentes de IA donde el tamaño y velocidad son críticos
- Algoritmos de grafos que requieren frecuentes accesos a nodos y edges
- Entrenamiento de modelos de aprendizaje automático sobre redes ecológicas
- Simulaciones en tiempo real donde la eficiencia de memoria es importante
- Transmisión eficiente entre sistemas distribuidos
- Análisis de redes tróficas en entornos con recursos limitados

## Limitaciones o notas importantes
- Las mismas limitaciones que la versión estándar aplican (basado en observaciones documentadas, niveles de confianza, etc.)
- Este formato asume que el consumidor conoce la estructura específica para parsear correctamente
- Menos legible para humanos que el formato estándar (pero perfectamente válido para máquinas)
- Requiere documentación clara del formato para uso por terceros

## Enlaces relacionados
- [[../data/ecosystem_graph_optimized.json]]
- [[../data/ecosystem_graph_standard.json|ver versión estándar]]
- [[../data/trophic_matrix.tsv|trophic_matrix]]
- [[ecosystem/wiki/ecosystem_graph_standard_explicación|explicación versión estándar]]
- [[ecosystem/wiki/vertebrates_explicación|vertebrates]]
- [[ecosystem/wiki/plant_clusters_explicación|plant_clusters]]
## Visualizador Interactivo

Este formato optimizado es utilizado por el visualizador interactivo para mejorar el rendimiento en aplicaciones de IA y algoritmos de grafos:

- [[ecosystem/wiki/ecosystem_graph_visualizer.html|ecosystem_graph_visualizer.html]]

El visualizador carga los datos desde la versión estándar pero el formato optimizado es ideal para el procesamiento previo por agentes de IA antes de la visualización.
