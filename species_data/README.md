# Species Data for Alt Pirineu Ecosystem Simulation

This directory contains structured data extracted from the biological documentation of the Parc Natural de l'Alt Pirineu for use in the agent-based ecosystem simulation.

## Files

### 1. [vertebrates.tsv](vertebrates.tsv)
Structured data of vertebrate species from the park with the following columns:
- `taxon_group`: taxonomic class (Mammalia, Aves, Reptilia, Amphibia, Actinopterygii)
- `scientific_name`: Latin scientific name
- `common_name_ca`: common name in Catalan
- `trophic_level`: general trophic level (Herbivore, Carnivore, Omnivore, etc.)
- `main_diet`: primary food sources described in Catalan
- `main_predators`: main predators of this species
- `reproduction_summary`: key reproductive biology information
- `body_mass_kg_approx`: approximate body mass range in kilograms

Contains 38 species and functional vertebrate clusters including:
- Herbivores: Isard, Cérvol, Cabirol, Mufló, Daina, Conill, Esquirol, Marmota
- Omnivores: Ós bru, Llúdriga, Almesquera, Marta, Guineu, Gat fer, Teixó, Senglar, Corb
- Carnivores: Mostela, Ermíni
- Birds: Gall fer, Perdiu xerra, Trencalòs, Àguila reial, Corb
- Reptiles: Sargantana pallaresa, Sargantana roquera, Sargantana vivípara
- Amphibians: Tritó pirinenc, Granota roja, Gripau comú, Salamandra
- Fish: Truita de riu autòctona, Barb roig/Veró
- Functional vertebrate clusters: V-Passeriformes, V-Ratpenats, V-RapinyairesNocturnesGrans, V-RapinyairesNocturnesPetites, V-MicromamífersPetits, V-InsectívorsMitjans

### 2. [plant_clusters.tsv](plant_clusters.tsv)
Functional plant groups for simulation modeling:
- `cluster_id`: P1, P2, P3
- `cluster_description`: descriptive name of the cluster
- `representative_species`: key species examples
- `ecological_function`: role in the ecosystem
- `reproduction_type`: how the plants reproduce
- `phenology`: seasonal growth patterns
- `notes`: additional ecological importance

Three plant clusters:
- **P1**: Entomophilous plants of forest floor and flowering meadows (dependent on external pollinators)
- **P2**: Independent producers (aquatic plants, ferns, bryophytes)
- **P3**: Rapid growth grasslands and pastures (base resource for herbivores)

### 3. [invertebrate_clusters.tsv](invertebrate_clusters.tsv)
Functional invertebrate groups:
- `cluster_id`: I1, I2, I3
- `cluster_description`: descriptive name
- `representative_species`: key species examples
- `ecological_function`: role in ecosystem
- `trophic_role`: feeding guild
- `key_interactions`: main ecological interactions
- `notes`: additional information

Three invertebrate clusters:
- **I1**: Mutualist pollinators (day-flying Lepidoptera, bumblebees)
- **I2**: Herbivores/phytophages (leaf consumers, potential pests)
- **I3**: Predators/parasitoids (biological control agents)

### 4. [trophic_matrix.tsv](trophic_matrix.tsv)
Machine-readable trophic interaction network:
- `consumer_taxon`: taxonomic group of consumer
- `consumer_scientific_name`: scientific name of consumer
- `resource_taxon`: taxonomic group of resource
- `resource_scientific_name`: scientific name of resource
- `interaction_type`: type of interaction (predation, herbivory, scavenging, parasitism, mutualism, etc.)
- `confidence`: confidence level (high, medium, low) based on source specificity
- `notes`: additional context about the interaction

Contains over 210 documented trophic interactions covering:
- Mammal predation on vertebrates and invertebrates
- Mammal herbivory and frugivory on plants
- Mammal scavenging behavior
- Bird predation and herbivory
- Reptile and amphibian insectivory
- Fish predation on invertebrates and vertebrates
- Invertebrate herbivory on plants
- Invertebrate mutualism (pollination, ant-aphid)
- Invertebrate parasitism (parasitoid wasps)
- Invertebrate predation (spiders, ants)

## Data Sources
All data extracted from:
"Base d'espècies i interaccions tròfiques per a una simulació agent-based al Parc Natural de l'Alt Pirineu"
located in `/home/pepe/proyectos/ecosystem_simulator/biodata/`

## Usage Notes
- Taxonomic groups follow the classification used in the source document
- Body mass estimates are approximateaverages from literature
- Interaction confidence reflects how explicitly the relationship was stated in the source
- For simulation use, consider converting taxonomic names to species IDs
- The trophic matrix can be used to build adjacency matrices or interaction webs
- Seasonal variations in diet are noted in the main_diet field where applicable

## Next Steps for Simulation
1. Link consumer/resource names to species IDs in the simulation engine
2. Assign interaction strengths based on confidence and dietary proportions
3. Implement seasonal diet shifts where documented
4. Use functional clusters (P1-P3, I1-I3, V-herbivors, etc.) for population-level parameters
5. Validate emergent food webs against the documented matrix