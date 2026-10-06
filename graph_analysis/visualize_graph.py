#!/usr/bin/env python3
"""Generate publication-quality trophic network graph visualization."""

import json
import os
import re
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "ecosystem", "data")
GRAPH_FILE = os.path.join(DATA_DIR, "ecosystem_graph_standard.json")
OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "ecosystem", "paper", "trophic_network_graph.png"
)

TAXON_COLORS = {
    "Mammalia": "#2e86ab",
    "Aves": "#a23b72",
    "Reptilia": "#f18f01",
    "Amphibia": "#42bf2e",
    "Actinopterygii": "#22aed1",
    "Cluster_Vertebrat": "#8eb8e5",
    "Cluster_Invertebrat": "#c9a959",
    "Cluster_Planta": "#5cb85c",
    "Plantae": "#5cb85c",
    "Recursos Vegetals": "#95d695",
    "Araneae": "#8b4513",
    "Formicidae": "#8b0000",
    "Aphididae": "#b8860b",
    "Coleoptera": "#b8860b",
    "Diptera": "#b8860b",
    "Ephemeroptera": "#b8860b",
    "Hemiptera": "#b8860b",
    "Lepidoptera": "#b8860b",
    "Orthoptera": "#b8860b",
    "Plecoptera": "#b8860b",
    "Trichoptera": "#b8860b",
    "Thaumetopoea pityocampa": "#b8860b",
    "Boloria eunomia": "#daa520",
    "Bombus spp.": "#daa520",
    "Parnassius mnemosyne": "#daa520",
    "Ichneumonidae_Braconidae": "#8b4513",
    "Nardus stricta": "#2e8b57",
    "Festuca spp.": "#2e8b57",
    "Vaccinium myrtillus": "#6b8e23",
}

TAXON_LABELS = {
    "Mammalia": "Mamífers",
    "Aves": "Ocells",
    "Reptilia": "Rèptils",
    "Amphibia": "Amfibis",
    "Actinopterygii": "Peixos",
    "Cluster_Vertebrat": "Clúster vertebrat",
    "Cluster_Invertebrat": "Clúster invertebrat",
    "Cluster_Planta": "Clúster planta",
    "Plantae": "Plantes",
    "Recursos Vegetals": "Recursos vegetals",
    "Araneae": "Aranyes",
    "Formicidae": "Formigues",
    "Aphididae": "Pugons",
    "Coleoptera": "Coleòpters",
    "Diptera": "Dípters",
    "Ephemeroptera": "Efemeròpters",
    "Hemiptera": "Hemípter",
    "Lepidoptera": "Lepidòpters",
    "Orthoptera": "Ortòpters",
    "Plecoptera": "Plecòpters",
    "Trichoptera": "Tricòpters",
    "Thaumetopoea pityocampa": "Processonària",
    "Boloria eunomia": "Boloria",
    "Bombus spp.": "Bombus",
    "Parnassius mnemosyne": "Mnemòsine",
    "Ichneumonidae_Braconidae": "Parasitoides",
    "Nardus stricta": "Nardus",
    "Festuca spp.": "Festuca",
    "Vaccinium myrtillus": "Vaccinium",
    "V-RapinyairesNocturnesGrans": "Rap. nocturnes grans",
    "V-RapinyairesNocturnesPetites": "Rap. nocturnes petites",
    "V-Passeriformes": "Passeriformes",
    "V-Ratpenats": "Ratpenats",
    "V-MicromamífersPetits": "Micromamífers petits",
    "V-InsectívorsMitjans": "Insectívors mitjans",
    "I1": "Pol·linitzadors",
    "I2": "Fitòfags",
    "I3": "Depredadors/Parasitoides",
    "P1": "Pl. Entomòfiles",
    "P2": "Prod. Independents",
    "P3": "Pastures",
}


def strip_emoji(text):
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"
        "\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff"
        "\U0001f1e0-\U0001f1ff"
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "\U0001f900-\U0001f9ff"
        "\U0001fa00-\U0001fa6f"
        "\U0001fa70-\U0001faff"
        "\U00002600-\U000026ff"
        "\U0000fe00-\U0000fe0f"
        "\U0000200d"
        "\U00002b50"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text).strip()


def shorten_label(label, max_len=25):
    if len(label) <= max_len:
        return label
    return label[: max_len - 1] + "\u2026"


