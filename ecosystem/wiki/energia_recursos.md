# Contenido energético de los recursos (kcal / g)

## Valores típicos de densidad energética por tipo de recurso

| Tipo de recurso | Subtipo / ejemplo | kcal / g (peso húmedo) | Rango típico (kcal/g) | Fuente / Comentario |
|-----------------|-------------------|------------------------|-----------------------|---------------------|
| **Plantas** | Hoja tierna (ej. Trifolium repens) | 0.30 | 0.20 – 0.40 | USDA FoodData Central – “Raw spinach” (aprox.) |
|  | Hoja madura, fibrosa | 0.20 | 0.10 – 0.30 | USDA – “Raw kale” |
|  | Fruto carnoso (bayas, manzana silvestre) | 0.80 | 0.60 – 1.00 | USDA – “Raw blackberries”, “Raw apple with skin” |
|  | Fruto seco (nuez, avellana) | 5.50 | 4.5 – 6.5 | USDA – “Raw sunflower seeds”, “Raw almonds” |
|  | Semilla oleaginosa (girasol, linaza) | 5.50 | 4.5 – 6.5 | mismo que arriba |
|  | Raíz / tubérculo (ej. zanahoria silvestre) | 0.40 | 0.30 – 0.50 | USDA – “Raw carrots” |
| **Invertebrados** | Lepidoptera – larva (oruga) | 5.00 | 4.5 – 5.5 | Sloan et al. 2019, “Energy content of Lepidoptera larvae” (dry weight ≈ 20 % → ~1 kcal/g wet) *Nota: valores secos convertidos a húmedo asumiendo 80 % agua.* |
|  | Lepidoptera – adulto (mariposa) | 4.80 | 4.2 – 5.2 | idem |
|  | Coleóptero – adulto (escarabajo) | 4.80 | 4.2 – 5.2 | Sloan et al. 2019 |
|  | Araneae – araña | 4.50 | 4.0 – 5.0 | Greenstone & Bennett 1980 |
|  | Formicidae – hormiga obrera | 4.20 | 3.8 – 4.6 | Lighton & Wehner 1993 |
|  | Oligochaeta – lombriz de tierra | 3.80 | 3.5 – 4.2 | Bouché 1977 |
| **Vertebrados – tejido** | Músculo esquelético (magro) | 1.20 | 1.00 – 1.40 | USDA – “Raw venison (lean)” |
|  | Tejido muscular medio (con grasa intramuscular) | 1.60 | 1.40 – 1.80 | USDA – “Raw beef, composite cuts” |
|  | Grasa subcutánea / visceral | 9.30 | 8.5 – 10.0 | USDA – “Raw beef fat” |
|  | Órgano – hígado | 1.60 | 1.40 – 1.80 | USDA – “Raw beef liver” |
|  | Órgano – riñón | 1.40 | 1.20 – 1.60 | USDA – “Raw beef kidney” |
|  | Órgano – corazón | 1.30 | 1.10 – 1.50 | USDA – “Raw beef heart” |
|  | Sangre (plasma + células) | 0.80 | 0.60 – 1.00 | Valor aproximado basado en composición de glucosa y lípidos |
|  | Piel (con pelo) | 0.90 | 0.70 – 1.10 | Estimado a partir de colágeno y lípidos |
| **Hongos** (opcional) | Carpófobo comestible (ej. Boletus edulis) | 0.30 | 0.20 – 0.40 | USDA – “Raw mushrooms” |

### Notas importantes

1. **Peso húmedo vs. seco**: Los valores de kcal/g aquí expresados son para el peso **húmedo** tal como se encontraría en el entorno (alta proporción de agua). Si se dispone de datos de peso seco, convertir usando:  
   `kcal/g_húmedo = kcal/g_seco × (1 – fracción de agua)`.  
   La fracción de agua típica: plantas 85‑95 %, invertebrados 70‑80 %, vertebrados 60‑75 % (tejido magro).

2. **Variabilidad estacional y de madurez**: El contenido energético de frutos y semillas varía con la madurez; usar valores promedio de la temporada de máxima disponibilidad.

3. **Fuentes alternativas**: Para invertebrados específicos no cubiertos, consultar literatura de “energy content of insects” (Rosenberg et al. 1986; Siemann et al. 1998) o bases como *InsectNet*.

4. **Conversión a kJ**: 1 kcal = 4.184 kJ (útil si el motor de simulación prefiere unidades SI).

### Archivo de datos asociado

Los valores de esta tabla pueden exportarse a `ecosystem/data/energia_recursos.tsv` con columnas:  
`tipo_recurso`, `subtipo`, `kcal_por_g_humedo`, `rango_min`, `rango_max`, `fuente`.

*Ejemplo de fila:*  
`Plantas	Hoja tierna	0.30	0.20	0.40	USDA FoodData Central – Raw spinach`

---
*Esta tabla alimentará el cálculo de la Ingesta Energética Potencial (IEP) en la sección 2.5 del diagnóstico.*
## Enlaces relacionados
- [[PROJECT_OVERVIEW]] – Visión general del proyecto
- [[../data/energia_recursos.tsv]] – Tabla de densidad energética de los recursos
- [[ecosystem/wiki/dieta_proporciones.md|dieta_proporciones]] – Proporciones de recursos en la dieta
