"""CLI for the Korea Real Estate API client."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from korea_realestate import KoreaRealEstateClient
from korea_realestate.config import DEFAULT_REGION_CODE
from korea_realestate.exceptions import KoreaRealEstateError

console = Console()


@click.group()
@click.version_option("0.1.0", prog_name="korea-realestate")
@click.pass_context
def cli(ctx):
    """Korea Real Estate API — land, buildings, market trends, events."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = KoreaRealEstateClient()


@cli.command("sales")
@click.option("--region", default=None, help="5-digit 시군구 code (default: DEFAULT_REGION_CODE in .env)")
@click.option("--from", "from_ym", required=True, help="Start year-month (YYYY-MM or YYYYMM)")
@click.option("--to", "to_ym", required=True, help="End year-month (YYYY-MM or YYYYMM)")
@click.option("--land-category", default=None, help="Filter by land category (임, 전, 대, …)")
@click.option("--limit", default=None, type=int, help="Most recent N results")
@click.option("--output", default=None, help="Save results to this CSV file")
@click.pass_context
def cmd_sales(ctx, region, from_ym, to_ym, land_category, limit, output):
    """Query past land sale transactions."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        df = client.events.get_land_sales(
            region_code=region or DEFAULT_REGION_CODE,
            start_year_month=from_ym,
            end_year_month=to_ym,
            land_category=land_category,
            limit=limit,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Land Sales — {region or DEFAULT_REGION_CODE}")
    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("commercial-sales")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--from", "from_ym", required=True, help="Start year-month")
@click.option("--to", "to_ym", required=True, help="End year-month")
@click.option("--type", "property_type", default=None, help="상업용 | 공장 | 창고")
@click.option("--limit", default=None, type=int, help="Most recent N results")
@click.option("--output", default=None, help="Save results to CSV")
@click.pass_context
def cmd_commercial_sales(ctx, region, from_ym, to_ym, property_type, limit, output):
    """Query past commercial / warehouse / factory sales."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        df = client.events.get_commercial_sales(
            region_code=region or DEFAULT_REGION_CODE,
            start_year_month=from_ym,
            end_year_month=to_ym,
            property_type=property_type,
            limit=limit,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Commercial Sales — {region or DEFAULT_REGION_CODE}")
    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("permits")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--from", "from_date", default=None, help="Start date YYYYMMDD")
@click.option("--to", "to_date", default=None, help="End date YYYYMMDD")
@click.option("--type", "permit_type", default=None, help="신축 | 증축 | 대수선 | 철거")
@click.option("--limit", default=None, type=int, help="Most recent N results")
@click.option("--output", default=None, help="Save results to CSV")
@click.pass_context
def cmd_permits(ctx, region, from_date, to_date, permit_type, limit, output):
    """Query building permit history."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        df = client.events.get_permit_history(
            region_code=region or DEFAULT_REGION_CODE,
            start_date=from_date,
            end_date=to_date,
            permit_type=permit_type,
            limit=limit,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Permits — {region or DEFAULT_REGION_CODE}")
    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("zoning")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--dong", default=None, help="Subdivision (읍·면·동) name filter")
@click.option("--output", default=None, help="Save results to CSV")
@click.pass_context
def cmd_zoning(ctx, region, dong, output):
    """Look up zoning and land use classification."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        df = client.land.get_zoning(region_code=region or DEFAULT_REGION_CODE, dong=dong)
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Zoning — {region or DEFAULT_REGION_CODE}")
    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("appraised-value")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--year", type=int, default=None, help="Reference year (e.g. 2024)")
@click.option("--output", default=None, help="Save results to CSV")
@click.pass_context
def cmd_appraised_value(ctx, region, year, output):
    """Get official government-appraised land values."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        df = client.land.get_appraised_value(region_code=region or DEFAULT_REGION_CODE, year=year)
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Appraised Value — {region or DEFAULT_REGION_CODE} {year or ''}")
    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("price-trends")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--type", "index_type", default="land", show_default=True,
              type=click.Choice(["land", "housing"]), help="Index type")
@click.option("--from", "from_ym", required=True, help="Start year-month")
@click.option("--to", "to_ym", required=True, help="End year-month")
@click.option("--limit", default=None, type=int, help="Most recent N results")
@click.option("--output", default=None, help="Save results to CSV")
@click.pass_context
def cmd_price_trends(ctx, region, index_type, from_ym, to_ym, limit, output):
    """Get land or housing price trend index."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        df = client.market.get_price_trends(
            region_code=region or DEFAULT_REGION_CODE,
            index_type=index_type,
            start_year_month=from_ym,
            end_year_month=to_ym,
            limit=limit,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Price Trends ({index_type}) — {region or DEFAULT_REGION_CODE}")
    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("building-registry")
@click.option("--region", default=None, help="5-digit 시군구 code")
@click.option("--parcel", default=None, help="Jibun parcel number (e.g. 100-5)")
@click.option("--ledger-type", default="표제부", help="표제부 | 총괄표제부 | 층별개요 | 지역지구구역")
@click.option("--output", default=None, help="Save results to CSV")
@click.pass_context
def cmd_building_registry(ctx, region, parcel, ledger_type, output):
    """Look up building registry (건축물대장)."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    parcel_main, parcel_sub = None, None
    if parcel:
        parts = parcel.replace("-", " ").split()
        parcel_main = parts[0] if parts else None
        parcel_sub = parts[1] if len(parts) > 1 else "0"
    try:
        df = client.building.get_registry(
            region_code=region or DEFAULT_REGION_CODE,
            parcel_main=parcel_main,
            parcel_sub=parcel_sub,
            ledger_type=ledger_type,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))

    _print_df(df, title=f"Building Registry — {region or DEFAULT_REGION_CODE}")
    if output:
        df.to_csv(output, index=False)
        console.print(f"[green]Saved {len(df)} rows to {output}[/green]")


@cli.command("resolve-address")
@click.argument("address")
@click.pass_context
def cmd_resolve_address(ctx, address):
    """Resolve a Korean address string to structured codes."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        result = client.address.resolve(address)
    except Exception as exc:
        raise click.ClickException(str(exc))

    for key, val in result.items():
        console.print(f"  [cyan]{key}[/cyan]: {val}")


def _print_df(df, title: str, max_rows: int = 30) -> None:
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
