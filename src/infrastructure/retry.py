"""Retry Utilities with Tenacity.

Provides configurable retry mechanisms with exponential backoff and circuit breaker.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Type, TypeVar, Union

from tenacity import (
    AsyncRetrying,
    RetryCallState,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)
from tenacity.stop import stop_base
from tenacity.wait import wait_base

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker."""
        import time

        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except self.expected_exception as e:
            self.on_failure()
            raise

    async def acall(
            self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute async function with circuit breaker."""
        import time

        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except self.expected_exception as e:
            self.on_failure()
            raise

    def on_success(self) -> None:
        """Reset failure count on success."""
        self.failure_count = 0
        self.state = "closed"

    def on_failure(self) -> None:
        """Increment failure count and potentially open circuit."""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning("Circuit breaker opened",
                           failure_count=self.failure_count)


def get_retry_policy(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    retry_exceptions: Union[Type[Exception], tuple] = Exception,
) -> AsyncRetrying:
    """Create a retry policy with exponential backoff and jitter.

    Args:
        max_attempts: Maximum number of attempts (including first)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Jitter factor (0-1)
        retry_exceptions: Exception types to retry on

    Returns:
        Configured AsyncRetrying instance
    """
    return AsyncRetrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(
            initial=base_delay,
            max=max_delay,
            jitter=jitter,
        ),
        retry=retry_if_exception_type(retry_exceptions),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True,
    )


async def retry_async(
    func: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    retry_exceptions: Union[Type[Exception], tuple] = Exception,
    **kwargs: Any,
) -> T:
    """Execute async function with retry policy.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Jitter factor
        retry_exceptions: Exception types to retry on
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Raises:
        Last exception if all attempts fail
    """
    retry_policy = get_retry_policy(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        jitter=jitter,
        retry_exceptions=retry_exceptions,
    )
    return await retry_policy(func, *args, **kwargs)


def retry_sync(
    func: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    retry_exceptions: Union[Type[Exception], tuple] = Exception,
    **kwargs: Any,
) -> T:
    """Execute sync function with retry policy.

    Args:
        func: Sync function to execute
        *args: Positional arguments for func
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Jitter factor
        retry_exceptions: Exception types to retry on
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Raises:
        Last exception if all attempts fail
    """
    from tenacity import Retrying

    retry_policy = Retrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(
            initial=base_delay,
            max=max_delay,
            jitter=jitter,
        ),
        retry=retry_if_exception_type(retry_exceptions),
        before_sleep=before_sleep_log(logger, "WARNING"),
        reraise=True,
    )
    return retry_policy(func, *args, **kwargs)

    async def acall(
            self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute async function with circuit breaker."""
        import time

        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except self.expected_exception as e:
            self.on_failure()
            raise

    def on_success(self) -> None:
        """Reset failure count on success."""
        self.failure_count = 0
        self.state = "closed"

    def on_failure(self) -> None:
        """Increment failure count and potentially open circuit."""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning("Circuit breaker opened",
                           failure_count=self.failure_count)
