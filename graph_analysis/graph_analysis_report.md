# Anàlisi de Xarxa Tròfica — Parc Natural de l'Alt Pirineu

## Estadístiques Globals

| Mètrica | Valor |
|---------|-------|
| Nodes totals (incl. clústers) | 75 |
| Arestes totals | 191 |
| Nodes (sense clustermember) | 75 |
| Arestes (sense clustermember) | 169 |
| Densitat del graf | 0.0305 |
| Nombre de components connectats | 8 |
| Coeficient d'agrupament (mitjà) | 0.1359 |
| Diàmetre (component gegant) | N/A (no connectat) |
| Grau de sortida (out-degree) mitjà | 2.25 |
| Grau d'entrada (in-degree) mitjà | 2.25 |
| Grau màxim de sortida | 16 |
| Grau màxim d'entrada | 33 |

## Espècies clau (Keystone) — Top 10 per Betweenness Centrality

La betweenness centrality mesura quantes rutes tròfiques passen per un node, identificant espècies pont crítiques per al flux d'energia:

1. **Corb** (Corvus corax) [Aves] — B=0.00164, D=0.16216, E=0.0
1. **Truita de riu autòctona** (Salmo trutta) [Actinopterygii] — B=0.00133, D=0.09459, E=0.0
1. **Gall fer** (Tetrao urogallus (subsp. pirenaica)) [Aves] — B=0.00114, D=0.09459, E=0.0
1. **Teixó** (Meles meles) [Mammalia] — B=0.00105, D=0.12162, E=0.0
1. **Esquirol** (Sciurus vulgaris) [Mammalia] — B=0.00098, D=0.10811, E=0.0
1. **Micromamífers petits** (V-MicromamífersPetits) [Cluster_Vertebrat] — B=0.00097, D=0.16216, E=0.0
1. **Passeriformes (ocells insectívors)** (V-Passeriformes) [Cluster_Vertebrat] — B=0.00065, D=0.16216, E=0.0
1. **🕷️ Depredadors/Parasitoides** (Formicidae) [Formicidae] — B=0.00061, D=0.06757, E=0.22941
1. **🐛 Fitòfags** (Hemiptera) [Hemiptera] — B=0.00056, D=0.06757, E=0.22941
1. **Conill** (Oryctolagus cuniculus) [Mammalia] — B=0.00056, D=0.12162, E=0.0

## Posició dels Clústers Vertebrats en el Rànquing de Centralitat

- **Micromamífers petits** (V-MicromamífersPetits) — Rang #6 en betweenness, B=0.00097
- **Passeriformes (ocells insectívors)** (V-Passeriformes) — Rang #7 en betweenness, B=0.00065
- **Insectívors mitjans** (V-InsectívorsMitjans) — Rang #12 en betweenness, B=0.00016
- **Rapinyaires nocturnes petites** (V-RapinyairesNocturnesPetites) — Rang #18 en betweenness, B=4e-05
- **Ratpenats (quiròpters)** (V-Ratpenats) — Rang #66 en betweenness, B=0.0
- **Rapinyaires nocturnes grans** (V-RapinyairesNocturnesGrans) — Rang #67 en betweenness, B=0.0

## Anàlisi de Centralitat

Nodes ordenats per betweenness centrality (nodes amb més influència com a ponts tròfics):

