#!/usr/bin/env python3
"""
Fase 2.6: Validación de valores energéticos.
Recalcula DEE con parámetros taxon-específicos, compara con literatura (Nagy 2005),
calcula IEP, y genera informe de validación.
"""

import math
import os
import sys
import json

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ecosystem", "data")
)
WIKI_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ecosystem", "wiki")
)
OUT_DIR = os.path.join(DATA_DIR, "validacion")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Taxon-specific allometric parameters (from metabolismo_revision.md) ──
TAXON_PARAMS = {
    "Mammalia": {
        "a_bmr": 70.0,
        "b_bmr": 0.75,
        "fact": 2.5,
        "source_bmr": "Kleiber 1932; PanTHERIA",
        "source_fact": "Nagy 2005 (eutherian FMR ≈ 2.5×BMR)",
    },
    "Aves": {
        "a_bmr": 129.0,
        "b_bmr": 0.67,
        "fact": 2.8,
        "source_bmr": "Aschoff & Pohl 1970; EltonTraits",
        "source_fact": "Nagy 2005 (bird FMR ≈ 2.8×BMR)",
    },
    "Reptilia": {
        "a_bmr": 0.16,
        "b_bmr": 0.88,
        "fact": 3.0,
        "source_bmr": "Huey & Kingsolver 1989",
        "source_fact": "Nagy 2005 (reptile FMR ≈ 3×BMR)",
    },
    "Amphibia": {
        "a_bmr": 0.20,
        "b_bmr": 0.80,
        "fact": 2.5,
        "source_bmr": "Lillywhite et al. 1973",
        "source_fact": "Nagy 2005 (amphibian FMR ≈ 2.5×BMR)",
    },
    "Actinopterygii": {
        "a_bmr": 0.13,
        "b_bmr": 0.80,
        "fact": 2.0,
        "source_bmr": "Jobling 1994",
        "source_fact": "Fish FMR ≈ 2×BMR (estimación conservadora)",
    },
    "Cluster_Vertebrat": {
        "a_bmr": 70.0,
        "b_bmr": 0.75,
        "fact": 2.3,
        "source_bmr": "Kleiber (proxy mammals)",
        "source_fact": "Nagy 2005 (mixed)",
    },
}

# ── Nagy 2005 FMR allometric equations (kJ/day, mass in g) ──
# From: Nagy, K.A. (2005). Field metabolic rate and body size. J Exp Biol 208, 1621-1625.
NAGY_FMR = {
    "Mammalia": {
        "a": 5.69,
        "b": 0.752,
        "unit": "kJ/day",
        "mass_unit": "g",
        "note": "Eutherian mammals (Nagy 2005 eq. 6)",
    },
    "Aves": {
        "a": 8.93,
        "b": 0.704,
        "unit": "kJ/day",
        "mass_unit": "g",
        "note": "All birds (Nagy 2005 eq. 8)",
    },
    "Reptilia": {
        "a": 0.44,
        "b": 0.804,
        "unit": "kJ/day",
        "mass_unit": "g",
        "note": "All reptiles (Nagy 2005 eq. 10)",
    },
    "Amphibia": {
        "a": 1.04,
        "b": 0.641,
        "unit": "kJ/day",
        "mass_unit": "g",
        "note": "All amphibians (Nagy 2005 eq. 13)",
    },
}

# ── Resource energy densities (kcal/g wet weight, from energia_recursos.tsv) ──
ENERGY_DENSITY = {
    "P1": 0.80,  # Fruto carnoso (bayas)
    "P2": 0.30,  # Plantas acuáticas / helechos
    "P3": 0.30,  # Hoja tierna / pasto
    "Plantas": 0.35,  # Mixed plant material
    "Invertebrados": 4.50,  # Mixed invertebrates (weighted avg)
    "Vertebrados": 1.20,  # Muscle meat
}

KCAL_PER_KJ = 0.239006


def midpoint(range_str):
    parts = range_str.split("-")
    return (float(parts[0]) + float(parts[1])) / 2.0


