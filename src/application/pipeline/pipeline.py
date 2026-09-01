"""Pipeline Orchestrator.

Runs pipeline steps in order with error handling, logging, and metrics.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import structlog

from application.dto.pipeline_context import PipelineContext
from application.pipeline.step import PipelineStep
from application.pipeline.step import PipelineStep
from application.services.notification_service import NotificationService
from infrastructure.logging.metrics import (
    MetricsContext,
    increment_counter,
    observe_histogram,
    pipeline_duration_seconds,
    pipeline_runs_total,
    pipeline_step_duration_seconds,
)

logger = structlog.get_logger(__name__)


class Pipeline:
    """Pipeline orchestrator with error handling, logging, and metrics."""
    
    def __init__(
        self,
        steps: List[PipelineStep],
        notification_service: Optional[NotificationService] = None,
    ):
        self._steps = steps
        self._notification_service = notification_service or NotificationService()
    
    async def run(self, context: PipelineContext) -> PipelineContext:
        """Run all steps in order with error handling and metrics."""
        # Set correlation ID for this pipeline run
        correlation_id = context.metrics.get("correlation_id")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())[:8]
            context.metrics["correlation_id"] = correlation_id
        
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        
        logger.info("Pipeline started", correlation_id=correlation_id)
        increment_counter(pipeline_runs_total, {"status": "started"})
        
        # Track overall pipeline duration
        with MetricsContext(pipeline_duration_seconds, {"dummy": "pipeline"}) as timer:
            context.metrics["pipeline_timer"] = timer
            
            for step in self._steps:
                step_name = step.name
                logger.info("Pipeline step started", step=step_name, correlation_id=correlation_id)
                
                step_timer = pipeline_step_duration_seconds.labels(step=step_name).time()
                step_timer.__enter__()
                
                try:
                    context = await step.execute(context)
                    logger.info("Pipeline step completed", step=step_name, correlation_id=correlation_id)
                except Exception as e:
                    logger.error("Pipeline step failed", step=step_name, error=str(e), correlation_id=correlation_id, exc_info=True)
                    context.add_error(step_name, str(e))
                    
                    # Send error notification
                    await self._notification_service.notify_error(
                        error=e,
                        context={
                            "correlation_id": correlation_id,
                            "step": step_name,
                            "article_id": context.metrics.get("current_article_id", "unknown"),
                        },
                        severity="ERROR",
                    )
                    
                    # Graceful degradation: continue with next step
                    logger.warning("Continuing pipeline after step failure", step=step_name, correlation_id=correlation_id)
                finally:
                    step_timer.__exit__(None, None, None)
        
        # Determine overall status
        status = "failure" if context.errors else "success"
        increment_counter(pipeline_runs_total, {"status": status})
        
        logger.info("Pipeline completed", correlation_id=correlation_id, status=status, errors=len(context.errors))
        
        # Send critical notification if pipeline failed
        if status == "failure" and self._notification_service:
            await self._notification_service.notify_critical(
                message=f"Pipeline failed with {len(context.errors)} error(s)",
                context={"correlation_id": correlation_id},
            )
        
        structlog.contextvars.unbind_contextvars("correlation_id")
        return context
    
    def add_step(self, step: PipelineStep) -> None:
        """Add step to pipeline."""
        self._steps.append(step)
    
    @property
    def steps(self) -> List[PipelineStep]:
        return self._steps