| Rang | Node | Label | Taxon | Degree Centrality | Betweenness Centrality | Eigenvector Centrality |
|------|------|-------|-------|------------------|------------------------|------------------------|
| 1 | Corvus corax | Corb | Aves | 0.16216 | 0.00164 | 0.0 |
| 2 | Salmo trutta | Truita de riu autòctona | Actinopterygii | 0.09459 | 0.00133 | 0.0 |
| 3 | Tetrao urogallus (subsp. pirenaica) | Gall fer | Aves | 0.09459 | 0.00114 | 0.0 |
| 4 | Meles meles | Teixó | Mammalia | 0.12162 | 0.00105 | 0.0 |
| 5 | Sciurus vulgaris | Esquirol | Mammalia | 0.10811 | 0.00098 | 0.0 |
| 6 | V-MicromamífersPetits | Micromamífers petits | Cluster_Vertebrat | 0.16216 | 0.00097 | 0.0 |
| 7 | V-Passeriformes | Passeriformes (ocells insectívors) | Cluster_Vertebrat | 0.16216 | 0.00065 | 0.0 |
| 8 | Formicidae | 🕷️ Depredadors/Parasitoides | Formicidae | 0.06757 | 0.00061 | 0.22941 |
| 9 | Hemiptera | 🐛 Fitòfags | Hemiptera | 0.06757 | 0.00056 | 0.22941 |
| 10 | Oryctolagus cuniculus | Conill | Mammalia | 0.12162 | 0.00056 | 0.0 |
| 11 | Phoxinus spp. | Barb roig / veró | Actinopterygii | 0.04054 | 0.00019 | 0.0 |
| 12 | V-InsectívorsMitjans | Insectívors mitjans | Cluster_Vertebrat | 0.12162 | 0.00016 | 0.0 |
| 13 | Marmota marmota | Marmota alpina | Mammalia | 0.05405 | 9e-05 | 0.0 |
| 14 | Rupicapra pyrenaica pyrenaica | Isard pirinenc | Mammalia | 0.04054 | 4e-05 | 0.0 |
| 15 | Capreolus capreolus | Cabirol | Mammalia | 0.04054 | 4e-05 | 0.0 |
| 16 | Ovis aries musimon | Mufló | Mammalia | 0.04054 | 4e-05 | 0.0 |
| 17 | Dama dama | Daina | Mammalia | 0.04054 | 4e-05 | 0.0 |
| 18 | V-RapinyairesNocturnesPetites | Rapinyaires nocturnes petites | Cluster_Vertebrat | 0.06757 | 4e-05 | 0.0 |
| 19 | Cervus elaphus | Cérvol | Mammalia | 0.02703 | 2e-05 | 0.0 |
| 20 | Sus scrofa | Porc senglar | Mammalia | 0.02703 | 2e-05 | 0.0 |
| 21 | Ursus arctos arctos | Ós bru | Mammalia | 0.21622 | 0.0 | 0.0 |
| 22 | Aphididae | 🐛 Fitòfags | Aphididae | 0.02703 | 0.0 | 0.22941 |
| 23 | I2 | 🐛 Fitòfags | Cluster_Invertebrat | 0.0 | 0.0 | 0.0 |
| 24 | Coleoptera | 🐛 Fitòfags | Coleoptera | 0.01351 | 0.0 | 0.22941 |
| 25 | Diptera | 🐛 Fitòfags | Diptera | 0.02703 | 0.0 | 0.22941 |
| 26 | Ephemeroptera | 🐛 Fitòfags | Ephemeroptera | 0.01351 | 0.0 | 0.0 |
| 27 | Lepidoptera | 🐛 Fitòfags | Lepidoptera | 0.01351 | 0.0 | 0.0 |
| 28 | Orthoptera | 🐛 Fitòfags | Orthoptera | 0.04054 | 0.0 | 0.0 |
| 29 | Plecoptera | 🐛 Fitòfags | Plecoptera | 0.01351 | 0.0 | 0.0 |
| 30 | Thaumetopoea pityocampa | 🐛 Fitòfags | Thaumetopoea pityocampa | 0.01351 | 0.0 | 0.0 |

## Detecció de Comunitats Tròfiques

Algorisme: Girvan-Newman (edge betweenness)
Nombre de comunitats detectades: 9