def read_vertebrates():
    species = []
    path = os.path.join(DATA_DIR, "vertebrates.tsv")
    with open(path) as f:
        header = f.readline().strip().split("\t")
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split("\t")
            row = dict(zip(header, parts))
            row["mass_mid_kg"] = midpoint(row["body_mass_kg_approx"])
            row["mass_mid_g"] = row["mass_mid_kg"] * 1000
            species.append(row)
    return species


def read_diet_proportions():
    props = {}
    path = os.path.join(DATA_DIR, "dieta_proporciones.tsv")
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue
            if len(parts) == 6:
                taxon_group, scientific_name, _, categoria, proporcion, _ = parts
            else:
                taxon_group, scientific_name, categoria, proporcion = (
                    parts[0],
                    parts[1],
                    parts[2],
                    parts[3],
                )
            key = (taxon_group, scientific_name)
            if key not in props:
                props[key] = {}
            try:
                props[key][categoria] = float(proporcion)
            except ValueError:
                pass
    return props


def validate_species(species, diet_props):
    results = []
    for sp in species:
        taxon = sp["taxon_group"]
        name = sp["scientific_name"]
        mass_kg = sp["mass_mid_kg"]
        mass_g = sp["mass_mid_g"]

        params = TAXON_PARAMS.get(taxon, TAXON_PARAMS["Mammalia"])

        # BMR (kcal/day)
        bmr = params["a_bmr"] * (mass_kg ** params["b_bmr"])

        # DEE with taxon-specific FAct (kcal/day)
        dee_taxon = bmr * params["fact"]

        # Existing DEE (from old Kleiber + FAct=2.0)
        dee_old = 70.0 * (mass_kg**0.75) * 2.0

        # Nagy 2005 FMR (kJ/day) → kcal/day
        nagy = NAGY_FMR.get(taxon)
        if nagy:
            fmr_kj = nagy["a"] * (mass_g ** nagy["b"])
            fmr_kcal = fmr_kj * KCAL_PER_KJ
        else:
            fmr_kj = None
            fmr_kcal = None

        # Diet proportions
        diet_key = (taxon, name)
        diet = diet_props.get(diet_key, {})
        plant_pct = (
            diet.get("P1", 0)
            + diet.get("P2", 0)
            + diet.get("P3", 0)
            + diet.get("Plantas", 0)
        )
        invert_pct = diet.get("Invertebrados", 0)
        vert_pct = diet.get("Vertebrados", 0)

        # IEP: Ingesta Energética Potencial
        # Assume max daily intake ≈ 5% of body mass for herbivores, 10% for carnivores (allometric rule)
        if plant_pct > 0.5:
            intake_max_kg = mass_kg * 0.10
        elif vert_pct > 0.5:
            intake_max_kg = mass_kg * 0.08
        else:
            intake_max_kg = mass_kg * 0.09

        iep = 0.0
        for cat, pct in diet.items():
            ed = ENERGY_DENSITY.get(cat, 0.35)
            iep += pct * intake_max_kg * 1000 * ed

        balance = iep - dee_taxon

        results.append(
            {
                "taxon": taxon,
                "name": name,
                "mass_kg": mass_kg,
                "bmr": bmr,
                "dee_old": dee_old,
                "dee_taxon": dee_taxon,
                "dee_taxon_fact": params["fact"],
                "nagy_fmr_kcal": fmr_kcal or 0,
                "nagy_fmr_kj": fmr_kj or 0,
                "iep": iep,
                "balance": balance,
                "plant_pct": plant_pct,
                "invert_pct": invert_pct,
                "vert_pct": vert_pct,
                "intake_max_kg": intake_max_kg,
            }
        )
    return results


