# Mapa d'Hàbitats del Terreny — Vall de Cardós

**Data de generació:** 2026-06-22  
**Font:** MCSC (Mapa de Cobertes del Sòl de Catalunya) via ICGC WFS  
**Resolució:** 25 m  
**Extensió:** 375 × 502 cel·les (9.4 × 12.6 km)  
**Sistema de coordenades:** EPSG:25831 (ETRS89 / UTM zone 31N)  

## Procés

1. **Font de dades:** ICGC WFS `inspire:LC.LandCoverSurfaces` a `https://geoserveis.icgc.cat/geoserver/wfs`
2. **Àrea:** Vall de Cardós (bounding box: 355842E, 4711526N, 365217E, 4724076N)
3. **Descàrrega:** 7.946 polígons en format GML via consulta WFS GetFeature
4. **Classificació:** 28 classes MCSC → 10 classes funcionals de simulació
5. **Rasterització:** Amb `rasterio.features.rasterize` a la graella de 25m

## Classes d'Hàbitat (Vall de Cardós, àrea de test)

| Codi | Classe | Polígons | Cel·les | % Àrea |
|------|--------|----------|---------|--------|
| 1 | Bosc de coníferes (*Pinus uncinata*, *Abies alba*, *P. sylvestris*) | 1.136 | 58.434 | 31,0% |
| 2 | Bosc caducifoli (*Fagus sylvatica*, *Betula*, *Quercus*) | 1.389 | 40.189 | 21,3% |
| 3 | Matollar (*Rhododendron*, *Vaccinium*, *Calluna*) | 1.789 | 44.530 | 23,7% |
| 4 | Pasturatge alpí/subalpí | 1.432 | 28.562 | 15,2% |
| 5 | Zona humida / mollera | 29 | 251 | 0,1% |
| 6 | Roca / tartera | 1.898 | 13.336 | 7,1% |
| 7 | Aigua (llacs, embassaments, rius) | 52 | 486 | 0,3% |
| 8 | Bosc de ribera | 106 | 1.783 | 0,9% |
| 9 | Neu permanent | 0 | 0 | 0% |
| 10 | Antròpic (edificacions, carreteres) | 115 | 679 | 0,4% |

## Mapatge complet MCSC (44 classes → 10 hàbitats funcionals)

El mapa MCSC de Catalunya classifica el territori en 44 classes de cobertura del sòl (nivell 4).
La taula següent mostra el mapatge complet cap als 10 tipus d'hàbitat funcional de la simulació:

