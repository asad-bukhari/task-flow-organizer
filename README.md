# Task Management API

A production-ready task management REST API built with FastAPI, SQLModel, and Neon PostgreSQL featuring rate limiting, security headers, and comprehensive test coverage.

## ✨ Features

### Core Functionality
- ✅ Create, read, update, and delete tasks
- 📖 Pagination support for large datasets
- 🔍 Filter tasks by status and priority
- 📊 Task statistics endpoint
- 🚀 Full async/await for high performance

### Security & Performance
- 🔒 Comprehensive security headers
- 🛡️ Rate limiting on all endpoints
- 🌐 Configurable CORS policies
- ⚡ Async database operations
- ✅ 55 tests with full coverage

## 📋 Task Fields

- `id`: Auto-generated unique identifier
- `title`: Task title (required, 1-200 characters)
- `description`: Task description (optional, max 2000 characters)
- `priority`: Task priority (low, medium, high) - default: medium
- `status`: Task status (todo, in_progress, done, cancelled) - default: todo
- `due_date`: Optional due date (ISO 8601 format)
- `created_at`: Auto-generated timestamp
- `updated_at`: Auto-generated timestamp

## 🏗️ Architecture

The project follows a clean, layered architecture:

```
┌─────────────────────────────────────────┐
│         API Layer (FastAPI)             │
│  HTTP request/response handling         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│       Service Layer (Business Logic)    │
│  Validation, orchestration, rules       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Repository Layer (Data Access)       │
│  Database queries, transactions         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Database (Neon PostgreSQL)         │
│  Persistent storage                     │
└─────────────────────────────────────────┘
```

### Project Structure

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
│   │   └── task.py                   # SQLModel models & schemas
│   ├── repositories/
│   │   └── task_repository.py        # Data access layer
│   ├── services/
│   │   └── task_service.py           # Business logic layer
│   └── main.py                       # FastAPI app setup
├── tests/
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_tasks.py                 # CRUD tests (23 tests)
│   ├── test_security.py              # Security tests (14 tests)
│   └── test_rate_limiting.py         # Rate limiting tests (13 tests)
├── .env                              # Environment variables (gitignored)
├── .env.example                      # Example environment file
├── pyproject.toml                    # Dependencies & project config
├── pytest.ini                        # Test configuration
├── main.py                           # Application entry point
├── CLAUDE.md                         # AI development guide
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Neon PostgreSQL database (get free account at https://neon.tech)
- uv package manager (recommended) or pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd task-managment
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Neon database URL:
   ```env
   DATABASE_URL=postgresql://username:password@ep-xyz.region.aws.neon.tech/neondb
   ```

4. **Run the application**
   ```bash
   # Using uvicorn with hot reload
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Or using the entry point
   python main.py
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Interactive docs (Swagger): http://localhost:8000/docs
   - Alternative docs (ReDoc): http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

## 🧪 Testing

The project includes comprehensive tests with 55 test cases covering all functionality.

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_tasks.py -v

# Run with coverage report
uv run pytest tests/ --cov=app --cov-report=html

# Run tests in parallel (faster)
uv run pytest tests/ -n auto
```

**Test Coverage:**
- ✅ CRUD operations (23 tests)
- ✅ Security headers (7 tests)
- ✅ CORS configuration (7 tests)
- ✅ Rate limiting (13 tests)
- ✅ Input validation
- ✅ Error handling

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Tasks

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| POST | `/tasks/` | 20/min | Create a new task |
| GET | `/tasks/` | 100/min | Get all tasks with pagination and filtering |
| GET | `/tasks/stats` | 50/min | Get task statistics |
| GET | `/tasks/{task_id}` | 100/min | Get a specific task by ID |
| PATCH | `/tasks/{task_id}` | 30/min | Update a task |
| DELETE | `/tasks/{task_id}` | 20/min | Delete a task |

#### System

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| GET | `/` | 100/min | Root endpoint with API info |
| GET | `/health` | 200/min | Health check endpoint |

### Query Parameters (GET /tasks/)

| Parameter | Type | Default | Limits | Description |
|-----------|------|---------|--------|-------------|
| `skip` | integer | 0 | - | Number of tasks to skip (pagination) |
| `limit` | integer | 100 | 1-100 | Maximum number of tasks to return |
| `status` | string | - | todo, in_progress, done, cancelled | Filter by status |
| `priority` | string | - | low, medium, high | Filter by priority |

### Example: Get Tasks with Filters

```bash
GET /api/v1/tasks/?status=todo&priority=high&skip=0&limit=10
```

## 💡 Usage Examples

### Create a Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation with examples",
    "priority": "high",
    "status": "todo",
    "due_date": "2026-01-31T23:59:59"
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation with examples",
  "priority": "high",
  "status": "todo",
  "due_date": "2026-01-31T23:59:59",
  "created_at": "2026-01-07T10:30:00",
  "updated_at": "2026-01-07T10:30:00"
}
```

### Get All Tasks

```bash
curl "http://localhost:8000/api/v1/tasks/"
```

### Get Tasks with Filtering

```bash
# Get high-priority todo tasks
curl "http://localhost:8000/api/v1/tasks/?status=todo&priority=high&limit=10"