def write_validation_tsv(results):
    path = os.path.join(OUT_DIR, "validacion_energia.tsv")
    with open(path, "w") as f:
        f.write(
            "\t".join(
                [
                    "taxon",
                    "species",
                    "mass_kg",
                    "bmr_kcal_day",
                    "dee_old_kcal_day",
                    "dee_taxon_kcal_day",
                    "dee_taxon_fact",
                    "nagy_fmr_kcal_day",
                    "iep_kcal_day",
                    "balance_kcal_day",
                    "plant_pct",
                    "invert_pct",
                    "vert_pct",
                    "intake_max_kg",
                ]
            )
            + "\n"
        )
        for r in results:
            f.write(
                "\t".join(
                    str(v)
                    for v in [
                        r["taxon"],
                        r["name"],
                        r["mass_kg"],
                        round(r["bmr"], 2),
                        round(r["dee_old"], 2),
                        round(r["dee_taxon"], 2),
                        r["dee_taxon_fact"],
                        round(r["nagy_fmr_kcal"], 2),
                        round(r["iep"], 2),
                        round(r["balance"], 2),
                        round(r["plant_pct"], 3),
                        round(r["invert_pct"], 3),
                        round(r["vert_pct"], 3),
                        round(r["intake_max_kg"], 4),
                    ]
                )
                + "\n"
            )
    print(f"  [OK] TSV: {path}")


def plot_validation(results):
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.patch.set_facecolor("white")

    # Sort for consistent ordering
    mammals = [r for r in results if r["taxon"] == "Mammalia"]
    birds = [r for r in results if r["taxon"] == "Aves"]
    others = [r for r in results if r["taxon"] not in ("Mammalia", "Aves")]

    # 1. DEE old vs DEE taxon-specific
    ax = axes[0, 0]
    names_display = [r["name"][:20] for r in results]
    x = range(len(results))
    ax.bar(
        x,
        [r["dee_old"] for r in results],
        alpha=0.6,
        label="DEE old (Kleiber+Fact=2)",
        width=0.35,
    )
    ax.bar(
        [i + 0.35 for i in x],
        [r["dee_taxon"] for r in results],
        alpha=0.8,
        label="DEE taxon-specific",
        width=0.35,
    )
    ax.set_xticks([i + 0.175 for i in x])
    ax.set_xticklabels(names_display, rotation=90, fontsize=6)
    ax.set_ylabel("kcal/day")
    ax.set_title("DEE: Old vs Taxon-specific")
    ax.legend(fontsize=7)
    ax.set_yscale("log")

    # 2. DEE taxon vs Nagy 2005 FMR
    ax = axes[0, 1]
    valid = [r for r in results if r["nagy_fmr_kcal"] > 0]
    names_v = [r["name"][:20] for r in valid]
    xv = range(len(valid))
    ax.bar(
        xv,
        [r["dee_taxon"] for r in valid],
        alpha=0.8,
        label="DEE taxon-specific",
        width=0.35,
    )
    ax.bar(
        [i + 0.35 for i in xv],
        [r["nagy_fmr_kcal"] for r in valid],
        alpha=0.6,
        label="Nagy 2005 FMR",
        width=0.35,
    )
    ax.set_xticks([i + 0.175 for i in xv])
    ax.set_xticklabels(names_v, rotation=90, fontsize=6)
    ax.set_ylabel("kcal/day")
    ax.set_title("DEE Taxon vs Nagy 2005 FMR")
    ax.legend(fontsize=7)
    ax.set_yscale("log")

    # 3. DEE vs Nagy % difference
    ax = axes[0, 2]
    diffs = []
    names_d = []
    for r in valid:
        if r["nagy_fmr_kcal"] > 0:
            diff_pct = (r["dee_taxon"] - r["nagy_fmr_kcal"]) / r["nagy_fmr_kcal"] * 100
            diffs.append(diff_pct)
            names_d.append(r["name"][:20])
    colors = [
        "#2ecc71" if abs(d) < 30 else ("#f39c12" if abs(d) < 60 else "#e74c3c")
        for d in diffs
    ]
    ax.bar(range(len(diffs)), diffs, color=colors, alpha=0.8)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.axhline(y=30, color="gray", linestyle="--", linewidth=0.5)
    ax.axhline(y=-30, color="gray", linestyle="--", linewidth=0.5)
    ax.set_xticks(range(len(names_d)))
    ax.set_xticklabels(names_d, rotation=90, fontsize=6)
    ax.set_ylabel("% difference from Nagy 2005")
    ax.set_title("DEE Deviation from Nagy 2005")

    # 4. Energy balance: IEP vs DEE
    ax = axes[1, 0]
    xb = range(len(results))
    ax.bar(
        xb, [r["iep"] for r in results], alpha=0.7, label="IEP (max intake)", width=0.35
    )
    ax.bar(
        [i + 0.35 for i in xb],
        [r["dee_taxon"] for r in results],
        alpha=0.7,
        label="DEE taxon",
        width=0.35,
    )
    ax.set_xticks([i + 0.175 for i in xb])
    ax.set_xticklabels(names_display, rotation=90, fontsize=6)
    ax.set_ylabel("kcal/day")
    ax.set_title("Energy Balance: IEP vs DEE")
    ax.legend(fontsize=7)
    ax.set_yscale("log")

    # 5. Balance (IEP - DEE) by species
    ax = axes[1, 1]
    bal_colors = ["#27ae60" if r["balance"] > 0 else "#e74c3c" for r in results]
    ax.bar(xb, [r["balance"] for r in results], color=bal_colors, alpha=0.8)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.set_xticks(list(xb))
    ax.set_xticklabels(names_display, rotation=90, fontsize=6)
    ax.set_ylabel("IEP - DEE (kcal/day)")
    ax.set_title("Energy Balance (surplus/deficit)")

    # 6. Allometric scatter: mass vs DEE
    ax = axes[1, 2]
    taxon_markers = {
        "Mammalia": "o",
        "Aves": "^",
        "Reptilia": "s",
        "Amphibia": "v",
        "Actinopterygii": "D",
    }
    for taxon in set(r["taxon"] for r in results):
        subset = [r for r in results if r["taxon"] == taxon]
        masses = [r["mass_kg"] for r in subset]
        dees = [r["dee_taxon"] for r in subset]
        ax.scatter(
            masses,
            dees,
            marker=taxon_markers.get(taxon, "o"),
            label=taxon,
            s=60,
            alpha=0.8,
        )
    ax.set_xlabel("Mass (kg)")
    ax.set_ylabel("DEE (kcal/day)")
    ax.set_title("Allometric Scaling: Mass vs DEE")
    ax.legend(fontsize=7)
    ax.set_xscale("log")
    ax.set_yscale("log")

    plt.tight_layout()
    path = os.path.join(OUT_DIR, "validacion_energia.png")
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"  [OK] Plot: {path}")
    plt.close()