| Codi MCSC | Descripció | Hàbitat funcional | Codi hab. |
|-----------|-----------|-------------------|-----------|
| 111 | Teixit urbà continu | ANTROPICO | 10 |
| 112 | Teixit urbà discontinu | ANTROPICO | 10 |
| 121 | Zones industrials i comercials | ANTROPICO | 10 |
| 122 | Xarxes viàries i ferroviàries | ANTROPICO | 10 |
| 131 | Zones d'extracció minera | ANTROPICO | 10 |
| 132 | Abocadors | ANTROPICO | 10 |
| 133 | Zones en construcció | ANTROPICO | 10 |
| 141 | Zones verdes urbanes | ANTROPICO | 10 |
| 142 | Instal·lacions esportives | ANTROPICO | 10 |
| 211 | Cultius herbacis de secà | PASTIZAL | 4 |
| 212 | Cultius herbacis de regadiu | PASTIZAL | 4 |
| 221 | Vinyes | PASTIZAL | 4 |
| 222 | Fruiters | PASTIZAL | 4 |
| 223 | Oliveres | PASTIZAL | 4 |
| 231 | Pastures i prats naturals | PASTIZAL | 4 |
| 241 | Cultius anuals associats | PASTIZAL | 4 |
| 242 | Mosaic de cultius | PASTIZAL | 4 |
| 243 | Terrenys agrícoles amb vegetació | PASTIZAL | 4 |
| 311 | Bosc coníferes (*P. uncinata*, *P. sylvestris*, *Abies*) | BOSQUE_CON | 1 |
| 312 | Bosc coníferes (*P. nigra*, *P. halepensis*, *P. pinea*) | BOSQUE_CON | 1 |
| 313 | Bosc caducifolis (*Fagus*, *Quercus*, *Betula*) | BOSQUE_CAD | 2 |
| 314 | Bosc mixt coníferes-caducifolis | BOSQUE_CAD | 2 |
| 321 | Pastures i matollars | MATORRAL | 3 |
| 322 | Matollars (*Rhododendron*, *Vaccinium*, *Calluna*) | MATORRAL | 3 |
| 323 | Vegetació escleròfila | MATORRAL | 3 |
| 324 | Matollar de transició i clarianes | MATORRAL | 3 |
| 325 | Prats i herbagens | PASTIZAL | 4 |
| 331 | Roques nues, tarteres | ROCA | 6 |
| 332 | Roques nues glacials/periglacials | ROCA | 6 |
| 333 | Neu permanent i glaceres | NIEVE | 9 |
| 334 | Zones cremades | HUMEDAL | 5 |
| 411 | Molleres i aiguamolls d'alta muntanya | HUMEDAL | 5 |
| 412 | Torberes | HUMEDAL | 5 |
| 421 | Maresmes i salins | HUMEDAL | 5 |
| 511 | Llacs i estanys | AGUA | 7 |
| 512 | Embassaments | AGUA | 7 |
| 521 | Rius i rierols | AGUA | 7 |
| 522 | Boscos de ribera | RIBERA | 8 |
| 523 | Canals i basses artificials | AGUA | 7 |
| 501 | Pineda de pi negre (*Pinus uncinata*) | BOSQUE_CON | 1 |
| 502 | Pineda de pi roig (*Pinus sylvestris*) | BOSQUE_CON | 1 |
| 503 | Avetosa (*Abies alba*) | BOSQUE_CON | 1 |
| 504 | Fageda (*Fagus sylvatica*) | BOSQUE_CAD | 2 |
| 505 | Bedollar (*Betula pubescens*) | BOSQUE_CAD | 2 |
| 506 | Matollar de rododèndron | MATORRAL | 3 |
| 507 | Matollar de nabiu (*Vaccinium myrtillus*) | MATORRAL | 3 |

## Assignació de Biomassa

La biomassa inicial per cel·la s'assigna segons la taula de `plan_terreno_simulacion.md`:

| Hàbitat | P1 | P2 | P3 | I1 | I2 | I3 |
|---------|----|----|----|----|----|----|
| BOSQUE_CON | 1,5 | 0,3 | 0,5 | 0,02 | 0,15 | 0,08 |
| BOSQUE_CAD | 1,0 | 0,3 | 0,5 | 0,015 | 0,08 | 0,05 |
| MATORRAL | 2,0 | 0,2 | 1,5 | 0,03 | 0,08 | 0,05 |
| PASTIZAL | 1,0 | 0,1 | 4,0 | 0,03 | 0,15 | 0,06 |
| HUMEDAL | 2,0 | 1,0 | 0,5 | 0,025 | 0,06 | 0,04 |
| ROCA | 0,2 | 0,15 | 0,0 | 0,005 | 0,01 | 0,01 |
| AGUA | 0,0 | 1,0 | 0,0 | 0,0 | 0,02 | 0,01 |
| RIBERA | 1,0 | 0,8 | 1,5 | 0,02 | 0,08 | 0,05 |
| ANTROPICO | 0,1 | 0,05 | 0,2 | 0,005 | 0,005 | 0,005 |

**Biomassa total inicial:** 529.392 kg de plantes, 35.074 kg d'invertebrats

## Arxius generats

- `ecosystem/data/terrain_habitat.tif` — Mapa d'hàbitats (GeoTIFF, 83 KB)
- `ecosystem/data/terrain_biomass.tif` — Biomassa per cel·la (9 bandes, 5.2 MB)
- `output/maps/terrain_habitat.png` — Visualització del mapa d'hàbitats
- `output/maps/terrain_dashboard.png` — Dashboard complet (9 panells)
