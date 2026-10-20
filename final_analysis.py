#!/usr/bin/env python3
# final_analysis.py
# Retrieves human genes in region 17:7,000,000-9,000,000 from the Ensembl REST API,
# saves them as JSON/CSV, analyzes them, and generates figures.

import json
import sys
import requests
import pandas as pd
# --------------------------------------------------------------
import numpy as np
import matplotlib
matplotlib.use("Agg")  # no screen on the server; save figures to files
import matplotlib.pyplot as plt
# -----------------------------------------------------------
# Ensembl server and genomic region to query
SERVER = "https://rest.ensembl.org"
REGION = "17:7000000-9000000"


# Request all genes in a genomic region from Ensembl.
# Returns a list of dictionaries (one per gene).
def fetch_genes(region):
    url = f"{SERVER}/overlap/region/human/{region}?feature=gene"
    try:
        r = requests.get(url, headers={"Content-Type": "application/json"}, timeout=60)
        r.raise_for_status()  # stop if the server returns an error code
    except requests.RequestException as e:
        sys.exit(f"Error connecting to Ensembl: {e}")
    return r.json()


# Save the raw data to data.json and a clean table to data.csv.
# Returns a pandas DataFrame.
def save_data(genes):
    with open("data.json", "w") as f:
        json.dump(genes, f, indent=2)
    df = pd.DataFrame(genes)
    df = df[["id", "external_name", "biotype", "start", "end", "strand"]]
    df.to_csv("data.csv", index=False)
    return df


# Analysis 1: compute gene length (bp) and print summary stats.
def add_gene_length(df):
    df["length"] = df["end"] - df["start"] + 1
    print("\nGene length summary (bp):")
    print(df["length"].describe().round(0))
    print("\nMedian length by biotype:")
    print(df.groupby("biotype")["length"].median().sort_values(ascending=False))
    return df


# Analysis 2: count how many genes belong to each biotype.
# Returns a pandas Series.
def count_biotypes(df):
    counts = df["biotype"].value_counts()
    print("\nGenes per biotype:")
    print(counts)
    return counts

# ------------------------------------------------------------
# Figure 1: histogram of gene lengths (log scale) with median line.
def plot_length_histogram(df, outfile="figure1.png"):
    bins = np.logspace(np.log10(df["length"].min()), np.log10(df["length"].max()), 30)
    median = df["length"].median()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["length"], bins=bins, color="steelblue", edgecolor="black", label="Genes")
    ax.axvline(median, color="red", linestyle="--", label=f"Median = {median:,.0f} bp")
    ax.set_xscale("log")
    ax.set_xlabel("Gene length (bp, log scale)")
    ax.set_ylabel("Number of genes")
    ax.set_title(f"Gene length distribution, human chr{REGION} (n={len(df)})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outfile, dpi=300)
    plt.close(fig)
    print(f"Saved: {outfile}")


# Figure 2: bar chart of genes per biotype, colored by broad category.
def plot_biotype_counts(counts, outfile="figure2.png"):
    # Assign each biotype to a broad group for coloring
    def group(b):
        if b == "protein_coding":
            return "Protein coding"
        if "pseudogene" in b:
            return "Pseudogene"
        return "Non-coding RNA / other"

    colors = {"Protein coding": "steelblue", "Pseudogene": "gray",
              "Non-coding RNA / other": "darkorange"}
    counts = counts.sort_values()
    bar_colors = [colors[group(b)] for b in counts.index]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(counts.index, counts.values, color=bar_colors, edgecolor="black")
    for i, v in enumerate(counts.values):
        ax.text(v + 1, i, str(v), va="center")  # count label at end of each bar
    ax.set_xlabel("Number of genes")
    ax.set_ylabel("Biotype")
    ax.set_title(f"Genes per biotype, human chr{REGION}")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors.values()]
    ax.legend(handles, colors.keys(), loc="lower right")
    fig.tight_layout()
    fig.savefig(outfile, dpi=300)
    plt.close(fig)
    print(f"Saved: {outfile}")

#----------------------------------------------------------
# Main workflow: retrieve -> save -> analyze
# Main workflow: retrieve -> save -> analyze -> plot
def main():
    genes = fetch_genes(REGION)
    print(f"Genes retrieved: {len(genes)}")
    df = save_data(genes)
    print("Saved: data.json, data.csv")
    df = add_gene_length(df)
    counts = count_biotypes(df)
    plot_length_histogram(df)
    plot_biotype_counts(counts)


if __name__ == "__main__":
    main()