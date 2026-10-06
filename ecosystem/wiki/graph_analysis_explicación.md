# Anàlisi de Xarxa Tròfica — Parc Natural de l'Alt Pirineu

## Visió General

L'anàlisi de xarxa s'aplica sobre el graf dirigit de 75 nodes i 220 arestes (191 tròfiques + 29 clustermember) generat a partir de `trophic_matrix.tsv`. S'han exclòs les arestes de tipus `clustermember` per a les anàlisis de centralitat i comunitats, ja que aquestes arestes només indiquen pertinença a un clúster funcional i no representen interaccions tròfiques reals.

## Estadístiques Globals

| Mètrica | Valor |
|---------|-------|
| Nodes totals | 75 |
| Arestes totals | 220 |
| Arestes tròfiques (sense clustermember) | 191 |
| Densitat del graf | 0.0343 |
| Components connectats | 7 |
| Coeficient d'agrupament mitjà | 0.2141 |
| Grau de sortida (out-degree) mitjà | 2.55 |
| Grau d'entrada (in-degree) mitjà | 2.55 |
| Grau màxim de sortida | 17 |
| Grau màxim d'entrada | 42 |

La densitat baixa (0.034) és típica de xarxes tròfiques reals: cada espècie interactua amb un subconjunt reduït de la xarxa completa. El component principal conté 61 dels 75 nodes; els 14 restants són nodes de clúster sense arestes tròfiques directes (I1, I2, I3, P1, P2, P3) i les espècies representatives de P2 connectades via clustermember.

## Detecció de Comunitats (Girvan-Newman)

L'algorisme de Girvan-Newman basat en betweenness d'arestes ha detectat **7 comunitats**:

| Comunitat | Nodes | Descripció |
|-----------|-------|------------|
| 1 | 61 | Xarxa tròfica principal (tots els vertebrats, plantes, insectes i recursos) |
| 2 | 5 | Subxarxa especialitzada: Coleoptera, Diptera, Lepidoptera, Ichneumonidae, Iberolacerta aurelioi |
| 3-7 | 1 c/u | Nodes de clúster aïllats (I1, I2, I3, P1, P3) sense arestes tròfiques |

La comunitat principal (61 nodes) agrupa pràcticament tota la xarxa, cosa que indica que el graf és altament interconnectat. La comunitat 2 (5 nodes) és remarcable: agrupa la sargantana pallaresa (*Iberolacerta aurelioi*) amb els seus recursos principals (coleòpters, dípters, lepidòpters) i el parasitoidisme dels icneumònids sobre lepidòpters, formant un subsistema tròfic relativament aïllat de la resta de la xarxa.

## Espècies Clau (Keystone) — Top 10

La betweenness centrality identifica nodes que actuen com a ponts crítics en el flux d'energia:

| Rang | Espècie | Betweenness | Degree | Notes |
|------|---------|-------------|--------|-------|
| 1 | **Corb** (*Corvus corax*) | 0.00169 | 0.157 | Omnívor generalista, connecta múltiples nivells tròfics |
| 2 | **Truita** (*Salmo trutta*) | 0.00145 | 0.100 | Piscívor/insectívor, eix del sistema aquàtic |
| 3 | **Gall fer** (*Tetrao urogallus*) | 0.00124 | 0.100 | Connecta plantes alpines amb depredadors forestals |
| 4 | **Teixó** (*Meles meles*) | 0.00104 | 0.114 | Omnívor generalista, pont entre sòl i nivells superiors |
| 5 | **Esquirol** (*Sciurus vulgaris*) | 0.00083 | 0.100 | Granívor forestal, presa de múltiples depredadors |
| 6 | **Hemiptera** (Fitòfags) | 0.00062 | 0.071 | Insecte base, alta eigenvector (0.236) |
| 7 | **Formicidae** (Depredadors) | 0.00041 | 0.057 | Insecte connector, alta eigenvector (0.236) |
| 8 | **Conill** (*O. cuniculus*) | 0.00003 | 0.129 | Presa base per a múltiples carnívors |
| 9 | **V-Passeriformes** | 0.00003 | 0.157 | Clúster d'insectívors aeris |
| 10 | **V-MicromamífersPetits** | 0.00003 | 0.157 | Clúster de preses base |

## Posició dels Clústers Vertebrats a la Xarxa

### V-Passeriformes (Rang #9 en betweenness)
- **10 depredadors**: gat fer, marta, guineu, teixó, mostela, ermini, corb, òs bru, àguila reial, rapinyaires nocturnes grans
- **Preses**: recursos vegetals (frugivoria estacional)
- **Paper**: Clúster amb més connectivitat depredadora de tots els V-clústers. 12 nodes al subgraf.

