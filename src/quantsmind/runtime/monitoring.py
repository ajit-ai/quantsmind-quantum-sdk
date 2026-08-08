"""
Runtime Monitoring Module

This module provides monitoring management for the Runtime package.

Purpose
-------
Provide monitoring management for the QuantsMind SDK.

Responsibilities
----------------
- Monitor system health
- Track performance metrics
- Support health checks
- Handle alerting

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from quantsmind.runtime.constants import DEFAULT_METRICS_INTERVAL
from quantsmind.runtime.types import MetricDict

logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status enumeration.

    Attributes:
        HEALTHY: System is healthy
        DEGRADED: System is degraded
        UNHEALTHY: System is unhealthy
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Concrete implementation of a health check.

    This class provides health check capabilities.

    Attributes:
        _name: Health check name
        _check_func: Check function
        _last_result: Last check result
        _last_check: Last check timestamp

    Example:
        >>> check = HealthCheck("cpu", lambda: {"status": "healthy"})
        >>> result = check.execute()
    """

    def __init__(self, name: str, check_func: Callable) -> None:
        """Initialize a HealthCheck.

        Args:
            name: Health check name
            check_func: Check function

        Example:
            >>> check = HealthCheck("cpu", lambda: {"status": "healthy"})
        """
        self._name = name
        self._check_func = check_func
        self._last_result: Optional[Dict[str, Any]] = None
        self._last_check: Optional[datetime] = None

    @property
    def name(self) -> str:
        """Get the health check name.

        Returns:
            Health check name

        Example:
            >>> print(f"Name: {check.name}")
        """
        return self._name

    def execute(self) -> Dict[str, Any]:
        """Execute the health check.

        Returns:
            Health check result

        Example:
            >>> result = check.execute()
        """
        try:
            result = self._check_func()
            self._last_result = result
            self._last_check = datetime.utcnow()
            return result
        except Exception as e:
            logger.error(f"Health check failed: {self._name}", exc_info=True)
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
            }


class MonitoringService:
    """Concrete implementation of a monitoring service.

    This class provides monitoring service capabilities.

    Attributes:
        _health_checks: Registered health checks
        _alerts: Active alerts
        _lock: Thread lock

    Example:
        >>> monitoring = MonitoringService()
        >>> monitoring.add_health_check(HealthCheck("cpu", lambda: {"status": "healthy"}))
    """

    def __init__(self) -> None:
        """Initialize a MonitoringService.

        Example:
            >>> monitoring = MonitoringService()
        """
        self._health_checks: Dict[str, HealthCheck] = {}
        self._alerts: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        logger.debug("Created monitoring service")

    @property
    def check_count(self) -> int:
        """Get the number of health checks.

        Returns:
            Number of health checks

        Example:
            >>> print(f"Check count: {monitoring.check_count}")
        """
        with self._lock:
            return len(self._health_checks)

    def add_health_check(self, health_check: HealthCheck) -> None:
        """Add a health check.

        Args:
            health_check: Health check to add

        Example:
            >>> monitoring.add_health_check(HealthCheck("cpu", lambda: {"status": "healthy"}))
        """
        with self._lock:
            self._health_checks[health_check.name] = health_check
        logger.debug(f"Added health check: {health_check.name}")

    def remove_health_check(self, name: str) -> bool:
        """Remove a health check.

        Args:
            name: Health check name

        Returns:
            True if removed, False otherwise

        Example:
            >>> removed = monitoring.remove_health_check("cpu")
        """
        with self._lock:
            if name in self._health_checks:
                del self._health_checks[name]
                return True
        return False

    def execute_health_check(self, name: str) -> Optional[Dict[str, Any]]:
        """Execute a specific health check.

        Args:
            name: Health check name

        Returns:
            Health check result or None

        Example:
            >>> result = monitoring.execute_health_check("cpu")
        """
        with self._lock:
            health_check = self._health_checks.get(name)
            if health_check:
                return health_check.execute()
        return None

    def execute_all_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """Execute all health checks.

        Returns:
            Dictionary of health check results

        Example:
            >>> results = monitoring.execute_all_health_checks()
        """
        with self._lock:
            return {
                name: check.execute()
                for name, check in self._health_checks.items()
            }

    def get_health_status(self) -> str:
        """Get overall health status.

        Returns:
            Overall health status

        Example:
            >>> status = monitoring.get_health_status()
        """
        results = self.execute_all_health_checks()
        
        if not results:
            return HealthStatus.HEALTHY

        statuses = [result.get("status", HealthStatus.UNHEALTHY) for result in results.values()]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED

    def create_alert(self, level: str, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Create an alert.

        Args:
            level: Alert level
            message: Alert message
            metadata: Optional metadata

        Example:
            >>> monitoring.create_alert("warning", "High CPU usage")
        """
        with self._lock:
            self._alerts.append({
                "level": level,
                "message": message,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat(),
            })
        logger.warning(f"Alert created: {level} - {message}")

    def get_alerts(self, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get alerts.

        Args:
            level: Optional alert level filter

        Returns:
            List of alerts

        Example:
            >>> alerts = monitoring.get_alerts("warning")
        """
        with self._lock:
            if level:
                return [alert for alert in self._alerts if alert["level"] == level]
            return self._alerts.copy()

    def clear_alerts(self) -> None:
        """Clear all alerts.

        Example:
            >>> monitoring.clear_alerts()
        """
        with self._lock:
            self._alerts.clear()
        logger.debug("Cleared all alerts")

    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status.

        Returns:
            Monitoring status

        Example:
            >>> status = monitoring.get_status()
        """
        return {
            "health_status": self.get_health_status(),
            "health_checks": list(self._health_checks.keys()),
            "alert_count": len(self._alerts),
            "health_check_results": self.execute_all_health_checks(),
        }


# Export
__all__ = [
    "HealthStatus",
    "HealthCheck",
    "MonitoringService",
]
