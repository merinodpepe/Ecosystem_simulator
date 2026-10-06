# Mancances ecològiques i pla d'acció

## Llegenda
- ✅ **DISPONIBLE** — La dada existeix al repositori, cal integrar-la
- ⏳ **POSSIBLE** — Es pot implementar amb deducció a partir de dades existents
- ❌ **NO DISPONIBLE** — Requereix noves dades externes o investigació addicional

---

## PART 1: DADES EXISTENTS QUE CAL INTEGRAR (ALTA PRIORITAT)

### 1.1 Dietes reals des de `dieta_proporciones.tsv` ✅
**Fitxer:** `ecosystem/data/dieta_proporciones.tsv` (125 línies, 28 espècies + clústers)
**Estat:** Rust usa `get_diet()` hardcoded a `foodweb.rs:42-71` amb valors diferents dels TSV
**Acció:** Carregar el TSV a l'inici i substituir la funció hardcoded. Les proporcions són molt més riques (P1/P2/P3, I1/I2/I3, vertebrats, carronya).

### 1.2 Xarxa tròfica completa des de `trophic_matrix.tsv` ✅
**Fitxer:** `ecosystem/data/trophic_matrix.tsv` (221 línies, depredador→presa amb pesos)
**Estat:** Rust té només 15 enllaços hardcoded a `TROPHIC_LINKS` (`foodweb.rs:73-89`)
**Acció:** Carregar la matriu completa. Això habilita depredació realista per TOTES les espècies.

### 1.3 Graf tròfic JSON (`ecosystem_graph_standard.json`) ✅
**Fitxer:** `ecosystem/data/ecosystem_graph_standard.json` (1779 línies, 86 nodes, multigraph)
**Estat:** No s'usa en absolut
**Acció:** Alternativa/pesada al trophic_matrix.tsv. Conté informació de connectivitat i centralitat.

### 1.4 Costos d'activitat des de `costos_actividad.tsv` ✅
**Fitxer:** `ecosystem/data/costos_actividad.tsv` (19 activitats amb MET)
**Estat:** `energy.rs` calcula DEE genèric, no usa aquests costos específics
**Acció:** Substituir el càlcul de `daily_dee()` per usar els MET values reals per activitat (FORAGE, LOCO, VIGILANCE, etc.)

### 1.5 Energia per recurs des de `energia_recursos.tsv` ✅
**Fitxer:** `ecosystem/data/energia_recursos.tsv` (22 subtipus amb kcal/g)
**Estat:** `agents.rs:310` usa valors hardcoded (1200 kcal/kg planta, 2500 kcal/kg invertebrat, 1500 kcal/kg carn)
**Acció:** Carregar densitats energètiques reals. Dades: fulles tendres 0.30 kcal/g, fruits carnosos 0.80, insectes 4.2-5.0, múscul 1.2, greix 9.3.

### 1.6 DEE estimat per espècie des de `dee_estimado.tsv` ✅
**Fitxer:** `ecosystem/data/dee_estimado.tsv` (39 espècies amb DEE, BMR, FACT, IEP)
**Estat:** No s'usa
**Acció:** Opcional — carregar DEE específic per espècie en lloc de calcular-lo per al·lometria genèrica.