# Pagination: Get second page
curl "http://localhost:8000/api/v1/tasks/?skip=10&limit=10"
```

### Get Task Statistics

```bash
curl "http://localhost:8000/api/v1/tasks/stats"
```

**Response:**
```json
{
  "total": 42,
  "by_status": {
    "todo": 15,
    "in_progress": 12,
    "done": 10,
    "cancelled": 5
  },
  "by_priority": {
    "low": 10,
    "medium": 20,
    "high": 12
  }
}
```

### Update a Task

```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "high"
  }'
```

### Delete a Task

```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

**Response (204 No Content)**

## 🔒 Security Features

### Security Headers

All API responses include comprehensive security headers:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

### CORS Configuration

- **Allowed Origins**: Configurable (default: localhost:3000, localhost:8000)
- **Allowed Methods**: GET, POST, PATCH, DELETE, OPTIONS
- **Allowed Headers**: Content-Type, Authorization, X-Requested-With
- **Credentials**: Supported
- **Max Age**: 600 seconds (10 minutes)

### Rate Limiting

IP-based rate limiting is applied to all endpoints:

| Endpoint | Limit |
|----------|-------|
| POST /tasks | 20/minute |
| GET /tasks | 100/minute |
| GET /tasks/{id} | 100/minute |
| PATCH /tasks/{id} | 30/minute |
| DELETE /tasks/{id} | 20/minute |
| GET /tasks/stats | 50/minute |
| GET /health | 200/minute |

**Rate Limit Response (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded"
}
```

## 🛠️ Development

### Adding New Features

1. **Define Models** (`app/models/`)
   - Create SQLModel classes
   - Define Create, Update, Read schemas
   - Add field validators if needed

2. **Create Repository** (`app/repositories/`)
   - Implement data access methods
   - Handle database queries
   - Manage transactions

3. **Create Service** (`app/services/`)
   - Implement business logic
   - Validate data
   - Orchestrate repository calls

4. **Create Endpoints** (`app/api/v1/endpoints/`)
   - Define route handlers
   - Apply rate limiting
   - Handle request/response

5. **Register Routes** (`app/api/v1/router.py`)
   - Include new router
   - Set prefix and tags

6. **Write Tests** (`tests/`)
   - Test CRUD operations
   - Test validation
   - Test error handling

### Code Style

- Use async/await for all I/O operations
- Follow Repository → Service → Endpoint pattern
- Type hints required on all functions
- Docstrings on all public functions
- Tests for all new features

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@ep-xyz.region.aws.neon.tech/dbname

# API Configuration (optional - defaults provided)
API_V1_STR=/api/v1
PROJECT_NAME=Task Management API
VERSION=1.0.0

# CORS (optional - defaults provided)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
ALLOW_CREDENTIALS=true
CORS_MAX_AGE=600
```

## 📦 Dependencies

### Core Dependencies
- **fastapi** (0.115.0): Modern web framework
- **uvicorn[standard]** (0.32.1): ASGI server
- **sqlmodel** (0.0.22): ORM (Pydantic + SQLAlchemy)
- **asyncpg** (0.29.0): PostgreSQL async driver
- **pydantic-settings** (2.6.1): Configuration management
- **slowapi** (0.1.9): Rate limiting

### Development Dependencies
- **pytest** (9.0.2): Testing framework
- **pytest-asyncio** (1.3.0): Async test support
- **httpx** (0.28.1): Async HTTP client for testing
- **aiosqlite** (0.20.0): Async SQLite for tests

## 🐛 Troubleshooting

### Common Issues

**"can't subtract offset-naive and offset-aware datetimes"**
- Problem: Timezone-aware datetime being stored in TIMESTAMP WITHOUT TIME ZONE column
- Solution: Field validators in TaskCreate/TaskUpdate automatically strip timezone info

**Rate limit exceeded during development**
- Solution: Wait 60 seconds for rate limit to reset, or use different IP addresses

**Tests failing with database errors**
- Solution: Ensure aiosqlite is installed: `uv add aiosqlite`

**CORS errors in frontend**
- Solution: Add your frontend origin to BACKEND_CORS_ORIGINS in .env

## 🗺️ Roadmap

### Planned Features
- [ ] User authentication with JWT
- [ ] Task assignments to users
- [ ] Task comments and notes
- [ ] File attachments
- [ ] Email notifications
- [ ] WebSocket for real-time updates
- [ ] Background job queue
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] API versioning
- [ ] GraphQL endpoint
- [ ] Elasticsearch integration

### Potential Improvements
- [ ] Add database migrations (Alembic)
- [ ] Implement caching (Redis)
- [ ] Add request logging
- [ ] OpenAPI schema customization
- [ ] API documentation improvements
- [ ] Performance benchmarking
- [ ] Load testing

## 📄 License

MIT License - feel free to use this project for learning or production.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the API docs at `/docs`
- Review test files for examples

---

**Built with ❤️ using FastAPI, SQLModel, and Neon PostgreSQL**
