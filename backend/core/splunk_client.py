import logging
import splunklib.client as splunk_client
import splunklib.results as splunk_results
from core.config import settings

logger = logging.getLogger(__name__)

class SplunkClient:

    def __init__(self):
        self.service = None
        self._connect()

    def _connect(self):
        try:
            self.service = splunk_client.connect(
                host=settings.SPLUNK_HOST,
                port=settings.SPLUNK_PORT,
                username=settings.SPLUNK_USERNAME,
                password=settings.SPLUNK_PASSWORD,
            )
            logger.info("Splunk connection successful")
        except Exception as e:
            logger.error(f"Splunk connection failed: {e}")
            self.service = None

    def run_spl_search(self, spl: str, earliest: str = "-1h", latest: str = "now") -> list:
        if not self.service:
            logger.warning("No Splunk connection, returning empty results")
            return []
        try:
            search_query = spl if spl.startswith("search") else f"search {spl}"
            job = self.service.jobs.oneshot(
                search_query,
                earliest_time=earliest,
                latest_time=latest,
                output_mode="json"
            )
            reader = splunk_results.JSONResultsReader(job)
            results = []
            for item in reader:
                if isinstance(item, dict):
                    results.append(item)
            logger.info(f"SPL search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"SPL search error: {e}")
            return []

    def run_anomaly_detection(self, index: str = "*") -> list:
        spl = f"search index={index} | anomalydetection action=summary | head 20"
        return self.run_spl_search(spl, earliest="-24h")

    def run_ml_forecast(self, index: str = "*", metric_field: str = "count") -> list:
        spl = f"search index={index} | timechart count | predict count future_timespan=5"
        return self.run_spl_search(spl, earliest="-7d")

    def get_notable_events(self, limit: int = 20) -> list:
        spl = f"search index=notable | head {limit} | fields *"
        return self.run_spl_search(spl, earliest="-24h")

    def test_connection(self) -> bool:
        try:
            if not self.service:
                return False
            list(self.service.apps.list())
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    async def async_run_spl_search(self, spl: str, earliest: str = "-1h", latest: str = "now") -> list:
        import asyncio
        return await asyncio.to_thread(self.run_spl_search, spl, earliest, latest)

    async def async_run_anomaly_detection(self, index: str = "*") -> list:
        import asyncio
        return await asyncio.to_thread(self.run_anomaly_detection, index)

    async def async_run_ml_forecast(self, index: str = "*", metric_field: str = "count") -> list:
        import asyncio
        return await asyncio.to_thread(self.run_ml_forecast, index, metric_field)

    async def async_get_notable_events(self, limit: int = 20) -> list:
        import asyncio
        return await asyncio.to_thread(self.get_notable_events, limit)

    async def async_test_connection(self) -> bool:
        import asyncio
        return await asyncio.to_thread(self.test_connection)


# Shared singleton instance used across the app
default_splunk_client = SplunkClient()
