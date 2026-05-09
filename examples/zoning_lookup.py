"""
Zoning lookup example.

Usage:
    python examples/zoning_lookup.py
    python examples/zoning_lookup.py --region 42820 --dong 대진리
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

from korea_realestate.clients import ZoningClient
from korea_realestate.exceptions import APIKeyError, KoreaRealEstateError

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Look up zoning classification for a region.")
    parser.add_argument("--region", default=None)
    parser.add_argument("--dong", default=None, help="Subdivision (읍·면·동) filter")
    args = parser.parse_args()

    api_key = os.environ.get("ZONING_API_KEY", "").strip()
    if not api_key or api_key == "your_service_key_here":
        console.print("[red]Error:[/red] ZONING_API_KEY not set in .env")
        sys.exit(1)

    region = args.region or os.environ.get("DEFAULT_REGION_CODE", "42820")

    try:
        client = ZoningClient(api_key=api_key, default_region=region)
        df = client.get_zoning(region_code=region, dong=args.dong)
    except APIKeyError as exc:
        console.print(f"[red]API key error:[/red] {exc}")
        sys.exit(1)
    except KoreaRealEstateError as exc:
        console.print(f"[red]API error:[/red] {exc}")
        sys.exit(1)

    table = Table(title=f"Zoning — {region}", header_style="bold cyan")
    for col in df.columns:
        table.add_column(col, overflow="fold")
    for _, row in df.head(50).iterrows():
        table.add_row(*[str(v) if v is not None and str(v) != "nan" else "" for v in row])

    console.print(table)
    if len(df) > 50:
        console.print(f"[dim]… {len(df) - 50} more rows[/dim]")


if __name__ == "__main__":
    main()