### Comunitat 1 (59 nodes)
  - 🐛 Fitòfags (Aphididae) [Aphididae]
  - Àguila reial (Aquila chrysaetos) [Aves]
  - 🕷️ Depredadors/Parasitoides (Araneae) [Araneae]
  - Boixerola (Arctostaphylos uva-ursi) [Plantae]
  - Bistorta (Bistorta officinalis) [Plantae]
  - 🐝 Pol·linitzadors (Boloria eunomia) [Boloria eunomia]
  - 🐝 Pol·linitzadors (Bombus spp.) [Bombus spp.]
  - Gripau comú (Bufo bufo) [Amphibia]
  - Cabirol (Capreolus capreolus) [Mammalia]
  - Cérvol (Cervus elaphus) [Mammalia]
  - 🐛 Fitòfags (Coleoptera) [Coleoptera]
  - Corb (Corvus corax) [Aves]
  - Corydalis (Corydalis spp.) [Plantae]
  - Daina (Dama dama) [Mammalia]
  - 🐛 Fitòfags (Diptera) [Diptera]
  - Faig (Fagus sylvatica) [Plantae]
  - Gat fer (Felis silvestris) [Mammalia]
  - 🌾 Prats i Pastures (Festuca spp.) [Festuca spp.]
  - 🕷️ Depredadors/Parasitoides (Formicidae) [Formicidae]
  - Almesquera (desmàn ibèric) (Galemys pyrenaicus) [Mammalia]
  - Trencalòs (Gypaetus barbatus) [Aves]
  - 🐛 Fitòfags (Hemiptera) [Hemiptera]
  - Sargantana pallaresa (Iberolacerta aurelioi) [Reptilia]
  - 🕷️ Depredadors/Parasitoides (Ichneumonidae_Braconidae) [Ichneumonidae_Braconidae]
  - Perdiu xerra (Lagopus muta) [Aves]
  - 🐛 Fitòfags (Lepidoptera) [Lepidoptera]
  - Marmota alpina (Marmota marmota) [Mammalia]
  - Marta (Martes martes) [Mammalia]
  - Teixó (Meles meles) [Mammalia]
  - Ermíni (Mustela erminea) [Mammalia]
  - Mostela (Mustela nivalis) [Mammalia]
  - 🌾 Prats i Pastures (Nardus stricta) [Nardus stricta]
  - 🐛 Fitòfags (Orthoptera) [Orthoptera]
  - Conill (Oryctolagus cuniculus) [Mammalia]
  - Mufló (Ovis aries musimon) [Mammalia]
  - 🌼 Plantes Entomòfiles (P1) [Cluster_Planta]
  - 🌾 Prats i Pastures (P3) [Cluster_Planta]
  - 🐝 Pol·linitzadors (Parnassius mnemosyne) [Parnassius mnemosyne]
  - Pi roig (Pinus sylvestris) [Plantae]
  - Pi negre (Pinus uncinata) [Plantae]
  - Sargantana roquera (Podarcis muralis) [Reptilia]
  - Roure (Quercus spp.) [Plantae]
  - Granota roja (Rana temporaria) [Amphibia]
  - Isard pirinenc (Rupicapra pyrenaica pyrenaica) [Mammalia]
  - Salamandra (Salamandra salamandra) [Amphibia]
  - Esquirol (Sciurus vulgaris) [Mammalia]
  - Porc senglar (Sus scrofa) [Mammalia]
  - Gall fer (Tetrao urogallus (subsp. pirenaica)) [Aves]
  - Ós bru (Ursus arctos arctos) [Mammalia]
  - Insectívors mitjans (V-InsectívorsMitjans) [Cluster_Vertebrat]
  - Micromamífers petits (V-MicromamífersPetits) [Cluster_Vertebrat]
  - Passeriformes (ocells insectívors) (V-Passeriformes) [Cluster_Vertebrat]
  - Rapinyaires nocturnes grans (V-RapinyairesNocturnesGrans) [Cluster_Vertebrat]
  - Rapinyaires nocturnes petites (V-RapinyairesNocturnesPetites) [Cluster_Vertebrat]
  - Ratpenats (quiròpters) (V-Ratpenats) [Cluster_Vertebrat]
  - 🌼 Plantes Entomòfiles (Vaccinium myrtillus) [Vaccinium myrtillus]
  - 🌱 Recursos Vegetals (Various) [Recursos Vegetals]
  - Guineu (Vulpes vulpes) [Mammalia]
  - Sargantana vivípara (Zootoca vivipara) [Reptilia]

### Comunitat 2 (8 nodes)
  - Tritó pirinenc (Calotriton asper) [Amphibia]
  - 🐛 Fitòfags (Ephemeroptera) [Ephemeroptera]
  - Llúdriga (Lutra lutra) [Mammalia]
  - 🌿 Productors Independents (P2) [Cluster_Planta]
  - Barb roig / veró (Phoxinus spp.) [Actinopterygii]
  - 🐛 Fitòfags (Plecoptera) [Plecoptera]
  - Truita de riu autòctona (Salmo trutta) [Actinopterygii]
  - 🐛 Fitòfags (Trichoptera) [Trichoptera]

### Comunitat 3 (2 nodes)
  - Pins (Pinus spp.) [Plantae]
  - 🐛 Fitòfags (Thaumetopoea pityocampa) [Thaumetopoea pityocampa]

### Comunitat 4 (1 nodes)
  - 🐛 Fitòfags (I2) [Cluster_Invertebrat]

### Comunitat 5 (1 nodes)
  - 🕷️ Depredadors/Parasitoides (I3) [Cluster_Invertebrat]

### Comunitat 6 (1 nodes)
  - 🐝 Pol·linitzadors (I1) [Cluster_Invertebrat]

### Comunitat 7 (1 nodes)
  - Cua de cavall aquàtica (Hippuris vulgaris) [Plantae]

