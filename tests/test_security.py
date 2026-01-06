import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSecurityHeaders:
    """Test security headers are present on responses."""

    async def test_root_endpoint_security_headers(self, client: AsyncClient):
        """Test security headers on root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200
        headers = response.headers

        # Check all security headers are present
        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") == "DENY"
        assert headers.get("x-xss-protection") == "1; mode=block"
        assert "strict-transport-security" in headers
        assert "content-security-policy" in headers
        assert "referrer-policy" in headers
        assert "permissions-policy" in headers

    async def test_tasks_endpoint_security_headers(self, client: AsyncClient):
        """Test security headers on tasks endpoint."""
        response = await client.get("/api/v1/tasks/")

        assert response.status_code == 200
        headers = response.headers

        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") == "DENY"
        assert headers.get("x-xss-protection") == "1; mode=block"

    async def test_task_creation_security_headers(self, client: AsyncClient):
        """Test security headers on task creation."""
        response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Security Test Task"}
        )

        assert response.status_code == 201
        headers = response.headers

        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") == "DENY"

    async def test_security_headers_on_error(self, client: AsyncClient):
        """Test security headers are present even on error responses."""
        response = await client.get("/api/v1/tasks/99999")

        assert response.status_code == 404
        headers = response.headers

        # Security headers should still be present
        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") == "DENY"

    async def test_content_security_policy_header(self, client: AsyncClient):
        """Test Content-Security-Policy header format."""
        response = await client.get("/")

        csp = response.headers.get("content-security-policy", "")

        # Should contain default directives
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "style-src 'self'" in csp

    async def test_strict_transport_security(self, client: AsyncClient):
        """Test Strict-Transport-Security header."""
        response = await client.get("/")

        hsts = response.headers.get("strict-transport-security", "")

        # Should have max-age and includeSubDomains
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    async def test_permissions_policy(self, client: AsyncClient):
        """Test Permissions-Policy header."""
        response = await client.get("/")

        permissions = response.headers.get("permissions-policy", "")

        # Should disable geolocation and microphone
        assert "geolocation=()" in permissions
        assert "microphone=()" in permissions

    async def test_referrer_policy(self, client: AsyncClient):
        """Test Referrer-Policy header."""
        response = await client.get("/")

        referrer = response.headers.get("referrer-policy", "")

        # Should be strict-origin-when-cross-origin
        assert "strict-origin-when-cross-origin" in referrer


@pytest.mark.asyncio
class TestCORSHeaders:
    """Test CORS headers configuration."""

    async def test_cors_headers_on_get_request(self, client: AsyncClient):
        """Test CORS headers are present on GET request."""
        response = await client.get(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.status_code == 200
        headers = response.headers

        # Check CORS headers
        assert "access-control-allow-origin" in headers
        assert headers["access-control-allow-origin"] in [
            "http://localhost:3000",
            "*"
        ]

    async def test_cors_options_request(self, client: AsyncClient):
        """Test CORS preflight request handling."""
        response = await client.options(
            "/api/v1/tasks/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        # Should return 200 with CORS headers
        assert response.status_code in [200, 204]

    async def test_cors_allow_methods(self, client: AsyncClient):
        """Test CORS allows correct methods."""
        response = await client.options(
            "/api/v1/tasks/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )

        assert response.status_code in [200, 204]
        headers = response.headers

        # Should allow common HTTP methods
        allow_methods = headers.get("access-control-allow-methods", "")
        allowed_methods = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]

        for method in allowed_methods:
            assert method in allow_methods

    async def test_cors_allow_headers(self, client: AsyncClient):
        """Test CORS allows correct headers."""
        response = await client.options(
            "/api/v1/tasks/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization"
            }
        )

        assert response.status_code in [200, 204]
        headers = response.headers

        allow_headers = headers.get("access-control-allow-headers", "")
        expected_headers = [
            "Accept",
            "Content-Type",
            "Authorization",
            "X-Requested-With"
        ]

        for header in expected_headers:
            # Case-insensitive check
            assert header.lower() in allow_headers.lower()

    async def test_cors_credentials(self, client: AsyncClient):
        """Test CORS allows credentials."""
        response = await client.get(
            "/api/v1/tasks/",
            headers={"Origin": "http://localhost:3000"}
        )

        headers = response.headers
        allow_credentials = headers.get("access-control-allow-credentials")

        # Should allow credentials
        assert allow_credentials == "true"

    async def test_cors_max_age(self, client: AsyncClient):
        """Test CORS max-age header."""
        response = await client.options(
            "/api/v1/tasks/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )

        headers = response.headers
        max_age = headers.get("access-control-max-age")

        # Should have a max-age value (usually in seconds)
        assert max_age is not None
        # Convert to int and verify it's reasonable
        max_age_int = int(max_age)
        assert max_age_int > 0


@pytest.mark.asyncio
class TestSecurityBestPractices:
    """Test security best practices are followed."""

    async def test_no_sensitive_data_in_errors(self, client: AsyncClient):
        """Test error messages don't leak sensitive information."""
        response = await client.get("/api/v1/tasks/99999")

        assert response.status_code == 404
        data = response.json()

        # Should not contain database queries, stack traces, etc.
        assert "SELECT" not in str(data)
        assert "database" not in str(data).lower()
        assert "traceback" not in str(data).lower()

    async def test_proper_content_type(self, client: AsyncClient):
        """Test API returns proper content type."""
        response = await client.get("/api/v1/tasks/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    async def test_json_payload_validation(self, client: AsyncClient):
        """Test API validates JSON payloads."""
        response = await client.post(
            "/api/v1/tasks/",
            json={"invalid_field": "value"}
        )

        # Should reject invalid fields through validation
        # Either 422 for validation errors or 201 if extra fields ignored
        assert response.status_code in [201, 422]

    async def test_reject_invalid_content_type(self, client: AsyncClient):
        """Test API rejects requests with invalid content type."""
        # Try sending text/plain instead of application/json
        response = await client.post(
            "/api/v1/tasks/",
            content="invalid data",
            headers={"Content-Type": "text/plain"}
        )

        # Should reject with 422 Unprocessable Entity
        assert response.status_code == 422
