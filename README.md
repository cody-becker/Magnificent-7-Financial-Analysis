# Magnificent 7 — Financial Analysis

A data analysis portfolio project examining the seven largest US technology 
companies by market cap: Apple, Microsoft, Google, Amazon, Meta, Nvidia, 
and Tesla.

## Overview
All financial data is pulled directly from the SEC EDGAR public API using 
a custom Python pipeline and stored in a local PostgreSQL database. Analysis 
is conducted in Jupyter Notebook using Python, SQL, and matplotlib.

## Tech Stack
- Python 3.11
- PostgreSQL 18
- Jupyter Notebook
- Libraries: pandas, matplotlib, sqlalchemy, psycopg2, python-dotenv

## Data Source
SEC EDGAR Public API — 10-K annual filings only

## Metrics Analyzed
- Net Income
- Earnings Per Share (EPS)
- Revenue
- Profit Margin
- R&D Spending
- Long Term Debt

## Key Findings
- The Magnificent 7 label obscures significant financial disparity between 
  these companies — at least three distinct tiers exist within the group
- Nvidia's revenue growth from ~$10B to $215B between 2020 and 2026 
  represents one of the most significant market ascents in modern history
- Tesla's financials consistently trail the group across every metric examined
- Microsoft's consistency and acquisition strategy make it structurally 
  resilient regardless of how AI develops
- Meta's low cost structure and margin recovery post-2022 show a 
  fundamentally strong business model

## Structure
- `sec_pipeline.py` — Data pipeline pulling from SEC EDGAR API into PostgreSQL
- `TechData.ipynb` — Full analysis notebook with charts and observations
- `password.env` — Local database credentials (not included in repo)

## Notes
Amazon is excluded from the R&D section as they do not report R&D as a 
separate line item, bundling it into a broader Technology and Content expense.
Several metrics required handling for GAAP naming changes, duplicate fiscal 
year filings, and non-December fiscal year ends across companies.
