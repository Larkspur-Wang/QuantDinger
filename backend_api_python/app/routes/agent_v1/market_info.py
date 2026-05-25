"""Read-class market information endpoints for Agent Gateway clients."""
from __future__ import annotations

from flask import request

from app.data_providers import cached_or_compute, invalidate
from app.data_providers.adanos_sentiment import fetch_adanos_market_sentiment
from app.utils.agent_auth import SCOPE_R, agent_required
from app.utils.logger import get_logger

from . import agent_v1_bp
from ._helpers import envelope, error

logger = get_logger(__name__)


@agent_v1_bp.route("/market-info/adanos-sentiment", methods=["GET"])
@agent_required(SCOPE_R)
def adanos_market_sentiment():
    """Return optional Adanos sentiment through agent-token auth.

    The legacy human UI route lives at `/api/global-market/adanos-sentiment`
    and intentionally uses user JWT auth. This route exposes the same read-only
    provider to automation clients through Agent Gateway scope `R`.
    """
    try:
        tickers = request.args.get("tickers", "")
        source = request.args.get("source")
        days = int(request.args.get("days") or 7)
        force = request.args.get("force", "").lower() in ("true", "1")
        cache_key = f"agent_adanos_sentiment:{source or 'default'}:{days}:{tickers.upper()}"

        def _compute():
            return fetch_adanos_market_sentiment(tickers, source=source, days=days)

        data = cached_or_compute(cache_key, _compute, ttl=300, force=force)
        if isinstance(data, dict) and (not data.get("enabled") or data.get("error")):
            invalidate(cache_key)
        return envelope(data)
    except ValueError as exc:
        return error(400, str(exc), http=400)
    except Exception as exc:
        logger.error("agent adanos_market_sentiment failed: %s", exc, exc_info=True)
        return error(500, "adanos sentiment fetch failed", details=str(exc), retriable=True, http=502)