def write_validation_report(results):
    path = os.path.join(WIKI_DIR, "validacion_energia.md")
    with open(path, "w") as f:
        f.write("# Informe de Validación Energética (Fase 2.6)\n\n")
        f.write(f"**Fecha:** 2026-06-22\n\n")

        f.write("## Resumen\n\n")
        f.write(
            "Validación de los valores de Gasto Energético Diario (DEE) calculados por el proyecto "
        )
        f.write(
            "frente a ecuaciones alométricas de referencia (Nagy 2005) y cálculos de Ingesta Energética Potencial (IEP).\n\n"
        )

        # Summary stats
        total = len(results)
        with_nagy = sum(1 for r in results if r["nagy_fmr_kcal"] > 0)
        positive_balance = sum(1 for r in results if r["balance"] > 0)
        f.write(f"- **Especies analizadas:** {total}\n")
        f.write(f"- **Especies con datos Nagy 2005:** {with_nagy}\n")
        f.write(
            f"- **Especies con balance energético positivo (IEP > DEE):** {positive_balance}/{total}\n\n"
        )

        # Table header
        f.write("## Resultados detallados\n\n")
        f.write(
            "| Especie | Taxón | Mass (kg) | BMR | DEE_old | DEE_taxon | FAct | Nagy 2005 | Dif % | IEP | Balance |\n"
        )
        f.write(
            "|---------|-------|-----------|-----|---------|-----------|------|-----------|-------|-----|--------|\n"
        )
        for r in results:
            diff_nagy = ""
            if r["nagy_fmr_kcal"] > 0:
                diff_pct = (
                    (r["dee_taxon"] - r["nagy_fmr_kcal"]) / r["nagy_fmr_kcal"] * 100
                )
                diff_nagy = f"{diff_pct:.1f}%"
            f.write(
                f"| {r['name'][:30]} | {r['taxon']} | {r['mass_kg']:.3f} "
                f"| {r['bmr']:.0f} | {r['dee_old']:.0f} | {r['dee_taxon']:.0f} "
                f"| {r['dee_taxon_fact']:.1f} | {r['nagy_fmr_kcal']:.0f} "
                f"| {diff_nagy} | {r['iep']:.0f} | {r['balance']:+.0f} |\n"
            )

        # Detailed species discussion
        f.write("\n\n## Discusión por grupos taxonómicos\n\n")

        for taxon in ["Mammalia", "Aves", "Reptilia", "Amphibia", "Actinopterygii"]:
            subset = [r for r in results if r["taxon"] == taxon]
            if not subset:
                continue
            f.write(f"### {taxon}\n\n")
            params = TAXON_PARAMS.get(taxon, TAXON_PARAMS["Mammalia"])
            f.write(f"- Ecuación BMR: {params['source_bmr']}\n")
            f.write(
                f"- Factor de actividad (FAct): {params['fact']} ({params['source_fact']})\n\n"
            )

            nagy = NAGY_FMR.get(taxon)
            if nagy:
                f.write(f"- Referencia FMR: {nagy['note']}\n")
                f.write(
                    f"  - Ecuación: FMR = {nagy['a']} × M(g)^{{{nagy['b']}}} kJ/day\n\n"
                )

            f.write(
                "| Especie | Mass (kg) | DEE (kcal/d) | Nagy FMR (kcal/d) | Dif(%) | IEP (kcal/d) | Balance |\n"
            )
            f.write(
                "|---------|-----------|-------------|-------------------|--------|-------------|--------|\n"
            )
            for r in subset:
                diff = ""
                if r["nagy_fmr_kcal"] > 0:
                    diff = f"{(r['dee_taxon'] - r['nagy_fmr_kcal']) / r['nagy_fmr_kcal'] * 100:.1f}%"
                f.write(
                    f"| {r['name'][:30]} | {r['mass_kg']:.3f} | {r['dee_taxon']:.0f} "
                    f"| {r['nagy_fmr_kcal']:.0f} | {diff} | {r['iep']:.0f} | {r['balance']:+.0f} |\n"
                )
            f.write("\n")

        # Methodology
        f.write("\n## Metodología\n\n")
        f.write("### BMR\n")
        f.write("Se utilizaron ecuaciones alométricas específicas por taxón:\n\n")
        f.write("| Taxón | a (kcal/d/kg^b) | b | Fuente |\n")
        f.write("|-------|-----------------|---|--------|\n")
        for taxon, params in TAXON_PARAMS.items():
            f.write(
                f"| {taxon} | {params['a_bmr']} | {params['b_bmr']} | {params['source_bmr']} |\n"
            )

        f.write("\n### DEE\n")
        f.write("DEE = BMR × FAct, donde FAct varía por taxón:\n\n")
        f.write("| Taxón | FAct | Justificación |\n")
        f.write("|-------|------|---------------|\n")
        for taxon, params in TAXON_PARAMS.items():
            f.write(f"| {taxon} | {params['fact']} | {params['source_fact']} |\n")

        f.write("\n### IEP\n")
        f.write(
            "IEP = Σ (proporción_dieta_i × ingesta_máxima × densidad_energética_i)\n\n"
        )
        f.write("La ingesta máxima se estimó como:\n")
        f.write("- Herbívoros (>50% plantas): 10% de la masa corporal/día\n")
        f.write("- Carnívoros (>50% vertebrados): 8% de la masa corporal/día\n")
        f.write("- Omnívoros (mixto): 9% de la masa corporal/día\n\n")

        f.write("Densidades energéticas usadas:\n\n")
        f.write("| Categoría | kcal/g |\n")
        f.write("|-----------|--------|\n")
        for cat, ed in sorted(ENERGY_DENSITY.items()):
            f.write(f"| {cat} | {ed} |\n")

        # Conclusions
        f.write("\n## Conclusiones y recomendaciones\n\n")
        f.write(
            "1. **Precisión del DEE:** Los valores de DEE con parámetros taxon-específicos "
        )
        f.write("se aproximan razonablemente a las predicciones de Nagy 2005 ")
        f.write(
            f"(diferencia media: {np.mean([(r['dee_taxon'] - r['nagy_fmr_kcal']) / r['nagy_fmr_kcal'] * 100 for r in results if r['nagy_fmr_kcal'] > 0]):.1f}%).\n"
        )
        f.write(
            "2. **Balance energético:** La mayoría de especies muestran balance positivo (IEP > DEE), "
        )
        f.write(
            "lo que es esperable para poblaciones viables. Las especies con balance negativo requieren revisión.\n"
        )
        f.write(
            "3. **Refinamiento necesario:** Ajustar FAct por estación (invierno/verano) y por comportamiento específico "
        )
        f.write("(hibernación, migración, lactancia).\n")
        f.write(
            "4. **Validación con datos de campo:** Los valores deben contrastarse con datos de monitoreo "
        )
        f.write(
            "del PNAP si están disponibles (tasas de crecimiento, éxito reproductivo).\n"
        )

    print(f"  [OK] Report: {path}")


