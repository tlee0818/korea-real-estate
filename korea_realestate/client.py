"""Korea Real Estate API — master client."""

from .http.public_data import PublicDataClient
from .http.reb import RebClient
from .http.juso import JusoClient


class KoreaRealEstateClient:
    """
    Thin facade wiring all three HTTP sources.

        client.public_data  → PublicDataClient  (apis.data.go.kr)
        client.reb          → RebClient         (reb.or.kr)
        client.juso         → JusoClient        (juso.go.kr)

    All three accept injectable clients for testing:
        KoreaRealEstateClient(public_data_client=mock, reb_client=mock, juso_client=mock)
    """

    def __init__(
        self,
        public_data_client: PublicDataClient | None = None,
        reb_client: RebClient | None = None,
        juso_client: JusoClient | None = None,
    ):
        self.public_data = public_data_client or PublicDataClient()
        self.reb = reb_client or RebClient()
        self.juso = juso_client or JusoClient()
