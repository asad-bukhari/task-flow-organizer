# Claude AI Development Guide

This document provides context and guidelines for Claude AI to assist with development of the Task Management API.

## Project Overview

**Tech Stack:**
- **Framework**: FastAPI 0.115.0
- **Database**: Neon PostgreSQL (Serverless)
- **ORM**: SQLModel (built on Pydantic + SQLAlchemy)
- **Async Runtime**: asyncio + asyncpg
- **Rate Limiting**: slowapi
- **Testing**: pytest + pytest-asyncio + httpx
- **Package Manager**: uv

**Architecture Pattern**: Repository + Service Layer with Async/Throughout

## Project Structure

```
task-managment/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── tasks.py          # API route handlers
│   │       └── router.py             # Route aggregator
│   ├── core/
│   │   ├── config.py                 # Pydantic settings
│   │   ├── database.py               # Async database connection
│   │   └── rate_limiter.py          # Rate limiter instance
│   ├── models/
│   │   └── task.py                   # SQLModel models
│   ├── repositories/
│   │   └── task_repository.py        # Data access layer
│   ├── services/
│   │   └── task_service.py           # Business logic layer
│   └── main.py                       # FastAPI app instance
├── tests/
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_tasks.py                 # CRUD tests
│   ├── test_security.py              # Security tests
│   └── test_rate_limiting.py         # Rate limiting tests
├── .env                              # Environment variables (gitignored)
├── pyproject.toml                    # Dependencies & project config
└── main.py                           # Application entry point
```

## Key Implementation Details

### Database Connection (Neon PostgreSQL)
- Uses `postgresql+asyncpg://` driver for async operations
- SSL mode parameter removed from connection string for asyncpg compatibility
- Connection pooling via SQLAlchemy's async engine
- All database operations use AsyncSession

### Rate Limiting
- IP-based rate limiting using slowapi
- Centralized limiter instance in `app/core/rate_limiter.py`
- Different limits per endpoint:
  - POST /tasks: 20/minute
  - GET /tasks: 100/minute
  - PATCH /tasks: 30/minute
  - DELETE /tasks: 20/minute
  - GET /tasks/stats: 50/minute

### Security Features
1. **Security Headers Middleware** (app/main.py):
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Strict-Transport-Security: max-age=31536000
   - Content-Security-Policy: default-src 'self'
   - Referrer-Policy: strict-origin-when-cross-origin
   - Permissions-Policy: geolocation=(), microphone=()

2. **CORS Configuration**:
   - Restrictive methods: GET, POST, PATCH, DELETE, OPTIONS
   - Specific allowed headers
   - Credential support enabled
   - Configurable origins via settings

### Timezone Handling
- **Critical**: Frontend sends timezone-aware datetimes
- Database column is TIMESTAMP WITHOUT TIME ZONE
- Pydantic field validators strip timezone info before storage
- Located in `app/models/task.py` TaskCreate and TaskUpdate models

## Testing Guidelines

### Test Database
- Uses in-memory SQLite (`sqlite+aiosqlite:///:memory:`)
- Fast test execution with complete isolation
- Async fixtures with proper session management

### Running Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_tasks.py -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### Test Organization
- **test_tasks.py**: CRUD operations, pagination, filtering
- **test_security.py**: Headers, CORS, security best practices
- **test_rate_limiting.py**: Rate limit verification

## Common Development Tasks

### Adding a New Model
1. Create model in `app/models/`
2. Define Create, Update, Read schemas
3. Add field validators if needed (e.g., datetime handling)
4. Create repository in `app/repositories/`
5. Create service in `app/services/`
6. Create endpoints in `app/api/v1/endpoints/`
7. Add route to `app/api/v1/router.py`
8. Write tests

### Modifying Existing Features
1. Update models/schemas in `app/models/`
2. Update repository methods
3. Update service methods
4. Update endpoints if needed
5. Update or add tests
6. Run tests: `uv run pytest tests/ -v`

### Database Migration
Currently using SQLModel's automatic table creation via `init_db()`.
For production migrations, consider adding Alembic.

## Dependencies Management

### Adding Dependencies
```bash
# Add new package
uv add package-name

# Add dev dependency
uv add --dev package-name
```

### Key Dependencies
- fastapi: Web framework
- uvicorn[standard]: ASGI server
- sqlmodel: ORM (Pydantic + SQLAlchemy)
- asyncpg: PostgreSQL async driver
- pydantic-settings: Configuration management
- slowapi: Rate limiting
- pytest: Testing framework
- pytest-asyncio: Async test support
- httpx: Async HTTP client for testing
- aiosqlite: Async SQLite for tests

## Configuration

### Environment Variables (.env)
```env
DATABASE_URL=postgresql://user:pass@ep-xyz.region.aws.neon.tech/dbname
```

### Settings (app/core/config.py)
- API_V1_STR: API prefix (default: /api/v1)
- PROJECT_NAME: Project name
- VERSION: API version
- BACKEND_CORS_ORIGINS: Allowed CORS origins
- ALLOW_CREDENTIALS: CORS credentials support
- CORS_MAX_AGE: CORS preflight cache duration

## Troubleshooting

### Common Issues

1. **"can't subtract offset-naive and offset-aware datetimes"**
   - Frontend sending timezone-aware datetimes
   - Solution: Field validators in TaskCreate/TaskUpdate strip timezone

2. **"connect() got an unexpected keyword argument 'sslmode'"**
   - asyncpg doesn't accept sslmode in connection string
   - Solution: Database URL cleaning in database.py

3. **Rate limiter conflicts**
   - Multiple Limiter instances with different key_func
   - Solution: Use centralized limiter from rate_limiter.py

4. **Tests failing with rate limit errors**
   - Tests share rate limiter state
   - Solution: Rate limiter reset fixture in conftest.py

## API Endpoints Reference

### Tasks
- `POST /api/v1/tasks/` - Create task (20/min)
- `GET /api/v1/tasks/` - List tasks (100/min)
  - Query: skip, limit, status, priority
- `GET /api/v1/tasks/stats` - Statistics (50/min)
- `GET /api/v1/tasks/{id}` - Get task (100/min)
- `PATCH /api/v1/tasks/{id}` - Update task (30/min)
- `DELETE /api/v1/tasks/{id}` - Delete task (20/min)

### System
- `GET /` - Root endpoint (100/min)
- `GET /health` - Health check (200/min)

## Development Workflow

1. **Install dependencies**: `uv sync`
2. **Configure environment**: Copy `.env.example` to `.env`, add DATABASE_URL
3. **Run development server**: `uv run uvicorn app.main:app --reload`
4. **Run tests**: `uv run pytest tests/ -v`
5. **Check API docs**: http://localhost:8000/docs

## Code Style Guidelines

- Use async/await for all I/O operations
- Follow Repository → Service → Endpoint pattern
- Type hints required on all functions
- Docstrings on all public functions/classes
- Tests for all new features
- Commit with clear messages

## Future Enhancements

Potential features to add:
- [ ] User authentication (JWT)
- [ ] Task assignments to users
- [ ] Task comments/notes
- [ ] File attachments
- [ ] Email notifications
- [ ] WebSocket for real-time updates
- [ ] Background job queue
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] API versioning strategy
- [ ] OpenAPI schema customization
