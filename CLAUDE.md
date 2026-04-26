# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WebP Editor is a Django web application for image editing and conversion focused on the WebP format. Django 6.0+ on Python 3.13, with a vanilla JS frontend using TailwindCSS/Flowbite/ToastUI. Deployed on Fly.io via Docker with Daphne ASGI server.

## Commands

### Development
```bash
uv venv && source .venv/bin/activate && uv sync   # Setup Python environment
pnpm install                                        # Install frontend dependencies
python manage.py runserver                          # Start dev server
pnpm run update-css                                 # TailwindCSS watch mode
```

### Testing
```bash
nox                                    # Full test suite with coverage (uses Python 3.13, uv backend)
coverage run -m pytest                 # Run tests with coverage directly
coverage report -m                     # View coverage report
```

Pytest is configured in `pyproject.toml`: test discovery looks for `main.py` files in `tests/` (not the default `test_*.py` pattern). Tests are registered as unittest TestCases loaded through `tests/main.py`.

### Code Quality
```bash
ruff check --fix          # Lint with auto-fix
ruff format               # Format code
isort .                   # Sort imports
basedpyright              # Type checking (strict mode)
```

Pre-commit hooks run: isort, ruff check+format, and uv sync/lock/export automatically.

### Database
```bash
python manage.py makemigrations      # Generate migrations
python manage.py migrate             # Apply migrations
```

Migrations live in `infrastructure/database/migrations/`. The migration module is remapped: `MIGRATION_MODULES = {"infrastructure": "infrastructure.database.migrations"}`.

## Architecture

### Clean Architecture Layers

The codebase follows strict layered architecture with dependency inversion:

- **`domain/`** - Pure domain models and constants. No framework dependencies.
- **`application/`** - Business logic organized as Commands (write) and Queries (read) following CQRS. Contains validators, services, and abstract interfaces (`abc/` subdirectories).
- **`infrastructure/`** - Django ORM models, repository implementations, Cloudinary integration, background jobs. Models are in `infrastructure/database/models/`, repositories in `infrastructure/repositories/`.
- **`api/`** - REST API layer using Django Ninja Extra. Controllers, middleware, authentication. Registered via `NinjaExtraAPI` in `api/urls.py`.
- **`views/`** - Django template-based views (class-based views for web pages).
- **`core/`** - Cross-cutting concerns: logging (loguru-based), result monad (`core/result/context_result.py`), abstract base classes.

### Dependency Injection (AnyDI)

Three DI modules loaded in order in `settings.py` under `ANYDI["MODULES"]`:
1. `CoreModule` (core/di.py) - Logger (singleton)
2. `InfrastructureModule` (infrastructure/di.py) - Repositories, Cloudinary client
3. `ApplicationModule` (application/di.py) - Services, commands, queries (request-scoped)

`PATCH_NINJA=True` enables automatic injection into Django Ninja endpoints. Dependencies are resolved by type with `Annotated[InterfaceType, ImplName]` for disambiguation when multiple implementations exist for the same interface.

### Naming Conventions

- `*ABC` suffix for abstract base classes
- `*Command` for state-mutating operations, `*Query` for read-only
- `*Service` for business logic, `*Repository` for data access
- `*Controller` for API endpoints
- Private attributes use Python name mangling (`__attribute`)
- Concrete classes use `@final` decorator
- Immutable attributes use `Final[Type]`
- Pydantic schemas use `ConfigDict(frozen=True, strict=True, extra="forbid")`

### Configuration

- Environment selected via `DJANGO_ENVIRONMENT` env var ("Development", "Staging", "Production")
- Env files: `.env.dev`, `.env.staging`, `.env.production`
- Ruff targets Python 3.14, Pyright targets 3.13
- Line length: 140 characters
- Ruff rules: E4, E7, E9, F, B, S (ignores E501, B008, S324)

### URL Structure

- `/admin/` - Django admin (django-unfold)
- `/api/` - REST API (Django Ninja Extra)
- `/converter/` - Image converter web UI
- `/about/`, `/contact/` - Static pages
- Catch-all `re_path` routes to content-not-found view
