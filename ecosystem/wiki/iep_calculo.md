---
tags:
  - energy
  - iep
  - ingestion
  - diet
  - validation
date: 2026-06-22
---
# Cálculo de la Ingesta Energética Potencial (IEP)

**Fase:** 2.5 del plan de diagnóstico energético
**Implementación:** `validate_energy.py:210-223`
**Referencia base:** [[2026-06-22_plan_diagnostico_energia]]

---

## Fórmula fundamental

$$
\text{IEP} = \sum_{i} \left( \text{proporción\_dieta}_i \times \text{ingesta\_max} \times \text{densidad\_energética}_i \right)
$$

en kcal/día, donde el sumatorio recorre todas las categorías de recurso en la dieta de la especie.

### Desglose de variables

| Variable | Fuente | Archivo |
|----------|--------|---------|
| `proporción_dieta_i` | Fracción de la categoría i en la dieta (0–1) | `dieta_proporciones.tsv` |
| `ingesta_max` | Ingesta máxima diaria (kg) | Regla alométrica según dieta |
| `densidad_energética_i` | kcal/g del recurso i | `energia_recursos.tsv` |

---

## Ingesta máxima diaria

Se estima como porcentaje de la masa corporal, variando según el gremio trófico:

```python
if plant_pct > 0.5:
    intake_max_kg = mass_kg * 0.10   # Herbívoros: 10% masa corporal/día
elif vert_pct > 0.5:
    intake_max_kg = mass_kg * 0.08   # Carnívoros: 8% masa corporal/día
else:
    intake_max_kg = mass_kg * 0.09   # Omnívoros: 9% masa corporal/día
```

| Gremio | Ingesta máxima | Fundamento |
|--------|---------------|------------|
| Herbívoros (>50% plantas) | 10% masa corporal/día | Alto volumen de materia vegetal de baja densidad energética |
| Carnívoros (>50% vertebrados) | 8% masa corporal/día | Dieta rica en proteínas/grasas, menor volumen necesario |
| Omnívoros (mixto) | 9% masa corporal/día | Valor intermedio |

---

## Densidades energéticas de recursos

Tomadas de `energia_recursos.tsv` y agregadas por categoría funcional:

| Categoría | kcal/g (peso húmedo) | Subtipos incluidos |
|-----------|---------------------|-------------------|
| **P1** (frutos carnosos) | 0.80 | Bayas (*Vaccinium*, *Rubus*), frutos de sotobosque |
| **P2** (acuáticas/helechos) | 0.30 | *Hippuris vulgaris*, pteridófitos, briófitos |
| **P3** (pastos) | 0.30 | *Nardus stricta*, *Festuca* spp., gramíneas alpinas |
| **Plantas** (mixto) | 0.35 | Agregado para recursos vegetales no diferenciados |
| **Invertebrados** | 4.50 | Media ponderada: larvas Lepidoptera 5.0, coleópteros 4.8, arácnidos 4.5, formícidos 4.2, oligoquetos 3.8 |
| **Vertebrados** | 1.20 | Músculo magro (carne de ungulados, aves, etc.) |

Fuentes completas en `energia_recursos.tsv`:
- USDA FoodData Central (valores de plantas y carnes)
- Sloan et al. 2019 (contenido energético de larvas de Lepidoptera)
- Greenstone & Bennett 1980 (arácnidos)
- Lighton & Wehner 1993 (formícidos)
- Bouché 1977 (oligoquetos)

---

## Proporciones de dieta

Extraídas de `dieta_proporciones.tsv`, generadas a partir de:
- Campo `main_diet` en `vertebrates.tsv`
- Matriz trófica en `trophic_matrix.tsv`
- Estimaciones cualitativas (high/medium/low → proporciones numéricas)

Ejemplos:

