#!/usr/bin/env python3
"""
Graph analysis for Alt Pirineu ecosystem trophic network.
Computes: subgraphs, centrality, communities, trophic chains.
"""

import json
import sys
import os
from collections import defaultdict

import networkx as nx
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "ecosystem", "data")
GRAPH_FILE = os.path.join(DATA_DIR, "ecosystem_graph_standard.json")

V_CLUSTERS = [
    "V-Passeriformes",
    "V-Ratpenats",
    "V-RapinyairesNocturnesGrans",
    "V-RapinyairesNocturnesPetites",
    "V-MicromamífersPetits",
    "V-InsectívorsMitjans",
]

V_CLUSTER_LABELS = {
    "V-Passeriformes": "Passeriformes (ocells insectívors)",
    "V-Ratpenats": "Ratpenats (quiròpters)",
    "V-RapinyairesNocturnesGrans": "Rapinyaires nocturnes grans",
    "V-RapinyairesNocturnesPetites": "Rapinyaires nocturnes petites",
    "V-MicromamífersPetits": "Micromamífers petits",
    "V-InsectívorsMitjans": "Insectívors mitjans",
}

CLUSTER_COLORS = {
    "V-Passeriformes": "#e41a1c",
    "V-Ratpenats": "#377eb8",
    "V-RapinyairesNocturnesGrans": "#4daf4a",
    "V-RapinyairesNocturnesPetites": "#984ea3",
    "V-MicromamífersPetits": "#ff7f00",
    "V-InsectívorsMitjans": "#ffff33",
}


def load_graph(path=GRAPH_FILE):
    with open(path) as f:
        data = json.load(f)
    G = nx.DiGraph()
    for n in data["nodes"]:
        G.add_node(n["id"], label=n.get("label", n["id"]), taxon=n.get("taxon", ""))
    for e in data["edges"]:
        G.add_edge(
            e["source"],
            e["target"],
            type=e.get("type", "unknown"),
            confidence=e.get("confidence", "unknown"),
        )
    return G, data


def strip_clustermember_edges(G):
    """Return a copy of G without clustermember edges."""
    H = G.copy()
    edges_to_remove = [
        (u, v) for u, v, d in H.edges(data=True) if d.get("type") == "clustermember"
    ]
    H.remove_edges_from(edges_to_remove)
    return H


def subgraph_around(G, node, radius=1):
    """Extract subgraph centered on a node within given radius."""
    nodes = {node}
    current = {node}
    for _ in range(radius):
        neighbors = set()
        for n in current:
            neighbors |= set(G.predecessors(n)) | set(G.successors(n))
        current = neighbors - nodes
        nodes |= current
    return G.subgraph(nodes).copy()


def cluster_subgraph_report(G_raw, cluster_id):
    """Generate a detailed report of what interacts with a V-cluster."""
    G_no_member = strip_clustermember_edges(G_raw)
    sg = subgraph_around(G_no_member, cluster_id, radius=1)

    preds = list(sg.predecessors(cluster_id))
    succs = list(sg.successors(cluster_id))

    lines = []
    lines.append(f"## Subgraf del clúster: {cluster_id}")
    lines.append(f"**{V_CLUSTER_LABELS.get(cluster_id, cluster_id)}**")
    lines.append("")
    lines.append(f"- **Nodes totals al subgraf (radi 1):** {sg.number_of_nodes()}")
    lines.append(f"- **Arestes al subgraf:** {sg.number_of_edges()}")
    lines.append("")

    lines.append("### Depredadors (qui el consumeix)")
    if preds:
        for p in preds:
            label = G_raw.nodes[p].get("label", p)
            edges_data = sg[p][cluster_id]
            types = [
                d.get("type", "")
                for d in (edges_data if isinstance(edges_data, list) else [edges_data])
            ]
            confs = [
                d.get("confidence", "")
                for d in (edges_data if isinstance(edges_data, list) else [edges_data])
            ]
            detail = ", ".join(f"{t} ({c})" for t, c in zip(types, confs))
            tax = G_raw.nodes[p].get("taxon", "")
            lines.append(f"  - **{label}** ({p}) [{tax}] — {detail}")
    else:
        lines.append("  - Cap depredador directe")

    lines.append("")
    lines.append("### Preses (a qui consumeix)")
    if succs:
        for s in succs:
            label = G_raw.nodes[s].get("label", s)
            edges_data = sg[cluster_id][s]
            types = [
                d.get("type", "")
                for d in (edges_data if isinstance(edges_data, list) else [edges_data])
            ]
            confs = [
                d.get("confidence", "")
                for d in (edges_data if isinstance(edges_data, list) else [edges_data])
            ]
            detail = ", ".join(f"{t} ({c})" for t, c in zip(types, confs))
            tax = G_raw.nodes[s].get("taxon", "")
            lines.append(f"  - **{label}** ({s}) [{tax}] — {detail}")
    else:
        lines.append("  - Cap presa directa")

    lines.append("")
    return "\n".join(lines), sg


