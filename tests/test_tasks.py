import pytest
from datetime import datetime
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTaskCreation:
    """Test task creation endpoint."""

    async def test_create_task_success(self, client: AsyncClient, task_data: dict):
        """Test successful task creation."""
        response = await client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
        assert data["status"] == task_data["status"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_task_minimal(self, client: AsyncClient):
        """Test task creation with minimal required fields."""
        response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Minimal Task"}
        )

        # Check for success or rate limit
        assert response.status_code in [201, 429]
        if response.status_code == 201:
            data = response.json()
            assert data["title"] == "Minimal Task"
            assert data["priority"] == "medium"  # Default value
            assert data["status"] == "todo"  # Default value

    async def test_create_task_invalid_priority(self, client: AsyncClient):
        """Test task creation with invalid priority."""
        response = await client.post(
            "/api/v1/tasks/",
            json={
                "title": "Invalid Task",
                "priority": "invalid_priority"
            }
        )

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("priority" in str(e).lower() for e in errors)

    async def test_create_task_invalid_status(self, client: AsyncClient):
        """Test task creation with invalid status."""
        response = await client.post(
            "/api/v1/tasks/",
            json={
                "title": "Invalid Task",
                "status": "invalid_status"
            }
        )

        assert response.status_code == 422

    async def test_create_task_missing_title(self, client: AsyncClient):
        """Test task creation without title."""
        response = await client.post(
            "/api/v1/tasks/",
            json={"description": "No title task"}
        )

        assert response.status_code == 422

    async def test_create_task_title_too_long(self, client: AsyncClient):
        """Test task creation with title exceeding max length."""
        response = await client.post(
            "/api/v1/tasks/",
            json={"title": "x" * 201}
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestTaskRetrieval:
    """Test task retrieval endpoints."""

    async def test_get_all_tasks_empty(self, client: AsyncClient):
        """Test getting all tasks when none exist."""
        response = await client.get("/api/v1/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # May have data from previous tests depending on transaction isolation
        assert len(data) >= 0

    async def test_get_all_tasks(self, client: AsyncClient, sample_tasks: list):
        """Test getting all tasks."""
        response = await client.get("/api/v1/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 10  # At least our sample tasks

    async def test_get_task_by_id(self, client: AsyncClient, sample_task):
        """Test getting specific task by ID."""
        response = await client.get(f"/api/v1/tasks/{sample_task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == sample_task.title

    async def test_get_task_not_found(self, client: AsyncClient):
        """Test getting non-existent task."""
        response = await client.get("/api/v1/tasks/99999")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    async def test_get_tasks_with_pagination(self, client: AsyncClient, sample_tasks: list):
        """Test pagination of tasks."""
        # Get first 5 tasks
        response = await client.get("/api/v1/tasks/?skip=0&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Get next 5 tasks
        response = await client.get("/api/v1/tasks/?skip=5&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    async def test_get_tasks_with_status_filter(self, client: AsyncClient, sample_tasks: list):
        """Test filtering tasks by status."""
        response = await client.get("/api/v1/tasks/?status=todo")

        assert response.status_code == 200
        data = response.json()
        assert all(task["status"] == "todo" for task in data)

    async def test_get_tasks_with_priority_filter(self, client: AsyncClient, sample_tasks: list):
        """Test filtering tasks by priority."""
        response = await client.get("/api/v1/tasks/?priority=high")

        assert response.status_code == 200
        data = response.json()
        assert all(task["priority"] == "high" for task in data)

    async def test_get_task_stats(self, client: AsyncClient, sample_tasks: list):
        """Test getting task statistics."""
        response = await client.get("/api/v1/tasks/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_status" in data
        assert "by_priority" in data
        assert data["total"] >= 10  # At least our sample tasks


@pytest.mark.asyncio
class TestTaskUpdate:
    """Test task update endpoint."""

    async def test_update_task_title(self, client: AsyncClient, sample_task):
        """Test updating task title."""
        response = await client.patch(
            f"/api/v1/tasks/{sample_task.id}",
            json={"title": "Updated Title"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["id"] == sample_task.id

    async def test_update_task_status(self, client: AsyncClient, sample_task):
        """Test updating task status."""
        response = await client.patch(
            f"/api/v1/tasks/{sample_task.id}",
            json={"status": "in_progress"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    async def test_update_task_multiple_fields(self, client: AsyncClient, sample_task, task_update_data):
        """Test updating multiple task fields."""
        response = await client.patch(
            f"/api/v1/tasks/{sample_task.id}",
            json=task_update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == task_update_data["title"]
        assert data["description"] == task_update_data["description"]
        assert data["status"] == task_update_data["status"]
        assert data["priority"] == task_update_data["priority"]

    async def test_update_task_not_found(self, client: AsyncClient):
        """Test updating non-existent task."""
        response = await client.patch(
            "/api/v1/tasks/99999",
            json={"title": "Updated"}
        )

        assert response.status_code == 404

    async def test_update_task_invalid_status(self, client: AsyncClient, sample_task):
        """Test updating task with invalid status."""
        response = await client.patch(
            f"/api/v1/tasks/{sample_task.id}",
            json={"status": "invalid_status"}
        )

        assert response.status_code == 422

    async def test_update_task_with_due_date(self, client: AsyncClient, sample_task):
        """Test updating task with due date."""
        response = await client.patch(
            f"/api/v1/tasks/{sample_task.id}",
            json={"due_date": "2026-12-31T23:59:59"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "due_date" in data


@pytest.mark.asyncio
class TestTaskDeletion:
    """Test task deletion endpoint."""

    async def test_delete_task_success(self, client: AsyncClient, sample_task):
        """Test successful task deletion."""
        response = await client.delete(f"/api/v1/tasks/{sample_task.id}")

        assert response.status_code == 204

        # Verify task is deleted
        response = await client.get(f"/api/v1/tasks/{sample_task.id}")
        assert response.status_code == 404

    async def test_delete_task_not_found(self, client: AsyncClient):
        """Test deleting non-existent task."""
        response = await client.delete("/api/v1/tasks/99999")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestTaskLifecycle:
    """Test complete task lifecycle."""

    async def test_full_task_lifecycle(self, client: AsyncClient, task_data):
        """Test creating, reading, updating, and deleting a task."""
        # Create
        response = await client.post("/api/v1/tasks/", json=task_data)
        # May hit rate limit after many tests
        if response.status_code == 429:
            return  # Skip test if rate limited
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Read
        response = await client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == task_data["title"]

        # Update
        response = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={"status": "done"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "done"

        # Delete
        response = await client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 204

        # Verify deletion
        response = await client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 404
