# Simulador d'Ecosistemes del Parc Natural de l'Alt Pirineu — Estat Actual

## Visió general

Simulador agent-based en Rust amb visualització Python. Modela 18 espècies vertebrades
en un grid de 25m de resolució amb terreno real (elevació, pendent, hàbitats, neu, temperatura).
Cada agent té metabolisme basat en la llei de Kleiber, comportament estocàstic, i
interaccions tròfiques basades en dieta real.

---

## Arquitectura

```
ecosystem_simulator/
├── ecosystem_simulator_rs/     ← Motor de simulació (Rust)
│   ├── src/sim/
│   │   ├── agents.rs           ← Comportament dels agents (estocàstic)
│   │   ├── energy.rs           ← Metabolisme (BMR, MET, DEE)
│   │   ├── environment.rs      ← Estacions, temperatura
│   │   ├── foodweb.rs          ← Dietes i enllaços tròfics
│   │   ├── grid.rs             ← Terreny, plantes, invertebrats, neu
│   │   ├── io.rs               ← Càrrega TSV/GeoTIFF
│   │   ├── pathfinding.rs      ← A* amb 8 direccions
│   │   ├── pools.rs            ← Poblacions (peixos, herps, etc.)
│   │   └── simulation.rs       ← Bucle principal, configuració
│   └── Cargo.toml
├── src/
│   └── visualize_simulation.py ← Visualització (4 gràfics)
├── run_simulation.sh           ← Script per executar-ho tot
├── docs/
│   ├── ESTADO_ACTUAL.md         ← Aquest document
│   └── PENDIENTE.md            ← Mancances per a versió realista
└── figures/                    ← Gràfics generats
```

---

## Com executar

### Requisits

- Rust 1.75+ (`rustup install stable`)
- Python 3.10+ amb: `matplotlib`, `pandas`, `numpy`
- Opcional: `libgdal-dev` per a càrrega GeoTIFF

### Execució ràpida (recomanat)

```bash
cd ecosystem_simulator
./run_simulation.sh --days 365
```

Això compila (si cal), executa la simulació 100×100 durant 365 dies,
i genera 4 gràfics a `figures/`.

### Execució manual

```bash
cd ecosystem_simulator_rs
cargo run --release -- --width 100 --height 100 --days 730 --output sortida
cd ..
python3 src/visualize_simulation.py --dir ecosystem_simulator_rs/sortida --save figures
```

### Paràmetres CLI

| Flag | Default | Descripció |
|------|---------|------------|
| `--width` | 400 | Amplada del grid (cel·les) |
| `--height` | 400 | Alçada del grid (cel·les) |
| `--days` | 365 | Dies de simulació |
| `--res` | 25 | Resolució (m/cel·la) |
| `--output` | "output" | Directori de sortida |
| `--data-dir` | "../ecosystem/data" | Directori amb dades de terreny |
| `--demo` | — | Atajo: 50×50, 30 dies |

### Execució a escala completa

```bash
./run_simulation.sh --full --days 365
```

Carrega el grid real de 375×502 cel·les (188.250 cel·les, ~80.000 ha).
**Nota**: pot trigar diversos minuts.

---

## Com funciona

### 1. Inicialització

1. Es carrega el TSV de terreny (`terrain_cells.tsv`) amb elevació, pendent, aspecte,
   TRI i pisos bioclimàtics de cada cel·la.
2. El piso determina l'hàbitat (10 tipus funcionals: bosc, pasturatge, roca, etc.)
3. Cada hàbitat té biomasa inicial de plantes i invertebrats.
4. Es generen agents amb variació individual:
   - **Pes**: ±20% del pes mitjà de l'espècie
   - **Gènere**: Male/Female (aleatori 50/50)
   - **Edat inicial**: fins al 25% de l'esperança de vida
   - **Personalitat** (`boldness` 0-1): afecta decisions
   - Agents apareixen en cel·les d'hàbitat adequat per a la seva espècie

### 2. Bucle diari

Cada dia:
1. **Ambient**: avança el dia, calcula estació
2. **Neu**: càlcul de cobertura nival segons elevació i dia de l'any
3. **Temperatura**: gradient adiabàtic (-6.5°C/km) amb oscil·lació estacional
4. **Pools**: creixement logístic de plantes, invertebrats, peixos, herps, aus, micromamífers
5. **Carronya**: decadència del 5%/dia
6. **Agents** (paral·lelitzat amb Rayon):
   - Fase 1: cada agent **decideix** què fer (independent, només llegeix grid)
   - Fase 2: cada agent **executa** l'acció (escriu al grid)
   - Accions possibles: Foragejar, Moure's, Explorar, Descansar
7. **Depredació**: carnívors maten preses a la mateixa cel·la
8. **Pools**: agents consumeixen peixos/micromamífers segons dieta
9. **Carronyeig**: espècies amb dieta carronya consumeixen cadàvers
10. **Reproducció**: només primavera/estiu, femelles amb energia suficient
11. **Neteja**: eliminació d'agents morts

### 3. Comportament dels agents (estocàstic)

