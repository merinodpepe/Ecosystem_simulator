from dataclasses import dataclass, field


@dataclass(frozen=True)
class TrophicLink:
    consumer: str
    resource: str
    interaction_type: str
    proportion: float = 0.1
    confidence: str = "medium"


@dataclass
class Diet:
    plant_proportion: float = 0.0
    invert_proportion: float = 0.0
    vertebrate_proportion: float = 0.0
    carrion_proportion: float = 0.0
    fish_proportion: float = 0.0

    @property
    def is_valid(self) -> bool:
        total = (
            self.plant_proportion
            + self.invert_proportion
            + self.vertebrate_proportion
            + self.carrion_proportion
            + self.fish_proportion
        )
        return abs(total - 1.0) < 0.01


HERBIVORE_DIETS = {
    "Rupicapra_pyrenaica": Diet(plant_proportion=1.0),
    "Cervus_elaphus": Diet(plant_proportion=1.0),
    "Capreolus_capreolus": Diet(plant_proportion=1.0),
    "Marmota_marmota": Diet(plant_proportion=0.95, invert_proportion=0.05),
    "Oryctolagus_cuniculus": Diet(plant_proportion=1.0),
    "Sciurus_vulgaris": Diet(plant_proportion=0.95, invert_proportion=0.05),
    "Ovis_aries_musimon": Diet(plant_proportion=1.0),
    "Dama_dama": Diet(plant_proportion=1.0),
    "Lagopus_muta": Diet(plant_proportion=0.8, invert_proportion=0.2),
    "Tetrao_urogallus": Diet(plant_proportion=0.7, invert_proportion=0.3),
}

CARNIVORE_DIETS = {
    "Aquila_chrysaetos": Diet(vertebrate_proportion=0.9, carrion_proportion=0.1),
    "Lutra_lutra": Diet(
        fish_proportion=0.8, invert_proportion=0.1, vertebrate_proportion=0.1
    ),
    "Martes_martes": Diet(
        vertebrate_proportion=0.5, invert_proportion=0.3, plant_proportion=0.2
    ),
    "Mustela_erminea": Diet(vertebrate_proportion=0.7, invert_proportion=0.3),
    "Mustela_nivalis": Diet(vertebrate_proportion=0.7, invert_proportion=0.3),
    "Felis_silvestris": Diet(vertebrate_proportion=0.8, invert_proportion=0.2),
}

OMNIVORE_DIETS = {
    "Ursus_arctos": Diet(
        plant_proportion=0.8,
        invert_proportion=0.1,
        vertebrate_proportion=0.05,
        carrion_proportion=0.05,
    ),
    "Sus_scrofa": Diet(
        plant_proportion=0.7,
        invert_proportion=0.2,
        vertebrate_proportion=0.05,
        carrion_proportion=0.05,
    ),
    "Vulpes_vulpes": Diet(
        vertebrate_proportion=0.4,
        invert_proportion=0.3,
        plant_proportion=0.2,
        carrion_proportion=0.1,
    ),
    "Meles_meles": Diet(
        invert_proportion=0.5,
        plant_proportion=0.3,
        vertebrate_proportion=0.15,
        carrion_proportion=0.05,
    ),
    "Corvus_corax": Diet(
        carrion_proportion=0.4,
        invert_proportion=0.3,
        plant_proportion=0.2,
        vertebrate_proportion=0.1,
    ),
    "Gypaetus_barbatus": Diet(carrion_proportion=0.95, vertebrate_proportion=0.05),
}

ALL_DIETS: dict[str, Diet] = {**HERBIVORE_DIETS, **CARNIVORE_DIETS, **OMNIVORE_DIETS}

TROPHIC_LINKS: list[TrophicLink] = [
    TrophicLink("Aquila_chrysaetos", "Rupicapra_pyrenaica", "predation", 0.3, "high"),
    TrophicLink("Aquila_chrysaetos", "Marmota_marmota", "predation", 0.5, "high"),
    TrophicLink("Aquila_chrysaetos", "Lagopus_muta", "predation", 0.1, "medium"),
    TrophicLink("Martes_martes", "Tetrao_urogallus", "predation", 0.3, "high"),
    TrophicLink("Martes_martes", "Sciurus_vulgaris", "predation", 0.3, "medium"),
    TrophicLink("Vulpes_vulpes", "Oryctolagus_cuniculus", "predation", 0.3, "high"),
    TrophicLink("Vulpes_vulpes", "Tetrao_urogallus", "predation", 0.1, "medium"),
    TrophicLink("Vulpes_vulpes", "Lagopus_muta", "predation", 0.1, "medium"),
    TrophicLink("Gypaetus_barbatus", "Rupicapra_pyrenaica", "scavenging", 0.4, "high"),
    TrophicLink("Gypaetus_barbatus", "Cervus_elaphus", "scavenging", 0.3, "high"),
    TrophicLink("Lutra_lutra", "Salmo_trutta", "predation", 0.6, "high"),
    TrophicLink("Mustela_erminea", "Lagopus_muta", "predation", 0.2, "medium"),
    TrophicLink("Mustela_nivalis", "Oryctolagus_cuniculus", "predation", 0.2, "medium"),
    TrophicLink(
        "Felis_silvestris", "Oryctolagus_cuniculus", "predation", 0.3, "medium"
    ),
    TrophicLink("Felis_silvestris", "Tetrao_urogallus", "predation", 0.1, "medium"),
]


def get_diet(species_key: str) -> Diet | None:
    return ALL_DIETS.get(species_key)


def get_predators(species_key: str) -> list[str]:
    return [link.consumer for link in TROPHIC_LINKS if link.resource == species_key]


def get_prey(species_key: str) -> list[str]:
    return [link.resource for link in TROPHIC_LINKS if link.consumer == species_key]
