# Graph Analysis — Alt Pirineu Ecosystem

This directory contains analysis of the trophic network graph for the
Parc Natural de l'Alt Pirineu ecosystem simulation.

## Files

- **`analyze_graph.py`** — Python analysis script (requires `networkx`, `numpy`)
  - Loads `ecosystem/data/ecosystem_graph_standard.json`
  - Computes centrality (degree, betweenness, eigenvector)
  - Detects communities (Girvan-Newman)
  - Extracts subgraphs for each V-cluster
  - Builds trophic chains through clusters
- **`graph_analysis_report.md`** — Full report in Catalan (380 lines)
- **`README.md`** — This file

## How to run

```bash
python3 graph_analysis/analyze_graph.py
```

## Key results summary

| Metric | Value |
|--------|-------|
| Nodes | 75 (71 original + P2 + 3 representative species) |
| Edges | 220 (191 trophic, 29 clustermember) |
| Density | 0.034 |
| Communities detected | 7 (1 main of 61 nodes + 6 satellite) |
| Top keystone (betweenness) | Corvus corax (0.00169) |

### V-cluster connectivity ranking (by betweenness centrality)
1. V-MicromamífersPetits — 13 nodes, 10 predators (B=0.00097, prey base cluster)
2. V-Passeriformes — 13 nodes, 10 predators (B=0.00065, insectivore cluster)
3. V-InsectívorsMitjans — 10 nodes, 7 predators (B=0.00016, soil link)
4. V-RapinyairesNocturnesPetites — 6 nodes, 3 predators (B=4e-05)
5. V-Ratpenats — 5 nodes, 3 predators (B=0.0, isolated niche)
6. V-RapinyairesNocturnesGrans — 7 nodes, 0 predators (B=0.0, nocturnal apex)

### Most connected individual species (by degree centrality)
1. Ós bru (Ursus arctos) — 0.2429
2. Corb (Corvus corax) — 0.1571
3. Conill (Oryctolagus cuniculus) — 0.1286
4. Teixó (Meles meles) — 0.1143
5. Truita (Salmo trutta) — 0.1000