- **Herbívors**: forragegen si la cel·la té prou plantes; si no, busquen millor cel·la
  (amb probabilitat 85% d'anar a la millor, 15% de vagar aleatòriament)
- **Carnívors**: busquen zones amb alta biomassa (probabilitat de presa), cacen segons
  enllaços tròfics ponderats
- **Omnívors**: ponderen planta/invertebrat/carroña segons la seva dieta
- **Tots**: 5% probabilitat d'inactivitat, 8% d'exploració aleatòria
- **Forrajeig**: èxit variable 60-100%

### 4. Metabolisme energètic

Basat en la llei de Kleiber:

```math
BMR = 70 × M^{0.75}  kcal/dia
DEE = BMR_h × (hores_activitat × MET)
```

| Activitat | MET | Hores/dia |
|-----------|-----|-----------|
| Repòs | 1.0 | 11 |
| Forrajeig | 2.0 | 8 |
| Locomoció | 2.5-6.0 (pendent) | 1 |
| Altres | 1.5 | 4 |

**Modificadors**:
- **Fred**: +2 hores a MET 2.0 si temperatura mitjana < -3°C
- **Lactància**: ×1.4

**Reserva energètica inicial**: 10.000 kcal/kg de massa

### 5. Dieta i xarxa tròfica

Cada espècie té proporcions definides de planta/invertebrat/vertebrat/carroña/peix.
Aquestes proporcions s'usen per:

- **Forrajeig**: `do_forage()` consumeix plantes i invertebrats segons la dieta
- **Depredació**: `predation_step()` usa `get_prey()` per matar preses
- **Pools**: `pool_consumption_step()` consumeix dels pools poblacionals
- **Carronyeig**: `scavenging_step()` amb `consume_carcass()`

### 6. Reproducció

- Només en primavera o estiu
- Només femelles (mascles no s'aparellen explícitament)
- Requisits:
  - `days_since_reproduction > reproductive_age_days` (específic per espècie)
  - Energia > llindar (2000-3000 kcal/kg segons tipus)
  - No embarassada, no lactant
  - 30% de probabilitat estocàstica
- Gestació: específica per espècie (23-280 dies)
- Tamaño de camada: específic per espècie
- Lactància: 60 dies post-part

### 7. Sortides

| Fitxer | Format | Contingut |
|--------|--------|-----------|
| `simulation_log.csv` | CSV | Dia a dia: vius, morts, biomassa vegetal/invertebrats/carronya, energia mitja, estació, temperatura |
| `species_population.csv` | CSV | Dia a dia: població per espècie (18 columnes) |
| `snap_NNNN.json` | JSON | Cada 100 dies: estat complet de tots els agents (posició, espècie, gènere, pes, energia, edat, embaràs) i pools |

### 8. Visualització Python

```bash
python3 src/visualize_simulation.py --dir ecosystem_simulator_rs/output --save figures
```

Genera 4 figures:
1. **overview.png**: poblacions totals, biomassa vegetal, energia, temperatura
2. **species_populations.png**: evolució de cada espècie (línies individuals)
3. **species_stacked.png**: àrea apilada de totes les espècies
4. **energy_balance.png**: reserves energètiques al llarg del temps

---

## Espècies modelades (18)

| Espècie | Català | Tipus | Massa (kg) | Gestació (dies) | Camada | Edat reprod. (dies) | Longevitat (anys) |
|---------|--------|-------|-----------|-----------------|--------|-------------------|-------------------|
| Rupicapra_pyrenaica | Isard | Herbívor | 35 | 165 | 1 | 1 | 16 |
| Cervus_elaphus | Cérvol | Herbívor | 200 | 235 | 1 | 2 | 20 |
| Capreolus_capreolus | Cabirol | Herbívor | 20 | 280 | 1-2 | 1 | 16 |
| Sus_scrofa | Senglar | Omnívor | 100 | 115 | 4-8 | 1 | 12 |
| Marmota_marmota | Marmota | Herbívor | 4.5 | 34 | 2-6 | 1 | 15 |
| Oryctolagus_cuniculus | Conill | Herbívor | 1.2 | 30 | 3-8 | 0.3 | 4 |
| Sciurus_vulgaris | Esquirol | Herbívor | 0.3 | 38 | 2-5 | 1 | 6 |
| Vulpes_vulpes | Guineu | Omnívor | 6 | 53 | 3-6 | 1 | 8 |
| Meles_meles | Teixó | Omnívor | 11 | 60 | 2-4 | 1 | 12 |
| Martes_martes | Marta | Carnívor | 1.5 | 30 | 2-4 | 1 | 10 |
| Felis_silvestris | Gat fer | Carnívor | 4 | 65 | 2-4 | 1 | 12 |
| Mustela_erminea | Ermíni | Carnívor | 0.15 | 42 | 4-8 | 1 | 6 |
| Mustela_nivalis | Mostela | Carnívor | 0.08 | 35 | 4-8 | 0.3 | 4 |
| Tetrao_urogallus | Gall fer | Herbívor | 4 | 26 | 6-12 | 1 | 7 |
| Lagopus_muta | Perdiu xerra | Herbívor | 0.5 | 23 | 5-10 | 1 | 4 |
| Corvus_corax | Corb | Omnívor | 1 | 21 | 3-7 | 1 | 20 |
| Gypaetus_barbatus | Trencalòs | Carronyaire | 5.5 | 55 | 1-2 | 5 | 30 |
| Aquila_chrysaetos | Àguila reial | Carnívor | 4 | 45 | 1-3 | 4 | 25 |

---

## Limitacions actuals

- **Comportament de cerca**: els agents no detecten preses/recursos a llarga distància
- **Aparellament**: no hi ha còpula explícita (mascles i femelles no interactuen)
- **Hibernació**: la marmota no hiberna
- **Migració**: cap espècie es desplaça altitudinalment
- **Creixement**: model senzill (0.5%/dia fins a massa adulta)
- **Malalties**: no modelades
- **Competència**: no hi ha competència intra/interespecífica explícita