### Comunitat 8 (1 nodes)
  - Falgueres (Pteridòfits) (Pteridophyta) [Plantae]

### Comunitat 9 (1 nodes)
  - Molses (Briòfits) (Bryophyta) [Plantae]

## Cadenes Tròfiques a través dels Clústers Vertebrats

### V-Passeriformes — Passeriformes (ocells insectívors)

Cadenes tròfiques representatives (depredador → clúster → presa):

  -   Ós bru (Ursus arctos arctos) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  -   Ós bru (Ursus arctos arctos) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)
  -   Marta (Martes martes) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  -   Marta (Martes martes) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)
  -   Guineu (Vulpes vulpes) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  -   Guineu (Vulpes vulpes) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)
  -   Gat fer (Felis silvestris) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  -   Gat fer (Felis silvestris) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)
  -   Mostela (Mustela nivalis) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  -   Mostela (Mustela nivalis) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)

Cadenes esteses (5 nivells):

  - Ós bru (Ursus arctos arctos) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  - Ós bru (Ursus arctos arctos) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)
  - Marta (Martes martes) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  - Marta (Martes martes) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)
  - Guineu (Vulpes vulpes) → Passeriformes (ocells insectívors) → 🌱 Recursos Vegetals (Various)
  - Guineu (Vulpes vulpes) → Passeriformes (ocells insectívors) → 🌼 Plantes Entomòfiles (P1)

---

### V-Ratpenats — Ratpenats (quiròpters)

Cadenes tròfiques representatives (depredador → clúster → presa):

  -   Marta (Martes martes) → Ratpenats (quiròpters) → 🌱 Recursos Vegetals (Various)
  -   Guineu (Vulpes vulpes) → Ratpenats (quiròpters) → 🌱 Recursos Vegetals (Various)
  -   Gat fer (Felis silvestris) → Ratpenats (quiròpters) → 🌱 Recursos Vegetals (Various)

Cadenes esteses (5 nivells):

  - Marta (Martes martes) → Ratpenats (quiròpters) → 🌱 Recursos Vegetals (Various)
  - Guineu (Vulpes vulpes) → Ratpenats (quiròpters) → 🌱 Recursos Vegetals (Various)
  - Gat fer (Felis silvestris) → Ratpenats (quiròpters) → 🌱 Recursos Vegetals (Various)

---

### V-RapinyairesNocturnesGrans — Rapinyaires nocturnes grans

  _No té depredadors directes (depredador apical o base de cadena)_

Cadenes esteses (5 nivells):


---

### V-RapinyairesNocturnesPetites — Rapinyaires nocturnes petites

Cadenes tròfiques representatives (depredador → clúster → presa):

  -   Marta (Martes martes) → Rapinyaires nocturnes petites → Micromamífers petits (V-MicromamífersPetits)
  -   Marta (Martes martes) → Rapinyaires nocturnes petites → 🌱 Recursos Vegetals (Various)
  -   Guineu (Vulpes vulpes) → Rapinyaires nocturnes petites → Micromamífers petits (V-MicromamífersPetits)
  -   Guineu (Vulpes vulpes) → Rapinyaires nocturnes petites → 🌱 Recursos Vegetals (Various)
  -   Rapinyaires nocturnes grans (V-RapinyairesNocturnesGrans) → Rapinyaires nocturnes petites → Micromamífers petits (V-MicromamífersPetits)
  -   Rapinyaires nocturnes grans (V-RapinyairesNocturnesGrans) → Rapinyaires nocturnes petites → 🌱 Recursos Vegetals (Various)

Cadenes esteses (5 nivells):

  - Marta (Martes martes) → Rapinyaires nocturnes petites → Micromamífers petits (V-MicromamífersPetits) → 🌱 Recursos Vegetals (Various) → 🌾 Prats i Pastures (P3)
  - Marta (Martes martes) → Rapinyaires nocturnes petites → 🌱 Recursos Vegetals (Various)
  - Guineu (Vulpes vulpes) → Rapinyaires nocturnes petites → Micromamífers petits (V-MicromamífersPetits) → 🌱 Recursos Vegetals (Various) → 🌾 Prats i Pastures (P3)
  - Guineu (Vulpes vulpes) → Rapinyaires nocturnes petites → 🌱 Recursos Vegetals (Various)
  - Rapinyaires nocturnes grans (V-RapinyairesNocturnesGrans) → Rapinyaires nocturnes petites → Micromamífers petits (V-MicromamífersPetits) → 🌱 Recursos Vegetals (Various) → 🌾 Prats i Pastures (P3)
  - Rapinyaires nocturnes grans (V-RapinyairesNocturnesGrans) → Rapinyaires nocturnes petites → 🌱 Recursos Vegetals (Various)