def centrality_analysis(G_raw):
    """Compute centrality measures for all non-clustermember nodes."""
    G = strip_clustermember_edges(G_raw)

    dc = nx.degree_centrality(G)
    try:
        bc = nx.betweenness_centrality(G, weight=None)
    except Exception:
        bc = nx.betweenness_centrality(G.to_undirected(), weight=None)
    try:
        ec = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-06)
    except Exception:
        ec = nx.eigenvector_centrality(G.to_undirected(), max_iter=1000, tol=1e-06)

    # Combine scores
    results = []
    for node in G.nodes():
        results.append(
            {
                "node": node,
                "label": G_raw.nodes[node].get("label", node),
                "taxon": G_raw.nodes[node].get("taxon", ""),
                "degree_centrality": round(dc.get(node, 0), 5),
                "betweenness_centrality": round(bc.get(node, 0), 5),
                "eigenvector_centrality": round(ec.get(node, 0), 5),
            }
        )

    results.sort(key=lambda x: x["betweenness_centrality"], reverse=True)

    lines = []
    lines.append("## Anàlisi de Centralitat")
    lines.append("")
    lines.append(
        "Nodes ordenats per betweenness centrality (nodes amb més influència com a ponts tròfics):"
    )
    lines.append("")
    lines.append(
        "| Rang | Node | Label | Taxon | Degree Centrality | Betweenness Centrality | Eigenvector Centrality |"
    )
    lines.append(
        "|------|------|-------|-------|------------------|------------------------|------------------------|"
    )
    for i, r in enumerate(results[:30], 1):
        lines.append(
            f"| {i} | {r['node']} | {r['label']} | {r['taxon']} | {r['degree_centrality']} | {r['betweenness_centrality']} | {r['eigenvector_centrality']} |"
        )

    lines.append("")
    return "\n".join(lines), results


def community_detection(G_raw):
    """Detect trophic communities using Girvan-Newman (edge betweenness)."""
    G = strip_clustermember_edges(G_raw).to_undirected()

    lines = []
    lines.append("## Detecció de Comunitats Tròfiques")
    lines.append("")

    try:
        comp = nx.community.girvan_newman(G)
        top_communities = list(next(comp))
        lines.append(f"Algorisme: Girvan-Newman (edge betweenness)")
        lines.append(f"Nombre de comunitats detectades: {len(top_communities)}")
        lines.append("")
        for i, comm in enumerate(sorted(top_communities, key=len, reverse=True), 1):
            members = []
            for n in sorted(comm):
                label = G_raw.nodes[n].get("label", n)
                tax = G_raw.nodes[n].get("taxon", "")
                members.append(f"{label} ({n}) [{tax}]")
            lines.append(f"### Comunitat {i} ({len(comm)} nodes)")
            for m in members:
                lines.append(f"  - {m}")
            lines.append("")
    except Exception as e:
        lines.append(f"No s'ha pogut completar la detecció de comunitats: {e}")
        lines.append("")

    return "\n".join(lines), top_communities if "top_communities" in dir() else []


