import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from ..data.mock_loader import MockDataLoader
from ..engine.translator import ImpactTranslator
from ..engine import universal_indicators
from ..engine import industry_indicators
from ..cache.redis_cache import Layer3RedisCache

logger = logging.getLogger(__name__)


class OperationalService:
    """
    Layer 3 operational indicator service.

    Supports three data-source modes (per blueprint §3.5):
      - 'mock'   → MockDataLoader only
      - 'real'   → Layer2Connector (PostgreSQL + MongoDB)
      - 'hybrid' → real first, mock fallback
    Mode is read from LAYER3_DATA_MODE env var (default 'mock').

    Persists results to TimescaleDB + MongoDB via Layer3Storage when
    persist=True (off by default to avoid DB dependency in tests).
    """

    def __init__(self, data_source_mode: Optional[str] = None, persist: bool = False):
        self.mode = (data_source_mode or os.getenv("LAYER3_DATA_MODE", "mock")).lower()
        self.persist = persist

        self.mock_loader = MockDataLoader()
        self.real_loader = None  # lazy
        self.storage = None      # lazy
        self.cache = Layer3RedisCache()  # gracefully no-ops if Redis unavailable
        self.translator = ImpactTranslator()  # TODO: load rules from PostgreSQL

    # ---- Data loading ------------------------------------------------------

    def _get_real_loader(self):
        if self.real_loader is None:
            from ..data.layer2_connector import Layer2Connector
            self.real_loader = Layer2Connector()
        return self.real_loader

    def _get_storage(self):
        if self.storage is None:
            from ..storage.layer3_storage import Layer3Storage
            self.storage = Layer3Storage()
        return self.storage

    def _fetch_national_indicators(self) -> Dict[str, Any]:
        """Resolve national indicators based on configured data-source mode."""
        if self.mode == "mock":
            return self.mock_loader.get_national_indicators()

        if self.mode == "real":
            return self._get_real_loader().get_latest_national_indicators()

        # hybrid
        try:
            real = self._get_real_loader().get_latest_national_indicators()
            if real and real.get("indicators"):
                return real
            logger.warning("Real Layer 2 returned no indicators, falling back to mock")
        except Exception as e:
            logger.warning(f"Layer 2 unavailable ({e}), falling back to mock")
        return self.mock_loader.get_national_indicators()

    # ---- Validation --------------------------------------------------------

    _REQUIRED_INDICATOR_CODES = {
        # universal indicators
        'ENV_ROAD_STATUS', 'ECON_FUEL_AVAIL', 'ENV_WEATHER_SEV', 'POL_UNREST_01',
        'SOCIAL_HEALTH_ALERTS', 'POL_STRIKE_ACTIVITY', 'SOCIAL_SAFETY_PERCEPTION',
        'ECON_PORT_OPS', 'LEGAL_IMPORT_POLICY', 'ECON_CURRENCY_STAB',
        'ECON_FUEL_PRICES', 'ECON_INFLATION_PRESSURE', 'SOCIAL_WAGE_PRESSURE',
        'LEGAL_REGULATORY_CHANGES', 'LEGAL_TAX_POLICY',
        # industry-specific
        'ECON_CONSUMER_CONF', 'ENV_POWER_RELIABILITY',
    }

    def _validate_national_indicators(self, national_indicators: Dict[str, Any]) -> None:
        """Log warnings for any expected indicator codes missing from the input."""
        present = {
            ind['indicator_code']
            for ind in national_indicators.get('indicators', [])
        }
        missing = self._REQUIRED_INDICATOR_CODES - present
        if missing:
            logger.warning(
                f"Layer 3 engine: {len(missing)} expected indicator code(s) absent — "
                f"calculations will use 0.0 for: {sorted(missing)}"
            )

    # ---- Main pipeline -----------------------------------------------------

    def calculate_indicators_for_company(self, company_id: str) -> Dict[str, Any]:
        """Run full calculation pipeline for a company."""
        company_profile = self.mock_loader.get_company(company_id)
        if not company_profile:
            raise ValueError(f"Company {company_id} not found")

        national_indicators = self._fetch_national_indicators()
        self._validate_national_indicators(national_indicators)

        # 2. Universal indicators (apply to every business)
        universal_results = {
            'transport_availability':
                universal_indicators.calculate_transportation_availability(national_indicators, company_profile),
            'workforce_availability':
                universal_indicators.calculate_workforce_availability(national_indicators, company_profile),
            'supply_chain_integrity':
                universal_indicators.calculate_supply_chain_integrity(national_indicators, company_profile),
            'cost_pressure':
                universal_indicators.calculate_operational_cost_pressure(national_indicators, company_profile),
            'compliance_status':
                universal_indicators.calculate_regulatory_compliance_status(national_indicators, company_profile),
        }

        # 3. Industry-specific indicators
        industry_results: Dict[str, Any] = {}
        industry = company_profile.get('industry')

        if industry == 'retail':
            industry_results['footfall_impact'] = industry_indicators.calculate_retail_footfall_impact(
                national_indicators, company_profile)
        elif industry == 'manufacturing':
            industry_results['production_capacity'] = industry_indicators.calculate_manufacturing_capacity(
                national_indicators, company_profile)
        elif industry == 'logistics':
            industry_results['fleet_availability'] = industry_indicators.calculate_logistics_fleet_availability(
                national_indicators, company_profile)

        # 4. Translation Matrix
        translation_results: List[Dict[str, Any]] = []
        for ind in national_indicators.get('indicators', []):
            translation_results.extend(
                self.translator.translate_to_operational(ind, company_profile)
            )

        # 5. Build output
        final_output = {
            'company_id': company_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data_source_mode': self.mode,
            'universal_indicators': universal_results,
            'industry_specific_indicators': industry_results,
            'translation_impacts': translation_results,
            'status': 'success',
        }

        # 6. Persist (TimescaleDB time-series + MongoDB calculation snapshot)
        if self.persist:
            try:
                self._persist(company_id, universal_results, industry_results, final_output)
            except Exception as e:
                logger.error(f"Layer 3 persistence failed for {company_id}: {e}")
                final_output['status'] = 'computed_but_not_persisted'
                final_output['persist_error'] = str(e)

        # 7. Update Redis current-state cache (fire-and-forget; never blocks caller)
        try:
            asyncio.get_running_loop()
            asyncio.ensure_future(self._cache_current_state(company_id, universal_results, industry_results, final_output['timestamp']))
        except RuntimeError:
            pass  # sync context without event loop — skip cache update

        return final_output

    def _persist(
        self,
        company_id: str,
        universal_results: Dict[str, Any],
        industry_results: Dict[str, Any],
        snapshot: Dict[str, Any],
    ) -> None:
        """Write operational indicators + full snapshot to databases."""
        storage = self._get_storage()

        # Flatten to {code: float} for TimescaleDB write.
        ts_indicators: Dict[str, float] = {}
        for k, v in universal_results.items():
            if isinstance(v, (int, float)):
                ts_indicators[f"OPS_UNIV_{k.upper()}"] = float(v)
        for k, v in industry_results.items():
            if isinstance(v, (int, float)):
                ts_indicators[f"OPS_IND_{k.upper()}"] = float(v)
            elif isinstance(v, dict) and 'value' in v:
                ts_indicators[f"OPS_IND_{k.upper()}"] = float(v['value'])

        # Layer3Storage methods are async — bridge sync caller via asyncio.run
        # only when no event loop is currently running.
        async def _write():
            await storage.store_operational_indicators(
                company_id, ts_indicators,
                metadata={'calculation_method': 'universal+industry'},
            )
            await storage.store_company_snapshot(company_id, snapshot)

        try:
            asyncio.get_running_loop()
            # Already inside an event loop — schedule and forget.
            # Caller is expected to be sync, so this branch is unusual; log it.
            logger.warning("Persist called from inside event loop; scheduling task.")
            asyncio.ensure_future(_write())
        except RuntimeError:
            asyncio.run(_write())

    async def _cache_current_state(
        self,
        company_id: str,
        universal_results: Dict[str, Any],
        industry_results: Dict[str, Any],
        timestamp: str,
    ) -> None:
        """Write flattened indicator values to Redis company:current:{company_id} hash."""
        flat: Dict[str, float] = {}
        for k, v in universal_results.items():
            if isinstance(v, (int, float)):
                flat[f"OPS_UNIV_{k.upper()}"] = float(v)
        for k, v in industry_results.items():
            if isinstance(v, (int, float)):
                flat[f"OPS_IND_{k.upper()}"] = float(v)
            elif isinstance(v, dict) and 'value' in v:
                flat[f"OPS_IND_{k.upper()}"] = float(v['value'])
        await self.cache.set_current_indicators(company_id, flat, timestamp)

    def get_all_companies(self) -> List[Dict[str, Any]]:
        return self.mock_loader.get_all_companies()
