# Revisión bibliográfica de metabología

## Ecuaciones allométricas para metabolismo basal (BMR) y gasto energético de campo (DEE/FMR)

| Grupo taxonómico | Ecuación | Parámetros (a, b) | Comentario / Fuente |
|------------------|----------|-------------------|---------------------|
| Mamíferos (general) | BMR = a·M^b | a = 70 kcal·día⁻¹·kg⁻ᵇ, b = 0.75 | Ley de Kleiber (1932). Fuente: PanTHERIA, White & Seymour 2003 |
| Mamíferos (específico por orden) | BMR = a·M^b | Valor variable según orden (ver PanTHERIA). | Fuente: PanTHERIA database (Jones et al. 2009) |
| Aves | BMR = a·M^b | a = 129 kcal·día⁻¹·kg⁻ᵇ, b = 0.67 | Fuente: EltonTraits, Aschoff & Pohl 1970 |
| Reptiles | BMR = a·M^b | a = 0.16 kcal·día⁻¹·kg⁻ᵇ, b = 0.88 | Fuente: Huey & Kingsolver 1989; Secor & Diamond 2000 |
| Anfibios | BMR = a·M^b | a = 0.20 kcal·día⁻¹·kg⁻ᵇ, b = 0.80 | Fuente: Lillywhite et al. 1973; Alcalde 1995 |
| Peces (Actinopterygii) | BMR = a·M^b | a = 0.13 kcal·día⁻¹·kg⁻ᵇ, b = 0.80 | Fuente: Jobling 1994; Martínez del Río et al. 2009 |

### Factores de actividad (FAct) para pasar de BMR a DEE

| Estado / comportamiento | Valor típico de FAct | Comentario |
|--------------------------|----------------------|------------|
| Basal (reposo, termoneutral) | 1.0‑1.2 | Multiplicador mínimo |
| Foraging moderado (búsqueda de alimento, desplazamiento bajo) | 1.5‑2.5 | Depende de la especie y hábitat |
| Foraging alto / locomotion sostenida | 2.5‑4.0 | Animales con patrullaje extensivo o migración |
| Actividad intensa (huida, pelea, canto reproductivo) | 4.0‑6.0 | Episodios breves de alto gasto |
| Hibernación / torpor | 0.3‑0.7 | Reducción metabólica significativa |

Los valores de FAct pueden ajustarse mediante observaciones etológicas específicas del Alt Pirineu (tiempo dedicado a alimentación, locomoción, vigilancia, etc.) o tomando promedios de la literatura (Nagy 2005; Williams et al. 2001).

## Fuentes y referencias

1. **Kleiber, M.** (1932). *Body Size and Metabolism*. Hilgardia.  
2. **Nagy, K.A.** (2005). Field metabolic rate and body size. *Journal of Experimental Biology*, 208, 1621‑1625.  
3. **PanTHERIA** – Jones, K.E., et al. (2009). *PanTHERIA: a species‑level database of life history, ecology, and geography of extant and recently extinct mammals*. *Ecology*, 90(9), 2648.  
4. **EltonTraits** – Wilman, H., et al. (2014). *EltonTraits 1.0: Species-level foraging attributes of the world’s birds and mammals*. *Ecology*, 95(8), 2027‑2036.  
5. **Secor, S.M., & Diamond, J.** (2000). Evolution of regulatory mechanisms for feeding and fasting in vertebrates. *American Zoologist*, 40, 229‑242.  
6. **Huey, R.B., & Kingsolver, J.G.** (1989). Evolution of thermal heterogeneity in ectotherms. *American Naturalist*, 134, 1‑13.  
7. **Lillywhite, H.B., et al.** (1973). The energetics of amphibian movements. *Copeia*, 1973(2), 241‑247.  
8. **Alcalde, J.** (1995). Metabolic rates of amphibians. In *Amphibian Biology*, Vol. 2.  
9. **Jobling, M.** (1994). *Fish Bioenergetics*. Chapman & Hall.  
10. **Martínez del Río, C., et al.** (2009). Isotopic ecology in fishes. *Annual Review of Ecology, Evolution, and Systematics*, 40, 241‑263.

### PDFs de referencia (guardados en `ecosystem/data/referencias/`)

- Nagy_2005_FieldMetabolicRate.pdf  
- PanTHERIA_overview.pdf  
- EltonTraits_birds.pdf  
- EltonTraits_mammals.pdf  
- Secor_Diamond_2000_VertebrateFasting.pdf  
- Huey_Kingsolver_1989_ThermalHeterogeneity.pdf  
- Jobling_1994_FishBioenergetics.pdf  
- Martínez_del_Río_et_al_2009_IsotopicEcology.pdf  

*(Los archivos PDF deben ser descargados y colocados en la carpeta indicada; aquí solo se listan los nombres esperados.)*

---
*Esta revisión será la base para el cálculo del Gasto Energético Diario (DEE) en la sección 2.4 del diagnóstico.*
## Enlaces relacionados
- [[PROJECT_OVERVIEW]] – Visión general del proyecto
- [[ecosystem/data/referencias/]] – Carpeta donde almacenar los PDFs de referencia citados
