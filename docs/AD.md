# Architecture Decisions (AD)
## News Aggregator & Publisher System

### AD1: Use DDD for Domain Modelling
**Context**: System has complex business rules (deduplication, template selection, multiple channels).  
**Decision**: Model core entities (Article, Post, Source, Channel) and value objects (URL, Embedding) as domain objects with clear boundaries.  
**Consequences**: Clear separation of concerns; easier to test; easier to change business logic.

### AD2: Apply Pipeline Pattern for Processing
**Context**: Processing flow is sequential and may evolve (add/remove steps).  
**Decision**: Implement each step as a separate class implementing `PipelineStep` interface; orchestrator runs them in order.  
**Consequences**: Easy to add new steps (e.g., sentiment analysis), easier to test each step in isolation.

### AD3: Dependency Injection via Constructor Injection
**Context**: Need to swap implementations (e.g., SQLite → PostgreSQL, Gemini → Claude).  
**Decision**: Use simple dependency injection (or `dependency-injector` library) to inject repositories, clients, services.  
**Consequences**: Decoupling, easier unit testing with mocks.

### AD4: Configuration Stored in Database
**Context**: Settings (RSS URLs, thresholds, enabled channels) change frequently; would require restarts if in code/env.  
**Decision**: Store all configurable parameters in `settings` table; read on each pipeline run.  
**Consequences**: Dynamic updates via dashboard without redeployment; but requires DB access.

### AD5: SQLite for Initial Development, with Abstraction
**Context**: Quick setup, no external dependency. But future may require PostgreSQL for pgvector.  
**Decision**: Use SQLAlchemy ORM with Alembic; repositories interface; SQLite in dev, PostgreSQL in prod (configurable).  
**Consequences**: Easy migration; slight overhead of ORM but manageable.

### AD6: In-Memory Cache for LLM Responses
**Context**: Repeated calls to expensive APIs (embeddings, post generation) for same inputs.  
**Decision**: Implement simple TTL cache (e.g., `cachetools` with maxsize=1000, ttl=1 hour).  
**Consequences**: Saves cost and time; must invalidate when content changes.

### AD7: Use Structlog for Structured Logging
**Context**: Need detailed, searchable logs for monitoring and debugging.  
**Decision**: Log all events as JSON with consistent fields (timestamp, level, module, message, extra).  
**Consequences**: Easier to parse with ELK or query via dashboard; slightly more verbose.

### AD8: Streamlit for Dashboard
**Context**: Need quick, interactive UI for admin tasks and monitoring.  
**Decision**: Use Streamlit due to rapid development, integrates well with Python, and can be run on same VPS.  
**Consequences**: Less control over styling but sufficient for internal tool; requires separate process.

### AD9: External Cron for Scheduling
**Context**: Simple, reliable scheduling; no need for complex job queue.  
**Decision**: Use system cron to run CLI script every 3 hours (or configured interval).  
**Consequences**: Easy to set up; no additional dependencies; but cannot easily reschedule dynamically (though config can be in DB for next run time).

### AD10: Graceful Degradation
**Context**: External APIs may fail; system should still operate partially.  
**Decision**: Each publishing channel is wrapped in try/except; if one fails, log and continue with others. If LLM fails, use fallback template.  
**Consequences**: Higher reliability; but may produce less optimal posts.