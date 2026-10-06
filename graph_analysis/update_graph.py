#!/usr/bin/env python3
"""Update graph JSONs to add P2 cluster, map herbivores to plant clusters."""

import json
import os

DATA_DIR = "/home/pepe/proyectos/ecosystem_simulator/ecosystem/data"


def update_graph(path):
    with open(path) as f:
        data = json.load(f)

    nodes = {n["id"]: n for n in data["nodes"]}
    edges = []
    for e in data["edges"]:
        # Skip old "Plantae Various" trophic edges that will be replaced
        if (
            e.get("type")
            in ("herbivory", "frugivory", "granivory", "nectarivory", "pollenivory")
            and e["target"] == "Various"
        ):
            # These will be handled by the new trophic matrix entries
            continue
        edges.append(e)

    trophic_additions = [
        # New herbivore → P3 edges (was completely missing)
        ("Rupicapra pyrenaica pyrenaica", "P3", "herbivory", "high"),
        ("Cervus elaphus", "P3", "herbivory", "high"),
        ("Capreolus capreolus", "P3", "herbivory", "high"),
        ("Sus scrofa", "P3", "herbivory", "high"),
        # Replaced Various → Cluster mappings
        ("Martes martes", "P1", "frugivory", "low"),
        ("Vulpes vulpes", "P1", "frugivory", "medium"),
        ("Felis silvestris", "P1", "frugivory", "low"),
        ("Meles meles", "P1", "frugivory", "medium"),
        ("Corvus corax", "P1", "frugivory", "medium"),
        ("V-Passeriformes", "P1", "frugivory", "medium"),
        ("V-InsectívorsMitjans", "P1", "frugivory", "low"),
        ("Boloria eunomia", "P1", "nectarivory", "high"),
        ("Parnassius mnemosyne", "P1", "nectarivory", "high"),
        ("Bombus spp.", "P1", "nectarivory", "high"),
        ("Bombus spp.", "P1", "pollenivory", "high"),
        ("Lagopus muta", "P3", "herbivory", "high"),
        ("Ovis aries musimon", "P3", "herbivory", "high"),
        ("Dama dama", "P3", "herbivory", "high"),
        ("Marmota marmota", "P3", "herbivory", "high"),
        ("Oryctolagus cuniculus", "P3", "herbivory", "high"),
        ("Sciurus vulgaris", "P3", "granivory", "high"),
        ("V-MicromamífersPetits", "P3", "herbivory", "high"),
        ("Orthoptera", "P3", "herbivory", "medium"),
        ("Formicidae", "P3", "granivory", "medium"),
        ("Phoxinus spp.", "P2", "herbivory", "medium"),
    ]

    for src, tgt, typ, conf in trophic_additions:
        edges.append(
            {
                "source": src,
                "target": tgt,
                "type": typ,
                "confidence": conf,
            }
        )

    # Add P2 cluster node if not present
    if "P2" not in nodes:
        nodes["P2"] = {
            "id": "P2",
            "label": "🌿 Productors Independents",
            "taxon": "Cluster_Planta",
            "title": "Productors Independents (P2) — Cluster_Planta",
        }

    # Add representative species for P2
    p2_species = [
        ("Hippuris vulgaris", "Cua de cavall aquàtica", "Plantae"),
        ("Pteridophyta", "Falgueres (Pteridòfits)", "Plantae"),
        ("Bryophyta", "Molses (Briòfits)", "Plantae"),
    ]
    for sid, slabel, staxon in p2_species:
        if sid not in nodes:
            nodes[sid] = {
                "id": sid,
                "label": slabel,
                "taxon": staxon,
                "title": f"{slabel} ({sid}) — Plantae",
            }
        edges.append(
            {
                "source": sid,
                "target": "P2",
                "type": "clustermember",
                "confidence": "high",
            }
        )

    # Rebuild
    data["nodes"] = list(nodes.values())
    data["edges"] = edges
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[OK] Updated {path}: {len(data['nodes'])} nodes, {len(edges)} edges")


update_graph(os.path.join(DATA_DIR, "ecosystem_graph_standard.json"))
update_graph(os.path.join(DATA_DIR, "ecosystem_graph_optimized.json"))