def load_graph(path=GRAPH_FILE):
    with open(path) as f:
        data = json.load(f)
    G = nx.DiGraph()
    for n in data["nodes"]:
        raw_label = n.get("label", n["id"])
        clean_label = strip_emoji(raw_label)
        taxon = n.get("taxon", "")
        G.add_node(
            n["id"],
            label=clean_label,
            raw_label=raw_label,
            taxon=taxon,
            title=n.get("title", ""),
        )
    for e in data["edges"]:
        G.add_edge(
            e["source"],
            e["target"],
            type=e.get("type", "unknown"),
            confidence=e.get("confidence", "unknown"),
        )
    return G, data


def get_taxon_color(taxon):
    return TAXON_COLORS.get(taxon, "#999999")


def get_taxon_label(taxon):
    return TAXON_LABELS.get(taxon, taxon)


def build_taxon_legend_data(G):
    taxon_to_nodes = {}
    for n, ndata in G.nodes(data=True):
        taxon = ndata.get("taxon", "unknown")
        if taxon not in taxon_to_nodes:
            taxon_to_nodes[taxon] = []
        taxon_to_nodes[taxon].append(n)
    legend_items = []
    for taxon in sorted(taxon_to_nodes.keys()):
        color = get_taxon_color(taxon)
        label = get_taxon_label(taxon)
        count = len(taxon_to_nodes[taxon])
        legend_items.append((color, f"{label} ({count})"))
    return legend_items


def visualize():
    G, data = load_graph()
    print(
        f"[OK] Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges"
    )

    pos = nx.kamada_kawai_layout(G, scale=2.5)
    print("[OK] Layout computed (kamada-kawai)")

    fig, ax = plt.subplots(1, 1, figsize=(32, 24), dpi=200)
    fig.patch.set_facecolor("white")

    node_colors = []
    node_sizes = []
    for n, ndata in G.nodes(data=True):
        taxon = ndata.get("taxon", "")
        node_colors.append(get_taxon_color(taxon))
        if taxon in (
            "Cluster_Vertebrat",
            "Cluster_Invertebrat",
            "Cluster_Planta",
            "Recursos Vegetals",
        ):
            node_sizes.append(1800)
        elif taxon in ("I1", "I2", "I3", "P1", "P2", "P3"):
            node_sizes.append(1400)
        elif taxon.startswith("V-"):
            node_sizes.append(1200)
        else:
            node_sizes.append(900)

    nx.draw_networkx_edges(
        G,
        pos,
        ax=ax,
        edge_color="#cccccc",
        arrows=True,
        arrowsize=8,
        arrowstyle="-|>",
        alpha=0.5,
        width=0.6,
        connectionstyle="arc3,rad=0.05",
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors="white",
        linewidths=0.8,
        alpha=0.92,
    )

    labels = {}
    for n, ndata in G.nodes(data=True):
        label = ndata.get("label", n)
        taxon = ndata.get("taxon", "")
        if taxon.startswith("V-"):
            labels[n] = TAXON_LABELS.get(n, shorten_label(label, 22))
        elif taxon in ("Cluster_Invertebrat", "Cluster_Vertebrat", "Cluster_Planta"):
            labels[n] = TAXON_LABELS.get(n, shorten_label(label, 22))
        elif taxon in ("Recursos Vegetals",):
            labels[n] = "Recursos Vegetals"
        elif n in ("I1", "I2", "I3", "P1", "P2", "P3"):
            labels[n] = TAXON_LABELS.get(n, shorten_label(label, 18))
        else:
            labels[n] = shorten_label(label, 22)

    nx.draw_networkx_labels(
        G,
        pos,
        ax=ax,
        labels=labels,
        font_size=4.5,
        font_family="sans-serif",
    )

    legend_items = build_taxon_legend_data(G)
    handles = []
    for color, label in legend_items:
        handles.append(
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=color,
                markersize=10,
                label=label,
            )
        )
    legend = ax.legend(
        handles=handles,
        loc="upper left",
        title="Grups Taxonòmics",
        fontsize=9,
        title_fontsize=11,
        framealpha=0.9,
        edgecolor="#cccccc",
        ncol=2,
    )

    ax.set_title(
        "Xarxa Tròfica del Parc Natural de l'Alt Pirineu",
        fontsize=20,
        fontweight="bold",
        pad=20,
    )
    ax.axis("off")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    plt.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"[OK] Image saved to: {OUTPUT_FILE}")
    plt.close()


if __name__ == "__main__":
    visualize()
