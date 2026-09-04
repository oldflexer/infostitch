"""Health Check Module.

Provides health and readiness checks for the application.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from infrastructure.config import get_settings
from infrastructure.db.session import get_db_manager
from infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class HealthStatus(str, Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    name: str
    status: HealthStatus
    message: str
    latency_ms: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class HealthResponse:
    """Overall health response."""
    status: HealthStatus
    timestamp: float
    version: str
    checks: Dict[str, HealthCheckResult]
    uptime_seconds: float
class HealthChecker:
    """Performs health checks on application dependencies."""

    def __init__(self):
        self._start_time = time.time()
        self._settings = get_settings()

    async def check_database(self) -> HealthCheckResult:
        """Check database connectivity."""
        start = time.time()
        try:
            from sqlalchemy import text
            db_manager = get_db_manager()
            async with db_manager.session() as session:
                # Simple query to verify connection
                await session.execute(text("SELECT 1"))
            latency = (time.time() - start) * 1000
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection OK",
                latency_ms=latency,
                details={"url": self._settings.database_url.split("@")[-1] if "@" in self._settings.database_url else "sqlite"},
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            logger.error("Database health check failed", error=str(e))
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {e}",
                latency_ms=latency,
            )

    async def check_external_apis(self) -> HealthCheckResult:
        """Check external API availability (Gemini, Jina)."""
        start = time.time()
        checks = {}
        overall_status = HealthStatus.HEALTHY

        # Check Gemini API key
        if self._settings.gemini_api_key:
            checks["gemini"] = "configured"
        else:
            checks["gemini"] = "not_configured"
            overall_status = HealthStatus.DEGRADED

        # Check Jina API key
        if self._settings.jina_api_key:
            checks["jina"] = "configured"
        else:
            checks["jina"] = "not_configured"
            overall_status = HealthStatus.DEGRADED

        latency = (time.time() - start) * 1000
        return HealthCheckResult(
            name="external_apis",
            status=overall_status,
            message="External API keys check",
            latency_ms=latency,
            details=checks,
        )

    async def check_publishers(self) -> HealthCheckResult:
        """Check publisher configurations."""
        start = time.time()
        checks = {}
        configured_count = 0

        # Telegram
        if self._settings.telegram_bot_token and self._settings.telegram_chat_id:
            checks["telegram"] = "configured"
            configured_count += 1
        else:
            checks["telegram"] = "not_configured"

        # VK
        if self._settings.vk_access_token and self._settings.vk_group_id:
            checks["vk"] = "configured"
            configured_count += 1
        else:
            checks["vk"] = "not_configured"

        # Max
        if self._settings.max_bot_token and self._settings.max_chat_id:
            checks["max"] = "configured"
            configured_count += 1
        else:
            checks["max"] = "not_configured"

        status = HealthStatus.HEALTHY if configured_count > 0 else HealthStatus.DEGRADED
        latency = (time.time() - start) * 1000

        return HealthCheckResult(
            name="publishers",
            status=status,
            message=f"{configured_count}/3 publishers configured",
            latency_ms=latency,
            details=checks,
        )

    async def run_all_checks(self) -> HealthResponse:
        """Run all health checks and return aggregated result."""
        checks = {}

        # Run checks in parallel
        db_check, api_check, pub_check = await asyncio.gather(
            self.check_database(),
            self.check_external_apis(),
            self.check_publishers(),
            return_exceptions=True,
        )

        # Handle exceptions
        for check in [db_check, api_check, pub_check]:
            if isinstance(check, Exception):
                logger.error("Health check exception", error=str(check))
                checks["unknown"] = HealthCheckResult(
                    name="unknown",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {check}",
                    latency_ms=0,
                )
            else:
                checks[check.name] = check

        # Determine overall status
        statuses = [c.status for c in checks.values()]
        if HealthStatus.UNHEALTHY in statuses:
            overall = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY

        return HealthResponse(
            status=overall,
            timestamp=time.time(),
            version="0.1.0",
            checks=checks,
            uptime_seconds=time.time() - self._start_time,
        )


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


async def health_check() -> HealthResponse:
    """Convenience function for health check."""
    checker = get_health_checker()
    return await checker.run_all_checks()


async def readiness_check() -> HealthResponse:
    """Readiness check - only critical dependencies."""
    checker = get_health_checker()
    # For readiness, only check database
    db_check = await checker.check_database()
    checks = {"database": db_check}

    overall = HealthStatus.HEALTHY if db_check.status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY

    return HealthResponse(
        status=overall,
        timestamp=time.time(),
        version="0.1.0",
        checks=checks,
        uptime_seconds=time.time() - checker._start_time,
    )