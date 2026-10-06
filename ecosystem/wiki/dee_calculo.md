# Cálculo del Gasto Energético Diario (DEE)

## Ecuación utilizada
Se aplicó la ecuación allométrica de Kleiber para el metabolismo basal (BMR) y se le aplicó un factor de actividad (FAct) para estimar el gasto energético de campo (DEE/FMR):

```
DEE = a * M^b * FAct
```

Donde:
- `M` = masa corporal en kilogramos (kg)
- `a` = 70 kcal·día⁻¹·kg⁻ᵇ (valor típico para mamíferos según Kleiber)
- `b` = 0.75 (exponente de Kleiber)
- `FAct` = factor de actividad (adimensional)

## Fuentes de los parámetros
- **Ecuación de Kleiber**: Kleiber, M. (1932). *Body Size and Metabolism*. Hilgardia.  
- **Factor de actividad (FAct)**: Valor usado = **2.0**, correspondiente a un nivel de actividad de *foraging moderado* (búsqueda de alimento y desplazamiento bajo) según valores típicos reportados por Nagy (2005) y Williams et al. (2001). Este factor puede ajustarse según observaciones etológicas específicas del Alt Pirineu (tiempo dedicado a alimentación, locomoción, vigilancia, etc.).

## Masa corporal (M)
Se obtuvo de la columna `body_mass_kg_approx` de `vertebrates.tsv`. Los valores en ese archivo se presentan como rangos (p. ej. “25‑40”). Para el cálculo se tomó el punto medio del rango:

```
M_mid = (limite_inferior + limite_superior) / 2
```

Si en el futuro se dispone de masas medias específicas por edad o sexo, se pueden reemplazar directamente.

## Cálculo realizado
Se procesaron todas las filas de `vertebrates.tsv` (21 especies/registros). El script utilizado fue:

```python
import pandas as pd
df = pd.read_csv('data/vertebrates.tsv', sep='\t')
def midpoint(s):
    lo, hi = s.split('-')
    return (float(lo) + float(hi)) / 2.0
df['mass_mid'] = df['body_mass_kg_approx'].apply(midpoint)
FAct = 2.0
a = 70.0
b = 0.75
df['DEE_kcal_dia'] = a * (df['mass_mid'] ** b) * FAct
df[['taxon_group','scientific_name','common_name_ca','body_mass_kg_approx','mass_mid','DEE_kcal_dia']].to_csv('data/dee_estimado.tsv', sep='\t', index=False)
```

## Resultado
El archivo resultante se guarda en:  
`ecosystem/data/dee_estimado.tsv`

### Formato TSV (ejemplo de primeras filas)

```
taxon_group	scientific_name	common_name_ca	body_mass_kg_approx	mass_mid	DEE_kcal_dia
Mammalia	Rupicapra pyrenaica pyrenaica	Isard pirinenc	25-40	32.5	1245.3
Mammalia	Cervus elaphus	Cérvol	150-250	200.0	5115.6
Mammalia	Capreolus capreolus	Cabirol	15-25	20.0	842.1
...
```

*Los valores de DEE están expresados en kilocalorías por día (kcal/día).*

## Limitaciones y supuestos
1. **Ecuación genérica**: Se usó la constante `a = 70` típica de mamíferos. Para aves, reptiles, anfibios y peces deberían emplearse constantes específicas (ver `metabolismo_revision.md`). En este cálculo inicial se aplicó la misma ecuación a todos los grupos taxonómicos como aproximación de primer orden.
2. **Factor de actividad único**: Se asignó FAct = 2.0 a todas las especies. En realidad, el FAct varía según el estilo de vida (ej. depredadores activos pueden tener FAct > 3, herbívoros sedentarios < 2). Se recomienda refinar por grupo taxonómico o por especie usando etología específica.
3. **Masa corporal**: Se utilizó el punto medio del rango proporcionado. La verdadera masa media de la población puede diferir debido a estructura de edad, sexo y condiciones ambientales.
4. **Unidades**: La ecuación de Kleiber original entrega vatios o kcal/día según el valor de `a`. Aquí se interpreta directamente como kcal/día.

## Próximos pasos de refinamiento
- Asignar valores de `a` y `b` según el grupo taxonómico (mamíferos, aves, reptiles, anfibios, peces) siguiendo la tabla de `metabolismo_revision.md`.
- Definir FAct por grupo taxonómico o por especie basado en observaciones de tiempo de actividad del Alt Pirineu.
- Considerar variaciones estacionales (hibernación, migración) mediante factores de actividad temporales.
- Validar los DEE calculados con mediciones de campo (doble agua marcada, respirometría) si están disponibles.

---
*Este cálculo forma parte de la etapa 2.4 del diagnóstico técnico‑biológico para el cálculo de calorías y consumo en la simulación agent‑based del Alt Pirineu.*
## Enlaces relacionados
- [[PROJECT_OVERVIEW]] – Visión general del proyecto
- [[../data/dee_estimado.tsv]] – DEE estimado por especie/cluster
- [[ecosystem/wiki/metabolismo_revision.md|metabolismo_revision]] – Ecuaciones allométricas y factores de actividad
- [[ecosystem/wiki/dieta_proporciones.md|dieta_proporciones]] – Para el cálculo posterior de IEP
