"""CLI for the Korea Real Estate API client."""

import json
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


def _extract_items(data: dict) -> list[dict]:
    body = data.get("response", {}).get("body", {}) or {}
    items_node = body.get("items") or {}
    if not isinstance(items_node, dict):
        return []
    item = items_node.get("item", [])
    if isinstance(item, dict):
        return [item]
    return item or []


def _print_items(items: list[dict], title: str, output: str | None = None) -> None:
    if not items:
        console.print(f"[yellow]No results for: {title}[/yellow]")
        return

    table = Table(title=title, show_lines=False, header_style="bold cyan")
    for col in items[0]:
        table.add_column(col, overflow="fold")
    for row in items[:30]:
        table.add_row(*[str(v) if v is not None else "" for v in row.values()])
    console.print(table)

    if len(items) > 30:
        console.print(f"[dim]… {len(items) - 30} more rows (use --output to save all)[/dim]")

    if output:
        import csv

        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
        console.print(f"[green]Saved {len(items)} rows to {output}[/green]")


@click.group()
@click.version_option("0.2.0", prog_name="korea-realestate")
@click.pass_context
def cli(ctx):
    """Korea Real Estate API — land, buildings, market trends."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = KoreaRealEstateClient()


@cli.command("sales")
@click.option("--region", default=None)
@click.option("--month", required=True, help="Year-month YYYYMM")
@click.option("--output", default=None)
@click.pass_context
def cmd_sales(ctx, region, month, output):
    """Land sale transactions for one calendar month."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.public_data.land_trade_history(
            region_code=region or DEFAULT_REGION_CODE,
            year_month=month,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data),
        title=f"Land Sales — {region or DEFAULT_REGION_CODE} {month}",
        output=output,
    )


@cli.command("commercial-sales")
@click.option("--region", default=None)
@click.option("--month", required=True, help="Year-month YYYYMM")
@click.option("--output", default=None)
@click.pass_context
def cmd_commercial_sales(ctx, region, month, output):
    """Commercial / warehouse / factory sales for one calendar month."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.public_data.commercial_trade_history(
            region_code=region or DEFAULT_REGION_CODE,
            year_month=month,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data),
        title=f"Commercial Sales — {region or DEFAULT_REGION_CODE} {month}",
        output=output,
    )


@cli.command("permits")
@click.option("--region", default=None)
@click.option("--from", "from_date", default=None, help="Start date YYYYMMDD")
@click.option("--to", "to_date", default=None, help="End date YYYYMMDD")
@click.option("--output", default=None)
@click.pass_context
def cmd_permits(ctx, region, from_date, to_date, output):
    """Building permit records for a region and date range."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.public_data.building_permit_records(
            region_code=region or DEFAULT_REGION_CODE,
            start_date=from_date,
            end_date=to_date,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data),
        title=f"Building Permits — {region or DEFAULT_REGION_CODE}",
        output=output,
    )


@cli.command("zoning")
@click.option("--region", default=None)
@click.option("--dong", default=None)
@click.option("--output", default=None)
@click.pass_context
def cmd_zoning(ctx, region, dong, output):
    """Zoning and land-use classification for a region."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.public_data.land_use_zoning(
            region_code=region or DEFAULT_REGION_CODE,
            dong=dong,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data), title=f"Zoning — {region or DEFAULT_REGION_CODE}", output=output
    )


@cli.command("appraised-value")
@click.option("--region", default=None)
@click.option("--year", type=int, default=None)
@click.option("--output", default=None)
@click.pass_context
def cmd_appraised_value(ctx, region, year, output):
    """Government-appraised individual land prices."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.public_data.individual_land_price(
            region_code=region or DEFAULT_REGION_CODE,
            year=year,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data),
        title=f"Appraised Value — {region or DEFAULT_REGION_CODE}",
        output=output,
    )


@cli.command("standard-price")
@click.option("--region", default=None)
@click.option("--year", type=int, default=None)
@click.option("--output", default=None)
@click.pass_context
def cmd_standard_price(ctx, region, year, output):
    """Publicly announced standard land prices."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.public_data.standard_land_price(
            region_code=region or DEFAULT_REGION_CODE,
            year=year,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data),
        title=f"Standard Price — {region or DEFAULT_REGION_CODE}",
        output=output,
    )


@cli.command("building-ledger")
@click.option("--region", default=None)
@click.option("--parcel", default=None, help="Jibun parcel e.g. 100-5")
@click.option("--ledger-type", default="표제부")
@click.option("--output", default=None)
@click.pass_context
def cmd_building_ledger(ctx, region, parcel, ledger_type, output):
    """Building ledger (건축물대장) for a parcel."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    parcel_main, parcel_sub = None, None
    if parcel:
        parts = parcel.replace("-", " ").split()
        parcel_main = parts[0] if parts else None
        parcel_sub = parts[1] if len(parts) > 1 else "0"
    try:
        data = client.public_data.building_ledger(
            region_code=region or DEFAULT_REGION_CODE,
            parcel_main=parcel_main,
            parcel_sub=parcel_sub,
            ledger_type=ledger_type,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data),
        title=f"Building Ledger — {region or DEFAULT_REGION_CODE}",
        output=output,
    )


@cli.command("price-index")
@click.option("--region", default=None)
@click.option("--type", "index_type", default="land", type=click.Choice(["land", "housing"]))
@click.option("--from", "from_ym", required=True, help="Start YYYYMM")
@click.option("--to", "to_ym", required=True, help="End YYYYMM")
@click.option("--output", default=None)
@click.pass_context
def cmd_price_index(ctx, region, index_type, from_ym, to_ym, output):
    """Land or housing real estate price index (한국부동산원)."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.reb.real_estate_price_index(
            region_code=region or DEFAULT_REGION_CODE,
            index_type=index_type,
            start_year_month=from_ym,
            end_year_month=to_ym,
        )
    except KoreaRealEstateError as exc:
        raise click.ClickException(str(exc))
    _print_items(
        _extract_items(data),
        title=f"Price Index ({index_type}) — {region or DEFAULT_REGION_CODE}",
        output=output,
    )


@cli.command("address-lookup")
@click.argument("address")
@click.pass_context
def cmd_address_lookup(ctx, address):
    """Resolve a Korean address string to structured road/jibun fields."""
    client: KoreaRealEstateClient = ctx.obj["client"]
    try:
        data = client.juso.address_lookup(keyword=address)
    except Exception as exc:
        raise click.ClickException(str(exc))
    results = data.get("results", {}).get("juso", []) or []
    if not results:
        console.print("[yellow]No results[/yellow]")
        return
    for entry in results:
        console.print_json(json.dumps(entry, ensure_ascii=False))


if __name__ == "__main__":
    cli()