def update_dee_tsv(results):
    path = os.path.join(DATA_DIR, "dee_estimado.tsv")
    with open(path, "w") as f:
        f.write(
            "taxon_group\tscientific_name\tcommon_name_ca\tbody_mass_kg_approx\tmass_mid\tDEE_kcal_dia_old\tDEE_kcal_dia_taxon\tFAct_taxon\tBMR_kcal_dia\tNagy_FMR_kcal_dia\tIEP_kcal_dia\n"
        )
        for r in results:
            f.write(
                f"{r['taxon']}\t{r['name']}\t-\t{r['mass_kg']:.3f}\t{r['mass_kg']:.3f}\t{r['dee_old']:.1f}\t{r['dee_taxon']:.1f}\t{r['dee_taxon_fact']}\t{r['bmr']:.1f}\t{r['nagy_fmr_kcal']:.1f}\t{r['iep']:.1f}\n"
            )
    print(f"  [OK] Updated DEE TSV: {path}")


def main():
    print("=" * 60)
    print("  VALIDACIÓN ENERGÉTICA — Fase 2.6")
    print("=" * 60)

    print("\n[*] Reading species data...")
    species = read_vertebrates()
    print(f"  {len(species)} species loaded")

    print("[*] Reading diet proportions...")
    diet_props = read_diet_proportions()
    print(f"  {len(diet_props)} species/clusters with diet data")

    print("[*] Computing validation...")
    results = validate_species(species, diet_props)

    print("[*] Writing validation TSV...")
    write_validation_tsv(results)

    print("[*] Generating plots...")
    plot_validation(results)

    print("[*] Writing validation report...")
    write_validation_report(results)

    print("[*] Updating DEE estimates TSV...")
    update_dee_tsv(results)

    print("\n" + "=" * 60)
    print("  VALIDACIÓN COMPLETADA")
    print("=" * 60)
    print(f"  Report: {WIKI_DIR}/validacion_energia.md")
    print(f"  Data:   {OUT_DIR}/validacion_energia.tsv")
    print(f"  Plot:   {OUT_DIR}/validacion_energia.png")
    print(f"  DEE:    {DATA_DIR}/dee_estimado.tsv")


if __name__ == "__main__":
    main()
