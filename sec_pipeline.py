import os
import requests
import psycopg2
import json
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION — credentials come from .env file
# ============================================================
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "sec_analysis"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

# Add as many companies as you want here
COMPANIES = {
    "Microsoft": "0000789019",
    "Apple":     "0000320193",
    "Nvidia":     "0001045810",
    "Google":     "0001652044",
    "Amazon":     "0001018724",
    "Meta":       "0001326801",
    "Tesla":      "0001318605"
}

# Metrics to pull from SEC — add or remove as needed
METRICS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "NetIncomeLoss",
    "LongTermDebt",
    "OperatingIncomeLoss",
    "EarningsPerShareBasic",
    "Assets",
    "StockholdersEquity",
    "CommonStockSharesOutstanding",
    "ResearchAndDevelopmentExpense",
    "TechnologyAndContentExpense",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "CashAndCashEquivalentsAtCarryingValue"
]

# ============================================================
# SETUP — creates table if it doesn't exist
# ============================================================
def create_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_financials (
            id              SERIAL PRIMARY KEY,
            company_name    TEXT,
            cik             TEXT,
            metric          TEXT,
            value           NUMERIC,
            unit            TEXT,
            period_end      DATE,
            form            TEXT,
            filed           DATE,
            UNIQUE (cik, metric, period_end, form)
        );
    """)
    print("Table ready.")

# ============================================================
# FETCH — pulls data from SEC API
# ============================================================
def fetch_company_facts(cik):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {"User-Agent": "Cody Becker codyjacobbecker@email.com"}  # SEC requires this
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# ============================================================
# PARSE — extracts the metrics you want
# ============================================================
def parse_facts(data, company_name, cik):
    rows = []
    facts = data.get("facts", {}).get("us-gaap", {})

    for metric in METRICS:
        if metric not in facts:
            print(f"  Metric not found: {metric}")
            continue

        units = facts[metric].get("units", {})

        for unit_type, entries in units.items():
            for entry in entries:
                # Only keep annual (10-K) and quarterly (10-Q) filings
                if entry.get("form") not in ("10-K", "10-Q"):
                    continue
                rows.append((
                    company_name,
                    cik,
                    metric,
                    entry.get("val"),
                    unit_type,
                    entry.get("end"),
                    entry.get("form"),
                    entry.get("filed"),
                ))
    return rows

# ============================================================
# LOAD — inserts rows into PostgreSQL
# ============================================================
def load_to_db(rows, cur):
    inserted = 0
    for row in rows:
        try:
            cur.execute("""
                INSERT INTO company_financials 
                    (company_name, cik, metric, value, unit, period_end, form, filed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cik, metric, period_end, form) DO NOTHING;
            """, row)
            inserted += 1
        except Exception as e:
            print(f"  Skipped row: {e}")
    return inserted

# ============================================================
# MAIN — runs everything
# ============================================================
def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    create_table(cur)
    conn.commit()

    for company_name, cik in COMPANIES.items():
        print(f"\nFetching {company_name} (CIK: {cik})...")
        try:
            data = fetch_company_facts(cik)
            rows = parse_facts(data, company_name, cik)
            inserted = load_to_db(rows, cur)
            conn.commit()
            print(f"  Loaded {inserted} rows for {company_name}")
        except Exception as e:
            print(f"  Failed for {company_name}: {e}")

        time.sleep(1)  # Be polite to SEC servers

    cur.close()
    conn.close()
    print("\nDone! Data is in your company_financials table.")

if __name__ == "__main__":
    main()