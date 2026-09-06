# Pylance Static Analysis Warnings - Fix Plan

## Overview
- **Total Issues**: ~250+ Pylance warnings
- **Nature**: Static type analysis warnings (NOT runtime errors)
- **Test Status**: ✅ 446 tests pass, 90% coverage
- **Production Status**: ✅ Fully functional

---

## Phase 1: Core Production Code Types (HIGH PRIORITY)
*Fixes that improve type safety in production code*

### 1.1 `src/infrastructure/db/sqlalchemy_models.py`
| Line | Issue | Fix |
|------|-------|-----|
| 35 | Unused `Engine` import | Remove import |
| 43 | `type_annotation_map` partially unknown | Add `from typing import Dict, List, Any` and type as `Dict[Any, Any]` |
| 187 | `Index` with `postgresql_where` string | Use `text("is_duplicate = false")` from `sqlalchemy` |
| 287 | `event.listen` PRAGMA execution | Use `text("PRAGMA journal_mode=WAL;")` and `connection.execute(text(...))` |

### 1.2 Domain Entities - Add Generic Type Arguments
| File | Method | Current | Fixed |
|------|--------|---------|-------|
| `channel.py` | `to_dict()` | `-> dict` | `-> dict[str, Any]` |
| `channel.py` | `config` field | `dict` | `dict[str, Any]` |
| `llm_model.py` | `to_dict()` | `-> dict` | `-> dict[str, Any]` |
| `rss_source.py` | `to_dict()` | `-> dict` | `-> dict[str, Any]` |
| `user.py` | `to_dict()` | `-> dict` | `-> dict[str, Any]` |
| `article.py` | `from_rss_entry()` param | `entry: dict` | `entry: dict[str, Any]` |
| `article.py` | `to_dict()` | `-> dict` | `-> dict[str, Any]` |
| `post.py` | `to_dict()` | `-> dict` | `-> dict[str, Any]` |
| `log.py` | `to_dict()` | `-> dict` | `-> dict[str, Any]` |

### 1.3 `src/infrastructure/config.py`
| Line | Issue | Fix |
|------|-------|-----|
| 9 | Unused `Optional` import | Remove |
| 123 | Return type `dict[Unknown, Unknown]` | `-> dict[str, Any]` |
| 136-169 | List append type inference | Add type annotation: `channels: list[dict[str, Any]] = []` |
| 171 | Return type `list[Unknown]` | `-> list[dict[str, Any]]` |
| 200 | `json` possibly unbound | Initialize `json = {}` before try block |
| 233 | `List` without type args | `List[dict[str, Any]]` |
| 236-237 | Return types `list[Unknown]` | `-> list[dict[str, Any]]` |

### 1.4 `src/application/dto/pipeline_context.py`
| Lines | Issue | Fix |
|-------|-------|-----|
| 20-51 | All list/dict fields unknown | Add proper generics: `list[Article]`, `dict[str, Any]`, etc. |
| 8 | Unused `Optional` import | Remove |

### 1.5 `src/infrastructure/logging/logger.py`
| Line | Issue | Fix |
|------|-------|-----|
| 10 | Unused `Dict` import | Remove |
| 80, 91, 93, 96 | List type unknown | Add `list[Processor]` type hints |

### 1.6 `src/domain/value_objects/url.py`
| Line | Issue | Fix |
|------|-------|-----|
| 7 | Unused `re` import | Remove |
| 130-131 | List append/join unknown | Add type annotation to list |

### 1.7 `src/domain/value_objects/template.py`
| Line | Issue | Fix |
|------|-------|-----|
| 19 | `variables` list unknown | `list[str]` |
| 44-45 | Append/return unknown | Add type annotation |

### 1.8 `src/domain/value_objects/embedding.py`
| Line | Issue | Fix |
|------|-------|-----|
| 23 | Unnecessary `isinstance` | Remove check (always true) |

---

## Phase 2: Repository & Service Layer (MEDIUM PRIORITY)