---

### V-MicromamífersPetits — Micromamífers petits

Cadenes tròfiques representatives (depredador → clúster → presa):

  -   Marta (Martes martes) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  -   Marta (Martes martes) → Micromamífers petits → 🌾 Prats i Pastures (P3)
  -   Guineu (Vulpes vulpes) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  -   Guineu (Vulpes vulpes) → Micromamífers petits → 🌾 Prats i Pastures (P3)
  -   Gat fer (Felis silvestris) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  -   Gat fer (Felis silvestris) → Micromamífers petits → 🌾 Prats i Pastures (P3)
  -   Mostela (Mustela nivalis) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  -   Mostela (Mustela nivalis) → Micromamífers petits → 🌾 Prats i Pastures (P3)
  -   Ermíni (Mustela erminea) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  -   Ermíni (Mustela erminea) → Micromamífers petits → 🌾 Prats i Pastures (P3)

Cadenes esteses (5 nivells):

  - Marta (Martes martes) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  - Marta (Martes martes) → Micromamífers petits → 🌾 Prats i Pastures (P3)
  - Guineu (Vulpes vulpes) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  - Guineu (Vulpes vulpes) → Micromamífers petits → 🌾 Prats i Pastures (P3)
  - Gat fer (Felis silvestris) → Micromamífers petits → 🌱 Recursos Vegetals (Various)
  - Gat fer (Felis silvestris) → Micromamífers petits → 🌾 Prats i Pastures (P3)

---

### V-InsectívorsMitjans — Insectívors mitjans

Cadenes tròfiques representatives (depredador → clúster → presa):

  -   Marta (Martes martes) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  -   Marta (Martes martes) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)
  -   Guineu (Vulpes vulpes) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  -   Guineu (Vulpes vulpes) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)
  -   Gat fer (Felis silvestris) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  -   Gat fer (Felis silvestris) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)
  -   Àguila reial (Aquila chrysaetos) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  -   Àguila reial (Aquila chrysaetos) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)
  -   Teixó (Meles meles) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  -   Teixó (Meles meles) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)

Cadenes esteses (5 nivells):

  - Marta (Martes martes) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  - Marta (Martes martes) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)
  - Guineu (Vulpes vulpes) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  - Guineu (Vulpes vulpes) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)
  - Gat fer (Felis silvestris) → Insectívors mitjans → 🌱 Recursos Vegetals (Various)
  - Gat fer (Felis silvestris) → Insectívors mitjans → 🌼 Plantes Entomòfiles (P1)

---

## Subgrafs dels Clústers Vertebrats

## Subgraf del clúster: V-Passeriformes
**Passeriformes (ocells insectívors)**

- **Nodes totals al subgraf (radi 1):** 13
- **Arestes al subgraf:** 29

### Depredadors (qui el consumeix)
  - **Teixó** (Meles meles) [Mammalia] — predation (low)
  - **Marta** (Martes martes) [Mammalia] — predation (high)
  - **Guineu** (Vulpes vulpes) [Mammalia] — predation (medium)
  - **Mostela** (Mustela nivalis) [Mammalia] — predation (medium)
  - **Ós bru** (Ursus arctos arctos) [Mammalia] — predation (low)
  - **Corb** (Corvus corax) [Aves] — predation (medium)
  - **Àguila reial** (Aquila chrysaetos) [Aves] — predation (medium)
  - **Rapinyaires nocturnes grans** (V-RapinyairesNocturnesGrans) [Cluster_Vertebrat] — predation (high)
  - **Ermíni** (Mustela erminea) [Mammalia] — predation (medium)
  - **Gat fer** (Felis silvestris) [Mammalia] — predation (high)

### Preses (a qui consumeix)
  - **🌱 Recursos Vegetals** (Various) [Recursos Vegetals] — entomophagy (high)
  - **🌼 Plantes Entomòfiles** (P1) [Cluster_Planta] — frugivory (medium)

## Subgraf del clúster: V-Ratpenats
**Ratpenats (quiròpters)**

- **Nodes totals al subgraf (radi 1):** 5
- **Arestes al subgraf:** 7

### Depredadors (qui el consumeix)
  - **Guineu** (Vulpes vulpes) [Mammalia] — predation (low)
  - **Gat fer** (Felis silvestris) [Mammalia] — predation (medium)
  - **Marta** (Martes martes) [Mammalia] — predation (medium)

