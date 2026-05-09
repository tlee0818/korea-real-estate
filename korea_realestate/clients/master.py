"""KoreaRealEstateClient — namespaced facade wiring all domain clients with shared HTTP."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Optional

from ..http.juso import JusoClient
from ..http.public_data import PublicDataClient
from ..http.reb import RebClient
from .address import AddressClient
from .building import BuildingClient
from .events import EventsClient
from .land import LandClient
from .market import MarketClient


class KoreaRealEstateClient:
    """
    Namespaced entry point for all Korea real estate data.

    Instantiates HTTP clients and domain clients once, wiring shared instances
    so all domains share the same connection pool and config.

    Usage:
        client = KoreaRealEstateClient()
        client.land.get_zoning(region_code="42820")
        client.events.get_land_sales(region_code="42820", start_year_month="202401", end_year_month="202501")
        client.building.get_full_profile(region_code="42820")
        client.market.get_price_trends(region_code="42820", index_type="land", start_year_month="202401", end_year_month="202501")
        client.address.resolve("강원도 고성군 대진리 123")

    Injectable HTTP clients for testing:
        client = KoreaRealEstateClient(
            public_data_client=mock_public,
            reb_client=mock_reb,
            juso_client=mock_juso,
        )
    """

    def __init__(
        self,
        public_data_client: Optional[PublicDataClient] = None,
        reb_client: Optional[RebClient] = None,
        juso_client: Optional[JusoClient] = None,
    ):
        http_public = public_data_client or PublicDataClient()
        http_reb = reb_client or RebClient()
        http_juso = juso_client or JusoClient()

        self._http = SimpleNamespace(
            public_data=http_public,
            reb=http_reb,
            juso=http_juso,
        )

        # Shared singletons — instantiated once, injected into all domain clients
        self.address = AddressClient(http=http_juso)
        self.events = EventsClient(http=http_public)

        # Domain clients receive shared instances, not their own copies
        self.land = LandClient(events=self.events, address=self.address, http=http_public)
        self.building = BuildingClient(events=self.events, address=self.address, http=http_public)
        self.market = MarketClient(events=self.events, address=self.address, http=http_reb)