### 2.1 Repository Files - Fix rowcount Access
| File | Lines | Fix |
|------|-------|-----|
| channel_repo.py | 92 | Add type: ignore[attr-defined] or cast |
| llm_model_repo.py | 95 | Same |
| setting_repo.py | 58 | Same |
| source_repo.py | 83, 93 | Same |
| user_repo.py | 92 | Same |
| post_repo.py | 175, 288 | Same |
| log_repo.py | Various | Fix and_ clause types

### 2.2 src/infrastructure/db/repositories/post_repo.py
| Line | Issue | Fix |
|------|-------|-----|
| 4 | Unused math import | Remove |
| 27, 235 | from_bytes argument type | Cast embedding to bytes |
| 157 | Embedding assignment | Handle None case |
| 248 | Method obscured | Rename or remove duplicate

### 2.3 src/infrastructure/db/repositories/setting_repo.py
| Line | Issue | Fix |
|------|-------|-----|
| 5 | Unused List import | Remove |
| 7 | Unused insert import | Remove |
| 99 | None to Dict[str, str] | Add Optional[Dict[str, str]]

### 2.4 src/infrastructure/db/repositories/article_repo.py
| Line | Issue | Fix |
|------|-------|-----|
| 6, 11 | Unused imports | Remove select, func, RssSourceModel

### 2.5 src/infrastructure/db/repositories/log_repo.py
| Line | Issue | Fix |
|------|-------|-----|
| 12 | Unused or_ import | Remove |
| 139-227 | List append/and_ unknown | Add type annotations

### 2.6 Service Files - Fix Mock Return Types
| File | Issue | Fix |
|------|-------|-----|
| notification_service.py | Mock client return types | Add proper Protocol or base class |
| embedding_service.py | MockGeminiClient return | Same |
| image_service.py | MockJinaClient return | Same |
| publisher_service.py | All mock clients | Same

### 2.7 Pipeline Steps - Add Generic Types
| File | Issue | Fix |
|------|-------|-----|
| check_embedding_duplicate.py | List/dict unknown | Add generics |
| compute_embedding.py | List append unknown | Add generics |
| deduplicate.py | Unused imports | Remove |
| extract_content.py | List append unknown | Add generics |
| fetch_rss.py | feedparser types | Add feedparser stubs or ignore |
| generate_post.py | List append unknown | Add generics |
| publish.py | Dict/list unknown | Add generics |
| select_top.py | List append unknown | Add generics

### 2.8 src/infrastructure/clients/*.py - All Clients
| File | Issues | Fix |
|------|--------|-----|
| telegram_client.py | Dict/list unknown, signal handler types | Add generics, fix __call__ signature |
| gemini_client.py | Dict/list unknown, __call__ signature | Add generics |
| jina_client.py | Dict unknown, __call__ signature | Add generics |
| max_client.py | Dict/list unknown, __call__ signature | Add generics |
| vk_client.py | Param types, dict/list unknown | Add type annotations

### 2.9 src/infrastructure/health.py
| Line | Issue | Fix |
|------|-------|-----|
| 105, 143, 184 | Dict unknown | Add dict[str, Any] |
| 169 | BaseException.name | Use type(e).__name__ |
| 172 | Loop variable types | Add type annotations |
| 221 | Protected _start_time | Use property or public method

### 2.10 src/infrastructure/retry.py
| Line | Issue | Fix |
|------|-------|-----|
| 48, 68 | Float - None subtraction | Add None check |
| 75 | Object not awaitable | Fix return type |
| 103, 137, 175 | Tuple without args | tuple[type[Exception], ...] |
| 125, 206 | Log level string vs int | Use logging.WARNING |
| 165 | Function return type | Fix generic signature |
| 11, 17, 18 | Unused imports | Remove |
| 58, 78 | Unused e variable | Use _

### 2.11 src/infrastructure/cache/cache_service.py
| Line | Issue | Fix |
|------|-------|-----|
| 7 | Unused time import | Remove |
| 87 | Unused settings | Use or remove

---

## Phase 3: Presentation Layer (LOW PRIORITY)

### 3.1 CLI - src/presentation/cli/run.py
| Line | Issue | Fix |
|------|-------|-----|
| 65, 371 | Signal handler params | Add signum: int, frame: Optional[FrameType] |
| 69, 70, 375, 376 | Handler type | Use Callable[[int, Optional[FrameType]], None] |
| 114 | Context type | Add proper union type |
| 116, 271, 274, 277, 281, 285, 295 | Unused variables | Remove or use _ prefix