### Preses (a qui consumeix)
  - **🌱 Recursos Vegetals** (Various) [Recursos Vegetals] — entomophagy (high)

## Subgraf del clúster: V-RapinyairesNocturnesGrans
**Rapinyaires nocturnes grans**

- **Nodes totals al subgraf (radi 1):** 7
- **Arestes al subgraf:** 10

### Depredadors (qui el consumeix)
  - Cap depredador directe

### Preses (a qui consumeix)
  - **Micromamífers petits** (V-MicromamífersPetits) [Cluster_Vertebrat] — predation (high)
  - **Passeriformes (ocells insectívors)** (V-Passeriformes) [Cluster_Vertebrat] — predation (high)
  - **Rapinyaires nocturnes petites** (V-RapinyairesNocturnesPetites) [Cluster_Vertebrat] — predation (medium)
  - **Conill** (Oryctolagus cuniculus) [Mammalia] — predation (medium)
  - **Insectívors mitjans** (V-InsectívorsMitjans) [Cluster_Vertebrat] — predation (medium)
  - **Corb** (Corvus corax) [Aves] — predation (medium)

## Subgraf del clúster: V-RapinyairesNocturnesPetites
**Rapinyaires nocturnes petites**

- **Nodes totals al subgraf (radi 1):** 6
- **Arestes al subgraf:** 11

### Depredadors (qui el consumeix)
  - **Guineu** (Vulpes vulpes) [Mammalia] — predation (medium)
  - **Rapinyaires nocturnes grans** (V-RapinyairesNocturnesGrans) [Cluster_Vertebrat] — predation (medium)
  - **Marta** (Martes martes) [Mammalia] — predation (medium)

### Preses (a qui consumeix)
  - **Micromamífers petits** (V-MicromamífersPetits) [Cluster_Vertebrat] — predation (high)
  - **🌱 Recursos Vegetals** (Various) [Recursos Vegetals] — entomophagy (high)

## Subgraf del clúster: V-MicromamífersPetits
**Micromamífers petits**

- **Nodes totals al subgraf (radi 1):** 13
- **Arestes al subgraf:** 27

### Depredadors (qui el consumeix)
  - **Teixó** (Meles meles) [Mammalia] — predation (medium)
  - **Marta** (Martes martes) [Mammalia] — predation (high)
  - **Guineu** (Vulpes vulpes) [Mammalia] — predation (high)
  - **Mostela** (Mustela nivalis) [Mammalia] — predation (high)
  - **Corb** (Corvus corax) [Aves] — predation (medium)
  - **Rapinyaires nocturnes grans** (V-RapinyairesNocturnesGrans) [Cluster_Vertebrat] — predation (high)
  - **Àguila reial** (Aquila chrysaetos) [Aves] — predation (high)
  - **Rapinyaires nocturnes petites** (V-RapinyairesNocturnesPetites) [Cluster_Vertebrat] — predation (high)
  - **Ermíni** (Mustela erminea) [Mammalia] — predation (high)
  - **Gat fer** (Felis silvestris) [Mammalia] — predation (high)

### Preses (a qui consumeix)
  - **🌱 Recursos Vegetals** (Various) [Recursos Vegetals] — entomophagy (low)
  - **🌾 Prats i Pastures** (P3) [Cluster_Planta] — herbivory (high)

## Subgraf del clúster: V-InsectívorsMitjans
**Insectívors mitjans**

- **Nodes totals al subgraf (radi 1):** 10
- **Arestes al subgraf:** 23

### Depredadors (qui el consumeix)
  - **Teixó** (Meles meles) [Mammalia] — predation (medium)
  - **Marta** (Martes martes) [Mammalia] — predation (low)
  - **Guineu** (Vulpes vulpes) [Mammalia] — predation (high)
  - **Corb** (Corvus corax) [Aves] — predation (low)
  - **Rapinyaires nocturnes grans** (V-RapinyairesNocturnesGrans) [Cluster_Vertebrat] — predation (medium)
  - **Àguila reial** (Aquila chrysaetos) [Aves] — predation (medium)
  - **Gat fer** (Felis silvestris) [Mammalia] — predation (medium)

### Preses (a qui consumeix)
  - **🌱 Recursos Vegetals** (Various) [Recursos Vegetals] — entomophagy (high)
  - **🌼 Plantes Entomòfiles** (P1) [Cluster_Planta] — frugivory (low)