### 1.7 Clústers de plantes i invertebrats ✅
**Fitxers:** `plant_clusters.tsv` (P1,P2,P3), `invertebrate_clusters.tsv` (I1,I2,I3)
**Estat:** Usats implícitament al grid, però les descripcions detallades (fenologia, funcions ecològiques) no es reflecteixen
**Acció:** Millorar el model de creixement estacional amb fenologia real (P1 floreix primavera, P3 creix ràpid a l'estiu, etc.)

### 1.8 GeoTIFFs de terreny ✅
**Fitxers:** `terrain_dem_25m.tif`, `terrain_slope.tif`, `terrain_aspect.tif`, `terrain_tri.tif`, `terrain_pisos.tif`, `terrain_habitat.tif`, `terrain_biomass.tif`
**Estat:** Codi existeix a `io.rs:31-143` sota feature `geo`, requereix `gdal` i `cargo run --features geo`
**Acció:** Fer funcionar el feature `geo`. El `terrain_biomass.tif` té 9 bandes (P1,P2,P3,I1,I2,I3,P1_max,P2_max,P3_max).

### 1.9 Espècies que falten a DEFAULT_POPULATIONS ✅
**Fitxer:** `simulation.rs:55-74`
**Estat:** Hi ha 18 espècies/configuracions, però en falten d'importants que tenen dieta definida:
- **Lutra lutra** (Llúdriga) — ja té dieta a foodweb.rs però NO té PopulationConfig
- **Ovis aries musimon** (Mufló) — present a vertebrates.tsv, dieta_proporciones.tsv, però NO al simulador
- **Dama dama** (Daina) — idem
- **Galemys pyrenaicus** (Almesquera) — idem
- Clústers funcionals no són agents individuals sinó pools (correcte)

---

## PART 2: MILLORES ECOLÒGIQUES IMPLEMENTABLES (PRIORITAT MITJANA)

### 2.1 Detecció de preses reals (no biomassa) ⏳
**Fitxer:** `agents.rs:422-446` — `detect_prey_cells()`
**Problema:** Busca biomassa a les cel·les, NO agents presa reals. Un carnívor detecta "menjar potencial" on hi ha biomassa vegetal, no on hi ha conills reals.
**Solució:** Passar llista d'agents vius a detect_prey_cells i buscar preses reals (coincidència amb trophic_matrix).

### 2.2 Competència intra/interespecífica ⏳
**Problema:** Múltiples agents al mateix cell mengen sense competir. No hi ha scramble competition.
**Solució:** Quan N agents foragen al mateix cell, el recurs es divideix entre ells (o es redueix la taxa d'extracció per càpita).

### 2.3 Memòria de taules de menjar ⏳
**Problema:** Els agents no recorden on van trobar bon menjar. Cada dia exploren de nou.
**Solució:** Afegir cache de cel·les visitades amb alta biomassa. Tendència a tornar a cel·les conegudes amb èxit previ.

### 2.4 Moviment estocàstic més realista ⏳
**Problema:** El moviment és aleatori dins del home range. No hi ha directional persistence.
**Solució:** Implementar correlació direccional (correlated random walk) — tendència a continuar en la mateixa direcció.

### 2.5 Cicles estacionals més detallats ⏳
**Problema:** Només 4 estacions amb modifiers senzills.
**Solució:** Usar fenologia real de plant_clusters.tsv (P1 brot primavera, flor estiu, fructificació tardor; P3 creixement ràpid estiu).

### 2.6 Termoregulació amb costos variables ⏳
**Problema:** Només "is_cold" binari que afegeix 2h de shivering.
**Solució:** Model continu de cost tèrmic basat en temperatura, vent, humitat, i aïllament del pelatge/plomatge.

### 2.7 Hibernació (marmotes, ossos) ⏳
**Problema:** Marmotes i ossos haurien d'hibernar a l'hivern (reduir metabolisme, no moure's).
**Solució:** Detectar espècie i estació. Si hivern, estat "hibernating": BMR reduït 90%, no foragging, no reproducció.

### 2.8 Depredació amb functional response (Holling) ⏳
**Problema:** La depredació treu massa fixa de preses. No hi ha resposta funcional (més preses disponibles → més depredació, però saturable).
**Solució:** Implementar Holling Type II o III: taxa de depredació = a*N/(1 + a*h*N).

---

## PART 3: MILLORES QUE REQUEREIXEN NOVES DADES (BAIXA PRIORITAT)

### 3.1 Malalties i paràsits ❌
**Problema:** No hi ha dades de prevalença de malalties al parc.
**Solució:** Caldria investigar estudis epidemiològics d'espècies del Pirineu.

### 3.2 Migració altitudinal ❌
**Problema:** Algunes espècies (isard, cérvol) es mouen altitudinalment entre estacions.
**Solució:** Calen dades de moviments estacionals documentats al PNAP.

### 3.3 Depredadors nous (llop, tigre) ❌
**Problema:** El llop (Canis lupus) no està present actualment al PNAP però està recolonitzant.
**Solució:** Caldria modelar com a escenari, no com a estat actual.

### 3.4 Genètica i endogàmia ❌
**Problema:** Poblacions petites pateixen endogàmia.
**Solució:** Caldria marcadors genètics i pedigrí.

### 3.5 Canvi climàtic ❌
**Problema:** Tendències a llarg termini de temperatura/precipitació.
**Solució:** Calen projeccions climàtiques per als Pirineus (escenaris RCP).

### 3.6 Disturbis (foc, allaus, activitat humana) ❌
**Problema:** No hi ha dades d'ocurrència d'aquests events.
**Solució:** Caldria sèries històriques d'incendis/allaus al PNAP.

---

## PART 4: PLA D'IMPLEMENTACIÓ (PER ORDRE)

| # | Tasca | Dades | Esforç | Impacte |
|---|-------|-------|--------|---------|
| 1 | Carregar `dieta_proporciones.tsv` → substituir `get_diet()` | ✅ | 2h | Alt |
| 2 | Carregar `trophic_matrix.tsv` → substituir `TROPHIC_LINKS` | ✅ | 2h | Alt |
| 3 | Afegir espècies que falten a DEFAULT_POPULATIONS | ✅ | 1h | Alt |
| 4 | Millorar `detect_prey_cells()` per buscar agents reals | ⏳ | 3h | Alt |
| 5 | Usar `energia_recursos.tsv` per densitats energètiques | ✅ | 1h | Mig |
| 6 | Usar `costos_actividad.tsv` per activity costs | ✅ | 2h | Mig |
| 7 | Usar `dee_estimado.tsv` per DEE per espècie | ✅ | 1h | Mig |
| 8 | Fer funcionar feature `geo` per carregar GeoTIFFs | ✅ | 3h | Mig |
| 9 | Implementar competència per recursos | ⏳ | 2h | Mig |
| 10 | Implementar memòria de taules de menjar | ⏳ | 2h | Mig |
| 11 | Implementar hibernació | ⏳ | 2h | Mig |
| 12 | Implementar functional response (Holling) | ⏳ | 2h | Mig |
| 13 | Implementar cicles estacionals amb fenologia real | ✅ | 2h | Mig |
| 14 | Validar amb dades reals de camp | ❌ | Continu | Alt |

---

## Notes tècniques

- **Rust → Python**: Mantenir desacoblament total (TSV/CSV/JSON com a interfície)
- **Rayon**: Ja s'usa per paral·lelitzar `decide()` — mantenir
- **Clústers vs Agents**: Els clústers funcionals (V-Passeriformes, V-Micromamífers, etc.) són pools de biomassa, NO agents individuals. Correcte així.
- **Geo feature**: `cargo run --features geo` requereix `gdal` i `libgdal-dev` al sistema