| Especie | Plantas | Invertebrados | Vertebrados |
|---------|---------|---------------|-------------|
| *Rupicapra pyrenaica* (Isard) | 0.92 (P3) | 0.05 | 0.03 |
| *Sus scrofa* (Senglar) | 0.60 (P3) | 0.20 | 0.20 |
| *Ursus arctos* (Ós bru) | 0.40 | 0.30 | 0.30 |
| *Aquila chrysaetos* (Àguila reial) | 0.05 | 0.10 | 0.85 |
| *Salmo trutta* (Truita) | 0.10 (P2) | 0.80 | 0.10 |
| *Calotriton asper* (Tritó pirinenc) | 0.00 | 0.95 | 0.05 |
| *Iberolacerta aurelioi* (Sargantana) | 0.02 | 0.95 | 0.03 |

---

## Implementación

```python
def validate_species(species, diet_props):
    results = []
    for sp in species:
        mass_kg = sp["mass_mid_kg"]
        # ... BMR, DEE calculation ...

        # Diet proportions
        diet = diet_props.get((taxon, name), {})
        plant_pct = diet.get("P1", 0) + diet.get("P2", 0) \
                  + diet.get("P3", 0) + diet.get("Plantas", 0)
        invert_pct = diet.get("Invertebrados", 0)
        vert_pct = diet.get("Vertebrados", 0)

        # Max intake
        intake_max_kg = mass_kg * 0.10 if plant_pct > 0.5 else \
                        mass_kg * 0.08 if vert_pct > 0.5 else \
                        mass_kg * 0.09

        # IEP = sum of (proportion × max_intake_kg × 1000 g/kg × kcal/g)
        iep = 0.0
        for cat, pct in diet.items():
            ed = ENERGY_DENSITY.get(cat, 0.35)  # default 0.35 kcal/g
            iep += pct * intake_max_kg * 1000 * ed

        balance = iep - dee_taxon
        results.append({...})
```

---

## Resultados del balance IEP vs DEE

De la validación con 38 especies/clusters (ver `validacion_energia.tsv`):

| Grupo | Especies | Balance positivo | Balance negativo |
|-------|----------|-----------------|-----------------|
| Mamíferos | 18 | 8 (*Sus*, *Ursus*, *Lutra*, *Vulpes*, *Felis*, *Martes*, *Meles*) | 10 (*Rupicapra*, *Cervus*, *Capreolus*, *Marmota*, etc.) |
| Aves | 5 | 0 | 5 (*Tetrao*, *Lagopus*, *Gypaetus*, *Aquila*, *Corvus*) |
| Reptiles | 3 | 3 | 0 |
| Anfibios | 4 | 4 | 0 |
| Peces | 2 | 2 | 0 |
| Clusters vertebrados | 6 | 2 | 4 |

**Observaciones:**
- Mamíferos grandes herbívoros muestran déficit (DEE > IEP), asumible con reservas corporales
- Carnívoros y omnívoros grandes con balance positivo (dieta rica en proteínas/grasas)
- Aves muestran déficit consistente (~25–34%), posiblemente por FAct sobreestimado o ingesta subestimada
- Ectotermos (reptiles, anfibios) con balance positivo pero baja demanda energética absoluta

---

## Parámetros por taxón (BMR y DEE para comparación)

| Taxón | a_BMR | b_BMR | FAct | Fuente BMR |
|-------|-------|-------|------|------------|
| Mammalia | 70.0 | 0.75 | 2.5 | Kleiber 1932 |
| Aves | 129.0 | 0.67 | 2.8 | Aschoff & Pohl 1970 |
| Reptilia | 0.16 | 0.88 | 3.0 | Huey & Kingsolver 1989 |
| Amphibia | 0.20 | 0.80 | 2.5 | Lillywhite et al. 1973 |
| Actinopterygii | 0.13 | 0.80 | 2.0 | Jobling 1994 |

**DEE = BMR × FAct** (kcal/día)

---

## Enlaces

- [[dee_calculo]] — Cálculo del DEE (Gasto Energético Diario)
- [[dieta_proporciones]] — Documentación de proporciones de dieta
- [[energia_recursos]] — Densidades energéticas detalladas
- [[validacion_energia]] — Informe completo de validación (Fase 2.6)
- [[../data/dieta_proporciones.tsv]] — Matriz de proporciones de dieta
- [[../data/energia_recursos.tsv]] — Tabla de densidades energéticas
- [[../data/dee_estimado.tsv]] — DEE calculados por especie
- [[../data/validacion/validacion_energia.tsv]] — Validación completa
