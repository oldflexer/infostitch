# Test Plan
## News Aggregator & Publisher System

### 1. Test Strategy
We adopt a pyramid approach: many unit tests, fewer integration tests, and a few end-to-end tests.

#### 1.1 Unit Tests
- **Scope**: Domain entities, value objects, utility functions, service logic (with mocked dependencies).
- **Tools**: `pytest`, `pytest-mock`.
- **Coverage target**: ≥80% lines and branches.
- **Run**: `pytest tests/unit/`

#### 1.2 Integration Tests
- **Scope**: Repository implementations (against test SQLite), pipeline steps (with HTTP mocks using `responses` or `pytest-httpx`), and service integrations.
- **Tools**: `pytest`, `pytest-httpx`, `pytest-sqlalchemy` (temporary test DB).
- **Run**: `pytest tests/integration/`

#### 1.3 End-to-End Tests
- **Scope**: Full pipeline execution from RSS fetching to "publishing" (channels are mocked). Uses a dedicated test configuration.
- **Tools**: `pytest`, with a test settings table.
- **Run**: `pytest tests/e2e/`

#### 1.4 Performance/Load Tests (optional)
- **Scope**: Measure time per step, memory usage.
- **Tools**: custom script with `time`, `memory_profiler`.
- **Threshold**: Full cycle < 2 minutes for 20 articles.

### 2. Test Environment
- **CI**: GitHub Actions or GitLab CI (can be added later). For now, run locally.
- **Test DB**: SQLite in-memory (`:memory:`) or file-based for integration tests.
- **Mocks**: External APIs are mocked to avoid cost and network dependency.

### 3. Test Data
- Fixed set of RSS test feeds (local files or mocked responses).
- Predefined articles with known duplicates and edge cases.

### 4. Acceptance Criteria
- All tests pass.
- Coverage ≥80%.
- No critical bugs after stabilization period.
- Pipeline executes without human intervention for 7 days straight.

### 5. Schedule
- Unit tests run on every commit (pre‑commit or CI).
- Integration and E2E tests run before merging to main.
- Performance tests run weekly.

### 6. Defect Tracking
- Issues logged in GitHub/GitLab issue tracker.
- Severity levels: Critical (system down), Major (functionality broken), Minor (cosmetic).

### 7. Sign-off
- System owner (you) approves after observing production runs for 1 week.