"""Seeded synthetic digital-lending loan book (no proprietary data).

Loans get a repayment *behavior* (on-time / late / default) so the marts
have realistic DPD buckets, NPLs and vintage curves to aggregate:
- on-time (~72%): fully repaid in installments before maturity
- late (~18%): keeps paying past maturity, lands in a DPD bucket
- default (~10%): pays a fraction then goes silent -> NPL after 90 days
"""

from __future__ import annotations

import argparse
import csv
import random
import tempfile
from datetime import date, timedelta
from pathlib import Path

import duckdb

SEED = 7
N_LOANS = 12_000
TODAY = date.today()

PRODUCTS = {
    # product: (weight, term_days, principal_usd_range, annual_rate_pct_range)
    "nano_loan": (0.45, 21, (10, 80), (24, 36)),
    "micro_loan": (0.30, 120, (100, 900), (18, 30)),
    "sme_loan": (0.10, 365, (1_000, 12_000), (12, 22)),
    "bnpl": (0.15, 60, (30, 400), (0, 8)),
}
COUNTRIES = {"SN": ("XOF", 0.30), "CI": ("XOF", 0.20), "BJ": ("XOF", 0.10),
             "NG": ("NGN", 0.25), "KE": ("KES", 0.15)}
SEGMENTS = {"nano": 0.55, "micro": 0.35, "sme": 0.10}
BEHAVIORS = {"on_time": 0.72, "late": 0.18, "default": 0.10}
FX_TO_USD = {"XOF": 655.957, "NGN": 1550.0, "KES": 130.0}


def _weighted(rng: random.Random, weights_by_key: dict[str, float]) -> str:
    keys = list(weights_by_key)
    return rng.choices(keys, weights=[weights_by_key[k] for k in keys])[0]


def generate(rng: random.Random) -> tuple[list[tuple], list[tuple]]:
    loans, repayments = [], []
    payment_id = 0
    for i in range(N_LOANS):
        product = _weighted(rng, {p: w for p, (w, *_ ) in PRODUCTS.items()})
        _, term_days, principal_range, rate_range = PRODUCTS[product]
        country = _weighted(rng, {c: w for c, (_, w) in COUNTRIES.items()})
        currency = COUNTRIES[country][0]

        disbursed = TODAY - timedelta(days=rng.randint(0, 720))
        maturity = disbursed + timedelta(days=term_days)
        principal_usd = round(rng.uniform(*principal_range), 2)
        principal_local = round(principal_usd * FX_TO_USD[currency], 2)
        rate = round(rng.uniform(*rate_range), 1)
        total_due_local = round(
            principal_local * (1 + rate / 100 * term_days / 365), 2
        )

        loans.append((
            f"L{i:06d}", f"C{rng.randint(0, 2999):06d}",
            disbursed.isoformat(), maturity.isoformat(),
            principal_local, currency, rate, product, country,
            _weighted(rng, SEGMENTS),
        ))

        behavior = _weighted(rng, BEHAVIORS)
        n_installments = max(1, term_days // 15)
        if behavior == "on_time":
            paid_share, last_offset = 1.0, 0
        elif behavior == "late":
            paid_share = rng.uniform(0.7, 1.0)
            last_offset = rng.randint(5, 75)
        else:
            paid_share = rng.uniform(0.0, 0.6)
            last_offset = -rng.randint(0, term_days // 2)

        remaining = total_due_local * paid_share
        for k in range(n_installments):
            if remaining <= 0:
                break
            pay_date = disbursed + timedelta(
                days=int((term_days + last_offset) * (k + 1) / n_installments)
            )
            if pay_date > TODAY:
                break
            amount = round(min(remaining, total_due_local / n_installments), 2)
            if amount <= 0:
                break
            payment_id += 1
            repayments.append((
                f"P{payment_id:07d}", f"L{i:06d}", pay_date.isoformat(),
                amount, currency,
                _weighted(rng, {"mobile_money": 0.8, "bank": 0.12, "agent": 0.08}),
            ))
            remaining -= amount
    return loans, repayments


def load(db_path: str) -> tuple[int, int]:
    rng = random.Random(SEED)
    loans, repayments = generate(rng)
    con = duckdb.connect(db_path)
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        con.execute("DROP TABLE IF EXISTS raw.loans")
        con.execute("DROP TABLE IF EXISTS raw.repayments")
        con.execute("""
            CREATE TABLE raw.loans (
                loan_id VARCHAR, customer_id VARCHAR, disbursed_at DATE,
                maturity_date DATE, principal DOUBLE, currency VARCHAR,
                interest_rate_pct DOUBLE, product_type VARCHAR,
                country VARCHAR, segment VARCHAR
            )
        """)
        con.execute("""
            CREATE TABLE raw.repayments (
                payment_id VARCHAR, loan_id VARCHAR, payment_date DATE,
                amount DOUBLE, currency VARCHAR, channel VARCHAR
            )
        """)
        with tempfile.TemporaryDirectory() as tmp:
            for name, rows in (("loans", loans), ("repayments", repayments)):
                csv_path = Path(tmp) / f"{name}.csv"
                with open(csv_path, "w", newline="") as handle:
                    csv.writer(handle).writerows(rows)
                con.execute(f"COPY raw.{name} FROM '{csv_path}' (FORMAT CSV, NULL '')")
    finally:
        con.close()
    return len(loans), len(repayments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="lending.duckdb")
    args = parser.parse_args()
    n_loans, n_payments = load(args.db)
    print(f"{n_loans} loans, {n_payments} repayments -> {args.db}")
