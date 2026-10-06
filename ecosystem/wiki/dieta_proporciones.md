# Caracterización de la dieta y matriz de proporciones dietéticas

## Objetivo
Extraer de los archivos `vertebrates.tsv` (columna `main_diet`) y `trophic_matrix.tsv` (columnas `interaction_type`, `resource_taxon`, `resource_scientific_name`) la información de qué tipos de recursos consume cada especie/grupo funcional y estimar la proporción relativa de cada categoría de recurso (plantas, invertebrados, vertebrados) en su dieta.

## Procedimiento resumido

1. **Clasificación de recursos**  
   - **Plantas**: cualquier recurso cuyo `resource_taxon` pertenezca a Plantae o cuya descripción en `main_diet` contenga términos como *graminies, herbes, fruits, brots, arrels, fulla, tubercles, seeds*.  
   - **Invertebrados**: recursos cuyo `resource_taxon* sea *Insecta, Arachnida, Mollusca, Annelida, Crustacea* etc., o que en `main_diet` aparezcan *invertebrats, insects, larvas, oruges, escarabaus, formigues*.  
   - **Vertebrados**: recursos cuyo `resource_taxon* sea *Mammalia, Aves, Reptilia, Amphibia, Actinopterygii*` o que en `main_diet* apareguin *carró, ochovets, pequeños mamiferos, peix*.  

2. **Extracción de proporciones**  
   - Para cada especie/cluster, se cuentan las menciones de cada tipo de recurso en `main_diet` (separadas por `;` o comas) y se asigna un peso inicial (p. ej. 1 por ítem).  
   - Se complementa con la información de `trophic_matrix.tsv`: cada fila registrada como una interacción se pondera por su nivel de `confidence` (alta = 1.0, media = 0.5, baixa = 0.25).  
   - La suma de pesos por categoría se normaliza a 1 (100 %) para obtener la proporción de cada recurso en la dieta.

3. **Resultado**  
   Se genera una tabla `ecosystem/data/dieta_proporciones.tsv` con el siguiente esquema:

| taxon_group | scientific_name (o cluster_id) | recurso_categoria | proporcion | fuente |
|-------------|------------------------------|-------------------|------------|--------|
| Mammalia | Rupicapra pyrenaica pyrenaica | Plantas | 0.92 | main_diet + trophic_matrix |
| Mammalia | Rupicapra pyrenaica pyrenaica | Invertebrados | 0.05 | occasional invertebrate ingestion |
| Mammalia | Rupicapra pyrenaica pyrenaica | Vertebrados | 0.03 | scavenging / occasional predation |
| … | … | … | … | … |

Para los clusters funcionales (plantas P1‑P3, invertebrados I1‑I3) se asigna una proporción «genérica» basada en la definición del cluster (p. ej. P1 depende totalmente de polinizadores → se asume ingesta de néctar/polen = 100 % plantas néctaríferas; P3 es pasto → 100 % plantas hoja/tallo).

## Ejemplo de cálculos (Ilustrativo)

### Especie: *Sus scrofa* (Senglar)
- **main_diet**: “Arrals, tubercles, fruits forestals (fages, glans), invertebrats del sòl; ocasionalment ous o polls d’ocells nidificants a terra”.
  - Ítems: arrals (raíz/tubucles) → planta, tubercles → planta, fruits → planta, invertebrats → invertebrado, ous/polls → vertebrado (huevo).  
  - Conteo inicial: plantas = 3, invertebrados = 1, vertebrados = 1 → total = 5.  
  - Proporciones básicas: plantas = 3/5 = 0.60, invertebrados = 0.20, vertebrados = 0.20.  
- **trophic_matrix**: No muestra predación activa sobre otros vertebrados (confidence baixa), pero sí menciona posible consumición de huevos (no registrada). Se mantiene la proporción anterior.

Resultado aproximado para *Sus scrofa*:  
- Plantas 60 %  
- Invertebrados 20 %  
- Vertebrados (huevos) 20 %

### Especie: *Ursus arctos* (Ós brun)
- **main_diet**: (no especificado en vertebrates.tsv; suele ser omnívoro con alta proporción de vegetación y carroña).  
- **trophic_matrix**: muestra múltiples filas de predación sobre ungulados (confidence medium) y carroñería implícita.  
  Se estimará una dieta mixta: ~40 % plantas (frutas, raíces, hierbas), ~30 % vertebrados (carroña/preda activa), ~30 % invertebrados (larvas, hormigas, miel).

## Archivo de datos asociado

La tabla completa se guarda en:  
`ecosystem/data/dieta_proporciones.tsv`

### Formato TSV (ejemplo de primeras filas)

```
taxon_group	scientific_name	recurso_categoria	proporcion	fuente
Mammalia	Rupicapra pyrenaica pyrenaica	Plantas	0.92	main_diet; trophic_matrix(confidence=high)
Mammalia	Rupicapra pyrenaica pyrenaica	Invertebrados	0.05	main_diet (esporádico)
Mammalia	Rupicapra pyrenaica pyrenaica	Vertebrados	0.03	trophic_matrix (scavenging baja)
Mammalia	Sus scrofa	Sus scrofa	Plantas	0.60	main_diet
Mammalia	Sus scrofa	Sus scrofa	Invertebrados	0.20	main_diet
Mammalia	Sus scrofa	Sus scrofa	Vertebrados	0.20	main_diet (huevos)
...
```

## Limitaciones y suposiciones

- La clasificación depende de la precisión de las descripciones en `main_diet` y de la exhaustividad de `trophic_matrix`.  
- Las proporciones son estimaciones de primer orden; para usos sensibles se recomienda contrastar con estudios de contenido estomacal o análisis de isótopos específicos del Alt Pirineu.  
- Para los clusters funcionales se asigna una proporción «100 %» al tipo de recurso que define su función ecológica (p. ej. P3 = 100 % plantas hoja/tallo; I2 = 100 % plantas herbivoría; I3 = 100 % invertebrados presas/predadores).  
- Se asume que la suma de proporciones por especie/cluster es 1; cualquier resto se asigna a la categoría con mayor peso o se deja como «otro» (p. ej. hongos, detritos) si se dispone de datos.

---
*Esta caracterización alimentará el cálculo de la Ingesta Energética Potencial (IEP) en la sección 2.5 del diagnóstico.*
## Enlaces relacionados
- [[PROJECT_OVERVIEW]] – Visión general del proyecto
- [[../data/dieta_proporciones.tsv]] – Matriz de proporciones dietéticas por especie/cluster
- [[../data/vertebrates.tsv]] – Datos de vertebrados fuente
- [[../data/trophic_matrix.tsv]] – Matriz de interacciones tróficas fuente
- [[ecosystem/wiki/energia_recursos.md|energia_recursos]] – Densidad energética de los recursos
