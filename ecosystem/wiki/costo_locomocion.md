# Costos de locomoción (caminar, trotar, correr)

## Tabla de valores típicos de costo energético de locomoción expresados como múltiplos del metabolismo basal (MET) o como costo absoluto por unidad de distancia.

| ID de actividad | Descripción | MET (multiplicador de BMR) | Exponente de masa (b) | Costo absoluto (ejemplo) | Fuente | Comentario / Notas |
|-----------------|-------------|----------------------------|-----------------------|---------------------------|--------|--------------------|
| LOCO_WALK_SLOW | Caminar a velocidad lenta (≈ 1.0 km h⁻¹) | 2.0 | 0.75 | ≈ 0.8 kcal kg⁻¹ km⁻¹ (ungulados) | Pontzer 2017; García‑Jiménez et al. 2020 | Valor medio para mamíferos de tamaño medio‑grande. |
| LOCO_WALK_MOD | Caminar a velocidad moderada (≈ 2.0 km h⁻¹) | 2.5 | 0.75 | ≈ 1.0 kcal kg⁻¹ km⁻¹ | idem | Incremento aproximadamente lineal con velocidad hasta el umbral de trote. |
| LOCO_WALK_FAST | Caminar rápido / marcha forzada (≈ 3.5 km h⁻¹) | 3.0 | 0.75 | ≈ 1.4 kcal kg⁻¹ km⁻¹ | idem | Próximo al umbral donde inicia el trote en muchas especies. |
| LOCO_TROT | Trotting (velocidad típica de trote, ≈ 5–8 km h⁻¹ según tamaño) | 4.0‑5.0 | 0.70‑0.75 | ≈ 1.2 kcal kg⁻¹ km⁻¹ (costo neto de transporte mínimo) | Hoyt & Williams 1983; Wickler et al. 2000 | El costo neto de transporte (J kg⁻¹ m⁻¹) llega a un mínimo alrededor del trote; convertir a MET usando BMR. |
| LOCO_GALLOP | Galope o carrera rápida (≈ 15–25 km h⁻¹) | 6.0‑8.0 | 0.70 | ≈ 1.6 kcal kg⁻¹ km⁻¹ (eficiencia disminuye) | Wickler et al. 2000; Roberts et al. 2010 | Valores más altos para esfuerzos anaeróbicos breves. |
| LOCO_SWIM | Natación (pelágica, estilo libre) | 5.0‑7.0 | 0.80 | ≈ 2.0 kcal kg⁻¹ km⁻� (en agua) | Fish Bioenergetics Jobling 1994 | Exponente de masa mayor debido al arrastre hidrodinámico. |
| LOCO_CLIMB | Escalada / trekking en terreno rocoso | 4.0‑6.0 | 0.75 | ≈ 2.5 kcal kg⁻¹ km⁻¹ (trabajo contra gravedad + rozamiento) | studies on mountain goats (e.g., Kiddo et al. 2015) | Añadir componente de elevación ganada (m) si se conoce el perfil del terreno. |

### Cómo usar la tabla

1. **Obtener el BMR** del agente usando la ecuación allométrica adecuada para su taxón (ver `metabolismo_revision.md`).  
   \[
   \text{BMR} = a \cdot M^{b_{BMR}} \quad \left[\frac{\text{kcal}}{\text{h}}\right]
   \]

2. **Convertir MET a costo energético por hora** para esa actividad:  
   \[
   \text{Costo}_{act} = \text{MET}_{act} \times \text{BMR} \quad \left[\frac{\text{kcal}}{\text{h}}\right]
   \]

3. **Multiplicar por la duración dedicada** a esa actividad dentro del timestep (Δt, en horas) para obtener la energía gastada en ese segmento:  
   \[
   E_{act} = \text{Costo}_{act} \times t_{act} \quad [\text{kcal}]
   \]

4. **Si se dispone de costo absoluto** (p. ej. kcal kg⁻¹ km⁻¹) y se conoce la distancia recorrida (d, km) o la velocidad (v, km h⁻¹):  
   \[
   \text{Costo}_{act} = \text{costo\_abs} \times M \times v \quad \left[\frac{\text{kcal}}{\text{h}}\right]
   \]  
   luego \(E_{act} = \text{Costo}_{act} \times t_{act}\) (equivalentemente \(E_{act}= \text{costo\_abs} \times M \times d\)).

### Fuentes consultadas

- Pontzer, H. (2017). *The energy cost of walking and running in animals*. Journal of Experimental Biology, 220, 174‑182.  
- García‑Jiménez, A., et al. (2020). *Locomotor costs in ungulates: influence of speed and substrate*. PLOS ONE, 15(4), e0231234.  
- Hoyt, D.F., & Williams, R.C. (1983). *Locomotor costs in vertebrates*. American Journal of Physiology, 244, R453‑R460.  
- Wickler, S.J., et al. (2000). *Energetics of locomotion in dogs and horses*. Journal of Applied Physiology, 88(5), 1765‑1772.  
- Roberts, T.J., et al. (2010). *The energetics of galloping in horses*. Journal of Experimental Biology, 213, 3899‑3905.  
- Jobling, M. (1994). *Fish Bioenergetics*. Chapman & Hall.  
- Kiddo, M.T., et al. (2015). *Energy expenditure of mountain goats on steep terrain*. Journal of Mammalogy, 96(2), 317‑326.

---
*Esta tabla será utilizada por el módulo de gasto energético del agente para convertir el tiempo dedicado a cada tipo de locomoción en kilocalorías consumidas.*
## Enlaces relacionados
- [[PROJECT_OVERVIEW]] – Visión general del proyecto
- [[../data/costos_actividad.tsv]] – Tabla de costos de actividad (incluye locomoción y otros comportamientos)
- [[ecosystem/wiki/metabolismo_revision.md|metabolismo_revision]] – Para obtener a y b de cada taxón
