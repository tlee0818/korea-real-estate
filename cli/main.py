"""CLI for the Korea Real Estate API client."""

import sys
import os
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

# Allow running as `python -m korea_realestate` without installing
sys.path.insert(0, str(Path(__file__).parent.parent))

from korea_realestate.config import (
    DEFAULT_REGION_CODE,
    SALES_HISTORY_API_KEY,
    PRICE_TRENDS_API_KEY,
    APPRAISED_VALUE_API_KEY,
    ZONING_API_KEY,
)
from korea_realestate.exceptions import KoreaRealEstateError, APIKeyError

console = Console()


def _require_key(key_value: str | None, env_var: str, url: str) -> str:
    """Resolve API key: explicit flag > env var > error."""
    val = key_value or key_value  # placeholder for explicit --api-key flag (future)
    env_val = os.environ.get(env_var, "").strip()
    resolved = val or env_val
    if not resolved or resolved == "your_service_key_here":
        raise click.ClickException(
            f"API key not provided.\n"
            f"Set {env_var} in your .env file or pass --api-key.\n"
            f"Obtain a key at: {url}"
        )
    return resolved


@click.group()
@click.version_option("0.1.0", prog_name="korea-realestate")
def cli():
    """Korea Real Estate API — query land sales, price trends, appraised values, and zoning."""


@cli.command("sales")
@click.option("--region", default=None, help="5-digit 시군구 code (default: DEFAULT_REGION_CODE in .env)")
@click.option("--from", "from_ym", required=True, help="Start year-month (YYYY-MM or YYYYMM)")
@click.option("--to", "to_ym", required=True, help="End year-month (YYYY-MM or YYYYMM)")
@click.option("--land-category", default=None, help="Filter by land category (임, 전, 대, …)")
@click.option("--output", default=None, help="Save results to this CSV file")
@click.option("--api-key", default=None, envvar="SALES_HISTORY_API_KEY", help="Sales History API key")
def cmd_sales(region, from_ym, to_ym, land_category, output, api_key):
    """Query past land sale transactions."""
    from korea_realestate.clients import SalesHistoryClient

    key = _require_key(
        api_key, "SALES_HISTORY_API_KEY",
        "https://www.data.go.kr/data/15126466/openapi.do"
    )
    try:
        client = SalesHistoryClient(api_key=key, default_region=region or DEFAULT_REGION_CODE)
        df = client.get_sales(
            region_code=region,
            start_year_month=from_ym,
            end_year_month=to_ym,
            land_category=land_category,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Land Sales — {region or DEFAULT_REGION_CODE}")

    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("zoning")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--dong", default=None, help="Subdivision (읍·면·동) name filter")
@click.option("--output", default=None, help="Save results to CSV")
@click.option("--api-key", default=None, envvar="ZONING_API_KEY", help="Zoning API key")
def cmd_zoning(region, dong, output, api_key):
    """Look up zoning and land use classification."""
    from korea_realestate.clients import ZoningClient

    key = _require_key(
        api_key, "ZONING_API_KEY",
        "https://www.data.go.kr/data/15113034/openapi.do"
    )
    try:
        client = ZoningClient(api_key=key, default_region=region or DEFAULT_REGION_CODE)
        df = client.get_zoning(region_code=region, dong=dong)
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Zoning — {region or DEFAULT_REGION_CODE}")

    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("price-trends")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--type", "index_type", default="land", show_default=True,
              type=click.Choice(["land", "housing"]), help="Index type")
@click.option("--from", "from_ym", required=True, help="Start year-month")
@click.option("--to", "to_ym", required=True, help="End year-month")
@click.option("--output", default=None, help="Save results to CSV")
@click.option("--api-key", default=None, envvar="PRICE_TRENDS_API_KEY", help="Price Trends API key")
def cmd_price_trends(region, index_type, from_ym, to_ym, output, api_key):
    """Get land or housing price trend index."""
    from korea_realestate.clients import PriceTrendsClient

    key = _require_key(
        api_key, "PRICE_TRENDS_API_KEY",
        "https://www.data.go.kr/data/15134761/openapi.do"
    )
    try:
        client = PriceTrendsClient(api_key=key, default_region=region or DEFAULT_REGION_CODE)
        df = client.get_trend_index(
            index_type=index_type,
            region_code=region,
            start_year_month=from_ym,
            end_year_month=to_ym,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Price Trends ({index_type}) — {region or DEFAULT_REGION_CODE}")

    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("appraised-value")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--year", type=int, default=None, help="Reference year (e.g. 2024)")
@click.option("--output", default=None, help="Save results to CSV")
@click.option("--api-key", default=None, envvar="APPRAISED_VALUE_API_KEY", help="Appraised Value API key")
def cmd_appraised_value(region, year, output, api_key):
    """Get official government-appraised land values."""
    from korea_realestate.clients import AppraisedValueClient

    key = _require_key(
        api_key, "APPRAISED_VALUE_API_KEY",
        "https://www.data.go.kr/data/15057159/openapi.do"
    )
    try:
        client = AppraisedValueClient(api_key=key, default_region=region or DEFAULT_REGION_CODE)
        df = client.get_appraised_value(region_code=region, year=year)
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Appraised Value — {region or DEFAULT_REGION_CODE} {year or ''}")

    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


def _print_df(df, title: str, max_rows: int = 30) -> None:
    import pandas as pd

    if df.empty:
        console.print(f"[yellow]No results for: {title}[/yellow]")
        return

    table = Table(title=title, show_lines=False, header_style="bold cyan")
    for col in df.columns:
        table.add_column(col, overflow="fold")

    for _, row in df.head(max_rows).iterrows():
        table.add_row(*[str(v) if v is not None and str(v) != "nan" else "" for v in row])

    console.print(table)
    if len(df) > max_rows:
        console.print(f"[dim]… {len(df) - max_rows} more rows (use --output to save all)[/dim]")


if __name__ == "__main__":
    cli()
