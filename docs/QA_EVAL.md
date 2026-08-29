# Quality Assurance Evaluation Strategy
## News Aggregator & Publisher System

### 1. Code Quality Metrics

| Metric                     | Tool           | Target                     |
|----------------------------|----------------|----------------------------|
| Code coverage              | pytest-cov     | ≥ 80% lines and branches   |
| Static type checking       | mypy           | No errors (strict mode)    |
| Linting (PEP8, style)      | flake8, black  | Zero issues (black format) |
| Cyclomatic complexity      | radon / mccabe | ≤ 10 per function          |
| Documentation coverage     | pydocstyle     | ≥ 90% of public functions  |
| Maintainability Index      | radon          | ≥ 65                       |
| Dependencies (vulnerabilities) | safety     | No critical vulnerabilities |

### 2. Process Quality
- **Code Review**: All non-trivial changes reviewed by another developer (or self-review with checklist).
- **Commit Message Convention**: Conventional Commits (feat, fix, docs, test, refactor).
- **Branching Strategy**: Git Flow (main, develop, feature/xxx).
- **Continuous Integration**: Run linting, static analysis, and unit tests on every push (CI setup recommended but optional for now).

### 3. Operational Quality Metrics
| Metric                      | Target                          |
|-----------------------------|---------------------------------|
| Pipeline success rate       | ≥ 95% (excluding external outages) |
| Average pipeline duration   | < 2 minutes                     |
| API call success rate       | ≥ 98%                           |
| Notification delivery       | 100% for critical errors        |
| Data integrity (DB)         | No duplicate publish of same URL (primary key constraint) |

### 4. Evaluation Process
- **Weekly Review**: Check logs and metrics dashboard; identify trends.
- **Post-Mortem**: For critical failures, produce a short report with root cause and action items.
- **Regression Testing**: Before each release, run full test suite.

### 5. Tools
- **Linting & Formatting**: pre‑commit with flake8, black, isort.
- **Type Checking**: mypy.
- **Test Coverage**: pytest-cov (HTML report).
- **Monitoring**: Prometheus + Streamlit dashboard.
- **Logging**: structlog (JSON) for easy parsing.

### 6. Sign-off Criteria for Release
- All tests passed.
- Coverage ≥80%.
- No mypy errors.
- Manual smoke test on staging (or production dry-run) with all channels mocked.
- Acceptance by product owner (you).