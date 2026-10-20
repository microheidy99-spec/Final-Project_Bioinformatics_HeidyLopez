# Week 7 Final Project

## Purpose
This project gets all human genes in chromosome 17 (7,000,000 to 9,000,000)
from the Ensembl REST API.
It calculates gene lengths, counts genes by biotype, and makes two plots.

## How to run
From the week7 folder:

    python3 final_analysis.py

Needs Python 3 with requests, pandas, numpy and matplotlib.

## Files
- final_analysis.py: main script
- data.json: raw data from Ensembl
- data.csv: clean table with gene ID, name, biotype, start, end and strand
- figure1.png: histogram of gene lengths
- figure2.png: number of genes per biotype
- analysis_report.md: report with workflow, findings, figures and reflection
- reflection.md: reflection and AI use disclosure
- README.md: this file