### V-MicromamífersPetits (Rang #10 en betweenness)
- **10 depredadors**: gat fer, marta, guineu, teixó, mostela, ermini, corb, àguila reial, rapinyaires nocturnes grans i petites
- **Preses**: recursos vegetals (herbivoria)
- **Paper**: El clúster de preses més important de la xarxa — 10 depredadors diferents, la majoria amb confiança alta.

### V-RapinyairesNocturnesPetites (Rang #11)
- **3 depredadors**: marta, guineu, rapinyaires nocturnes grans
- **Preses**: micromamífers petits, recursos vegetals (insectes grans)
- **Paper**: Enllaç intermedi entre micromamífers i depredadors superiors.

### V-InsectívorsMitjans (Rang #12)
- **7 depredadors**: gat fer, guineu, teixó, marta, corb, àguila reial, rapinyaires nocturnes grans
- **Preses**: recursos vegetals
- **Paper**: Connecten sòl (cucs, larves) amb depredadors mitjans i grans.

### V-Ratpenats (Rang #66)
- **3 depredadors**: marta, gat fer, guineu (confiança medium-low)
- **Preses**: recursos vegetals (entomofàgia nocturna)
- **Paper**: Clúster petit i relativament aïllat; nínxol nocturn aeri.

### V-RapinyairesNocturnesGrans (Rang #67)
- **Sense depredadors** (apical nocturn)
- **6 preses**: micromamífers petits, passeriformes, rapinyaires nocturnes petites, conill, insectívors mitjans, corb
- **Paper**: Depredador apical nocturn; pressió sobre tots els clústers petits.

## Subgrafs dels Clústers

Cada clúster V té un subgraf d'1 radi d'interaccions tròfiques (excloent arestes de pertinença a clúster):

| Clúster | Nodes al subgraf | Arestes | Depredadors | Preses | Centralitat |
|---------|-----------------|---------|-------------|--------|-------------|
| V-Passeriformes | 13 | 29 | 10 | 2 (P1, Various entomophagy) | Alta connectivitat |
| V-MicromamífersPetits | 13 | 27 | 10 | 2 (P3, Various entomophagy) | Clúster presa més connectat |
| V-InsectívorsMitjans | 10 | 23 | 7 | 2 (P1, Various entomophagy) | Connexió sòl-nivell superior |
| V-RapinyairesNocturnesGrans | 7 | 10 | 0 (apical) | 6 (inclou 4 clústers V) | Depredador apical nocturn |
| V-RapinyairesNocturnesPetites | 6 | 11 | 3 (marta, guineu, V-RapGrans) | 2 (V-Micromamífers, P1/Various) | Enllaç intermedi |
| V-Ratpenats | 5 | 7 | 3 (marta, gat fer, guineu) | 1 (Various entomophagy) | Nínxol nocturn aïllat |

## Cadenes Tròfiques Representatives

### Cadena alpina nocturna
`V-RapinyairesNocturnesGrans → V-RapinyairesNocturnesPetites → V-MicromamífersPetits → Recursos Vegetals`

### Cadena forestal diürna
`Àguila reial → V-Passeriformes → Recursos Vegetals (insectes/fruits)`

### Cadena de depredació múltiple
`Marta → V-MicromamífersPetits → Recursos Vegetals`

### Cadena aquàtica
`Llúdriga → Salmo trutta → (Ephemeroptera, Plecoptera, Trichoptera) → algues/detritus`

### Cadena de carronyaire
`Trencalòs → Various (ossos d'ungulats)`

## Implicacions per a la Simulació

1. **V-MicromamífersPetits i V-Passeriformes** són els clústers més crítics — tenen més depredadors i més connectivitat. La seva dinàmica afectarà directament tots els carnívors mitjans i grans.

2. **V-RapinyairesNocturnesGrans** és l'únic clúster V sense depredadors — actua com a regulador top-down de la resta de clústers petits.

3. **V-Ratpenats** és el clúster més aïllat — la seva pèrdua afectaria principalment la marta i el gat fer, amb efectes limitats a la resta de la xarxa.

4. **L'ós bru** (node amb més out-degree: 17) és el vertebrat amb la dieta més diversa — connecta pràcticament tots els nivells tròfics.

5. **El corb** és l'espècie individual amb més betweenness — la seva omnivoria el converteix en un connector crític entre la carronya, els insectes, els petits vertebrats i els recursos vegetals.

## Enllaços relacionats
- [[ecosystem/data/trophic_matrix.tsv]]
- [[ecosystem/data/ecosystem_graph_standard.json]]
- [[ecosystem/data/ecosystem_graph_optimized.json]]
- [[graph_analysis/graph_analysis_report.md]]
- [[graph_analysis/analyze_graph.py]]
