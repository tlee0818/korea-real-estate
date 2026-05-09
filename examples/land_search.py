"""
Land sales search example.

Usage:
    python examples/land_search.py
    python examples/land_search.py --region 42820 --from 2022-01 --to 2024-12
    python examples/land_search.py --region 42820 --from 2022-01 --to 2024-12 --land-category 임
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

from korea_realestate.clients import SalesHistoryClient
from korea_realestate.exceptions import APIKeyError, KoreaRealEstateError

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Search past land sales for a region.")
    parser.add_argument("--region", default=None, help="5-digit 시군구 code")
    parser.add_argument("--from", dest="from_ym", default="202001", help="Start YYYYMM (default: 202001)")
    parser.add_argument("--to", dest="to_ym", default="202501", help="End YYYYMM (default: 202501)")
    parser.add_argument("--land-category", default=None, help="Filter: 임, 전, 대, …")
    args = parser.parse_args()

    api_key = os.environ.get("SALES_HISTORY_API_KEY", "").strip()
    if not api_key or api_key == "your_service_key_here":
        console.print("[red]Error:[/red] SALES_HISTORY_API_KEY not set in .env")
        console.print("Copy .env.example → .env and fill in your key from https://www.data.go.kr")
        sys.exit(1)

    region = args.region or os.environ.get("DEFAULT_REGION_CODE", "42820")

    console.print(f"[bold]Searching land sales — region [cyan]{region}[/cyan] "
                  f"from [cyan]{args.from_ym}[/cyan] to [cyan]{args.to_ym}[/cyan][/bold]")
    if args.land_category:
        console.print(f"  Filter: land_category = [cyan]{args.land_category}[/cyan]")

    try:
        client = SalesHistoryClient(api_key=api_key, default_region=region)
        df = client.get_sales(
            region_code=region,
            start_year_month=args.from_ym,
            end_year_month=args.to_ym,
            land_category=args.land_category,
        )
    except APIKeyError as exc:
        console.print(f"[red]API key error:[/red] {exc}")
        sys.exit(1)
    except KoreaRealEstateError as exc:
        console.print(f"[red]API error:[/red] {exc}")
        sys.exit(1)

    if df.empty:
        console.print("[yellow]No results found.[/yellow]")
        return

    # Price per ㎡ statistics
    ppsm = df["price_per_sqm"].dropna()
    stats_table = Table(title="Price per ㎡ Statistics (단위: 만원/㎡)", header_style="bold magenta")
    stats_table.add_column("Metric")
    stats_table.add_column("Value", justify="right")
    stats_table.add_row("Count", str(len(df)))
    stats_table.add_row("Min", f"{ppsm.min():.2f}")
    stats_table.add_row("Max", f"{ppsm.max():.2f}")
    stats_table.add_row("Mean", f"{ppsm.mean():.2f}")
    stats_table.add_row("Median", f"{ppsm.median():.2f}")
    console.print(stats_table)

    # Preview table (first 20 rows)
    preview = Table(title=f"Land Sales Preview (first 20 of {len(df)})", header_style="bold cyan")
    for col in ["deal_date", "dong", "land_category", "area_sqm", "price_10k_won", "price_per_sqm", "zoning"]:
        preview.add_column(col)
    for _, row in df.head(20).iterrows():
        preview.add_row(
            str(row["deal_date"]),
            str(row["dong"]),
            str(row["land_category"]),
            f"{row['area_sqm']:.1f}",
            str(row["price_10k_won"]),
            f"{row['price_per_sqm']:.2f}" if row["price_per_sqm"] else "",
            str(row["zoning"]),
        )
    console.print(preview)

    out_path = f"{region}_land_sales.csv"
    df.to_csv(out_path, index=False)
    console.print(f"[green]Full results saved to {out_path}[/green]")


if __name__ == "__main__":
    main()