### 3.2 Dashboard - src/presentation/dashboard/app.py
| Line | Issue | Fix |
|------|-------|-----|
| 11 | Unused get_settings import | Remove |
| 41, 48 | Dict unknown | Add dict[str, Any] |
| 68 | Coroutine type | Add proper return type |
| 215 | Function obscured | Rename inner function

### 3.3 Dashboard Pages - All Pages
| File | Issues | Fix |
|------|--------|-----|
| logs.py | plotly/stubs, autorefresh, dataframe types | Install stubs, add type ignores |
| metrics.py | plotly stubs, date/datetime, unused vars | Install stubs, fix types |
| overview.py | Dict values, dataframe types | Add generics |
| settings.py | Dict unknown, unused functions/vars | Add types, remove unused |
| manual_actions.py | All imports unused | Remove or use

---

## Phase 4: Test Files (COSMETIC - LOWEST PRIORITY)

### 4.1 tests/conftest.py
| Line | Issue | Fix |
|------|-------|-----|
| 41 | Fixture return type | Use @pytest.fixture with proper return type |
| 44 | Deprecated get_event_loop_policy | Use asyncio.get_event_loop_policy() |
| 68, 71 | Missing type annotations | Add types to fixture params |
| 82-104 | Settings constructor params | Update to match actual Settings class |
| 322, 345, 382 | List/tuple without args | Add generics |
| 447, 507, 514, 521, 522, 579, 605, 612, 619, 626, 633, 640, 647, 659-667 | Missing param types | Add type annotations |
| 539, 542, 543, 545, 538, 552-554, 557, 560, 562-564, 569, 579, 590, 608, 615, 622, 629, 636, 643, 650, 682 | Unknown types | Add proper mock types |
| 7, 16, 26-31, 117, 123, 129, 135, 141, 147, 153, 163, 170, 248, 255, 262, 269, 276, 349, 525 | Unused imports/obscured | Clean up

### 4.2 All Integration/Unit Test Files
- Add type annotations to all @pytest.fixture parameters
- Fix mock client type mismatches (use Protocol or base class)
- Remove unused imports
- Fix AsyncMock/MagicMock type annotations

---

## Phase 5: Third-Party Stubs (QUICK WIN)

pip install types-feedparser types-passlib plotly-stubs

# For streamlit_autorefresh - may need to ignore or create stub

---

## Phase 6: Tooling Configuration

### 6.1 pyproject.toml - Add pyright config
[tool.pyright]
reportMissingTypeStubs = false
reportUnknownParameterType = false
reportUnknownMemberType = false
reportUnknownVariableType = false
reportUnknownArgumentType = false
reportUnusedImport = warning
reportUnusedVariable = warning

### 6.2 .pylanceignore (if needed)
# Ignore test files for stricter checking
tests/

---

## Execution Order & Time Estimates

| Phase | Files | Est. Time | Priority |
|-------|-------|-----------|----------|
| 5. Stubs | 1 command | 2 min | Quick Win |
| 1. Core Types | 15 files | 45 min | High |
| 2. Repo/Service | 20 files | 60 min | Medium |
| 6. Tooling | 1 file | 5 min | Quick Win |
| 3. Presentation | 10 files | 30 min | Low |
| 4. Tests | 40+ files | 2+ hours | Cosmetic |

Total: ~4 hours for complete fix, ~1 hour for high-impact only

---

## Verification Commands

# After each phase, verify:
pyright                          # Check remaining errors
pytest tests/ -x -q              # Ensure tests still pass
python -m infostitch.cli run --dry-run  # Smoke test

---

## Notes

1. Dont fix test files first - theyre cosmetic and time-consuming
2. Use # type: ignore[code] sparingly for known-safe patterns
3. Prefer Protocol classes for mock compatibility
4. Run tests after each file to catch regressions
5. Focus on production code - tests/dashboard are lower priority

---

## Success Criteria

- [ ] pyright shows 0 errors on src/ (warnings OK)
- [ ] All 446 tests still pass
- [ ] CLI runs without errors
- [ ] Dashboard starts without errors