def trophic_chains_through_clusters(G_raw):
    """Build 3-step trophic chains passing through each V-cluster."""
    G = strip_clustermember_edges(G_raw)
    lines = []
    lines.append("## Cadenes Tròfiques a través dels Clústers Vertebrats")
    lines.append("")

    for cid in V_CLUSTERS:
        if cid not in G:
            continue
        lines.append(f"### {cid} — {V_CLUSTER_LABELS.get(cid, cid)}")
        lines.append("")
        preds = list(G.predecessors(cid))
        succs = list(G.successors(cid))

        if not preds:
            lines.append(
                "  _No té depredadors directes (depredador apical o base de cadena)_"
            )
        if not succs:
            lines.append("  _No té preses directes (productor o recurs base)_")

        # Build chains: predator -> cluster -> prey
        chains = []
        for p in preds[:5]:
            for s in succs[:5]:
                p_label = G_raw.nodes[p].get("label", p)
                s_label = G_raw.nodes[s].get("label", s)
                chains.append(
                    f"  {p_label} ({p}) → {V_CLUSTER_LABELS.get(cid, cid)} → {s_label} ({s})"
                )

        if chains:
            lines.append(
                "Cadenes tròfiques representatives (depredador → clúster → presa):"
            )
            lines.append("")
            for c in chains[:10]:
                lines.append(f"  - {c}")
        lines.append("")

        # Extended chains: predator_of_predator -> predator -> cluster -> prey -> prey_of_prey
        lines.append("Cadenes esteses (5 nivells):")
        lines.append("")
        extended = []
        for p in preds[:3]:
            pp = list(G.predecessors(p))[:2]
            for s in succs[:3]:
                ss = list(G.successors(s))[:2]
                chain_parts = []
                for pp_node in pp:
                    chain_parts.append(
                        f"{G_raw.nodes[pp_node].get('label', pp_node)} ({pp_node})"
                    )
                if chain_parts:
                    chain_parts.append("→")
                chain_parts.append(f"{G_raw.nodes[p].get('label', p)} ({p})")
                chain_parts.append("→")
                chain_parts.append(f"{V_CLUSTER_LABELS.get(cid, cid)}")
                chain_parts.append("→")
                chain_parts.append(f"{G_raw.nodes[s].get('label', s)} ({s})")
                for ss_node in ss:
                    chain_parts.append("→")
                    chain_parts.append(
                        f"{G_raw.nodes[ss_node].get('label', ss_node)} ({ss_node})"
                    )
                extended.append(" ".join(chain_parts))

        for c in extended[:8]:
            lines.append(f"  - {c}")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def summary_statistics(G_raw, centrality_results):
    """Generate ecosystem-level summary."""
    G_no_member = strip_clustermember_edges(G_raw)
    G_undirected = G_no_member.to_undirected()

    lines = []
    lines.append("# Anàlisi de Xarxa Tròfica — Parc Natural de l'Alt Pirineu")
    lines.append("")
    lines.append("## Estadístiques Globals")
    lines.append("")
    lines.append(f"| Mètrica | Valor |")
    lines.append(f"|---------|-------|")
    lines.append(f"| Nodes totals (incl. clústers) | {G_raw.number_of_nodes()} |")
    lines.append(f"| Arestes totals | {G_raw.number_of_edges()} |")
    lines.append(f"| Nodes (sense clustermember) | {G_no_member.number_of_nodes()} |")
    lines.append(f"| Arestes (sense clustermember) | {G_no_member.number_of_edges()} |")
    lines.append(f"| Densitat del graf | {nx.density(G_no_member):.4f} |")
    lines.append(
        f"| Nombre de components connectats | {nx.number_weakly_connected_components(G_no_member)} |"
    )
    lines.append(
        f"| Coeficient d'agrupament (mitjà) | {nx.average_clustering(G_undirected):.4f} |"
    )
    lines.append(
        f"| Diàmetre (component gegant) | {nx.diameter(G_undirected) if nx.is_connected(G_undirected) else 'N/A (no connectat)'} |"
    )

    # Degree distribution
    degrees = [d for _, d in G_no_member.out_degree()]
    in_degrees = [d for _, d in G_no_member.in_degree()]
    lines.append(f"| Grau de sortida (out-degree) mitjà | {np.mean(degrees):.2f} |")
    lines.append(f"| Grau d'entrada (in-degree) mitjà | {np.mean(in_degrees):.2f} |")
    lines.append(f"| Grau màxim de sortida | {max(degrees)} |")
    lines.append(f"| Grau màxim d'entrada | {max(in_degrees)} |")
    lines.append("")

    # Top keystone by betweenness
    lines.append("## Espècies clau (Keystone) — Top 10 per Betweenness Centrality")
    lines.append("")
    lines.append(
        "La betweenness centrality mesura quantes rutes tròfiques passen per un node, identificant espècies pont crítiques per al flux d'energia:"
    )
    lines.append("")
    for r in centrality_results[:10]:
        lines.append(
            f"1. **{r['label']}** ({r['node']}) [{r['taxon']}] — B={r['betweenness_centrality']}, D={r['degree_centrality']}, E={r['eigenvector_centrality']}"
        )
    lines.append("")

    # V-cluster positions in centrality rankings
    lines.append("## Posició dels Clústers Vertebrats en el Rànquing de Centralitat")
    lines.append("")
    for r in centrality_results:
        if r["node"] in V_CLUSTERS:
            rank = centrality_results.index(r) + 1
            lines.append(
                f"- **{r['label']}** ({r['node']}) — Rang #{rank} en betweenness, B={r['betweenness_centrality']}"
            )
    lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("  ANÀLISI DE XARXA TRÒFICA — PNAP")
    print("=" * 70)
    print()

    G_raw, data = load_graph()
    print(
        f"[OK] Graf carregat: {G_raw.number_of_nodes()} nodes, {G_raw.number_of_edges()} arestes"
    )
    print()

    # --- Summary stats ---
    print("[*] Calculant estadístiques globals...")
    summary_text, centrality_results = centrality_analysis(G_raw)
    stats_text = summary_statistics(G_raw, centrality_results)

    # --- Subgraph per cluster ---
    print("[*] Extraient subgrafs per clúster...")
    all_subgraph_reports = []
    all_subgraphs = {}
    for cid in V_CLUSTERS:
        report, sg = cluster_subgraph_report(G_raw, cid)
        all_subgraph_reports.append(report)
        all_subgraphs[cid] = sg
        print(f"    {cid}: {sg.number_of_nodes()} nodes, {sg.number_of_edges()} edges")

    # --- Community detection ---
    print("[*] Detectant comunitats tròfiques...")
    community_text, communities = community_detection(G_raw)

    # --- Trophic chains ---
    print("[*] Construint cadenes tròfiques...")
    chains_text = trophic_chains_through_clusters(G_raw)

    # --- Combine full report ---
    full = []
    full.append(stats_text)
    full.append(summary_text)
    full.append(community_text)
    full.append(chains_text)
    full.append("## Subgrafs dels Clústers Vertebrats")
    full.append("")
    full.extend(all_subgraph_reports)

    report = "\n".join(full)

    # Write report
    out_path = os.path.join(os.path.dirname(__file__), "graph_analysis_report.md")
    with open(out_path, "w") as f:
        f.write(report)
    print(f"\n[OK] Report escrit a: {out_path}")
    print()

    # Print V-cluster centrality for quick reference
    print("=" * 70)
    print("  CENTRALITAT DELS CLÚSTERS VERTEBRATS (resum ràpid)")
    print("=" * 70)
    for r in centrality_results:
        if r["node"] in V_CLUSTERS:
            rank = centrality_results.index(r) + 1
            print(f"  Rang #{rank}: {r['label']} — B={r['betweenness_centrality']}")
    print()


if __name__ == "__main__":
    main()
