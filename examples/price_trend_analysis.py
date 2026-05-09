"""
Price trend analysis example.

Usage:
    python examples/price_trend_analysis.py
    python examples/price_trend_analysis.py --region 42820 --type land --from 2020-01 --to 2025-01
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv(Path(__file__).parent.parent / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

from korea_realestate.clients import PriceTrendsClient
from korea_realestate.exceptions import APIKeyError, KoreaRealEstateError

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Analyse land/housing price trends.")
    parser.add_argument("--region", default=None)
    parser.add_argument("--type", dest="index_type", choices=["land", "housing"], default="land")
    parser.add_argument("--from", dest="from_ym", default="202001")
    parser.add_argument("--to", dest="to_ym", default="202501")
    args = parser.parse_args()

    api_key = os.environ.get("PRICE_TRENDS_API_KEY", "").strip()
    if not api_key or api_key == "your_service_key_here":
        console.print("[red]Error:[/red] PRICE_TRENDS_API_KEY not set in .env")
        sys.exit(1)

    region = args.region or os.environ.get("DEFAULT_REGION_CODE", "42820")

    try:
        client = PriceTrendsClient(api_key=api_key, default_region=region)
        df = client.get_trend_index(
            index_type=args.index_type,
            region_code=region,
            start_year_month=args.from_ym,
            end_year_month=args.to_ym,
        )
    except APIKeyError as exc:
        console.print(f"[red]API key error:[/red] {exc}")
        sys.exit(1)
    except KoreaRealEstateError as exc:
        console.print(f"[red]API error:[/red] {exc}")
        sys.exit(1)

    table = Table(
        title=f"{args.index_type.title()} Price Trend Index — {region}",
        header_style="bold cyan",
    )
    for col in df.columns:
        table.add_column(col)
    for _, row in df.iterrows():
        table.add_row(*[str(v) if v is not None else "" for v in row])

    console.print(table)


if __name__ == "__main__":
    main()
