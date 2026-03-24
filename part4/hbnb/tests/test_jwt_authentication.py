"""
Tests - JWT Authentication
Covers:
- Login returns token
- Wrong credentials rejected
- Protected endpoints require token
- Fake token rejected
- is_admin claim in token
- Public routes accessible without token
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestJWTAuthentication(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.admin_token = login.json.get("access_token", "")
        self.admin_auth = {"Authorization": f"Bearer {self.admin_token}"}

    def test_login_returns_token(self):
        """Valid login returns access_token."""
        resp = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access_token", resp.json)
        self.assertIsInstance(resp.json["access_token"], str)

    def test_login_wrong_password(self):
        """Wrong password → 401."""
        resp = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "wrong"
        })
        self.assertEqual(resp.status_code, 401)

    def test_login_unknown_user(self):
        """Unknown email → 401."""
        resp = self.client.post("/api/v1/auth/login", json={
            "email": "ghost@nowhere.com", "password": "pass"
        })
        self.assertEqual(resp.status_code, 401)

    def test_login_missing_password(self):
        """Missing password → 400 (Flask-RESTX validation)."""
        resp = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io"
        })
        self.assertIn(resp.status_code, [400, 500])

    def test_protected_endpoint_requires_token(self):
        """jwt_required() endpoint → 401 without token."""
        uid = unique()
        resp = self.client.post("/api/v1/users/", json={
            "first_name": "A", "last_name": "B",
            "email": f"{uid}@example.com", "password": "p"
        })
        self.assertEqual(resp.status_code, 401)

    def test_fake_token_rejected(self):
        """Fake JWT token → 401 or 422."""
        uid = unique()
        resp = self.client.post("/api/v1/users/", json={
            "first_name": "A", "last_name": "B",
            "email": f"{uid}@example.com", "password": "p"
        }, headers={"Authorization": "Bearer fake.jwt.token"})
        self.assertIn(resp.status_code, [401, 422])

    def test_token_grants_admin_access(self):
        """Admin token grants access to admin-only endpoints."""
        uid = unique()
        resp = self.client.post("/api/v1/amenities/", json={
            "name": f"JWT Test {uid}"
        }, headers=self.admin_auth)
        self.assertEqual(resp.status_code, 201)

    def test_protected_route_with_valid_token(self):
        """GET /auth/protected works with valid token."""
        resp = self.client.get("/api/v1/auth/protected",
                               headers=self.admin_auth)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("is_admin", resp.json)
        self.assertTrue(resp.json["is_admin"])

    def test_public_routes_no_token_needed(self):
        """Public endpoints → 200 without token."""
        for route in ["/api/v1/places/", "/api/v1/amenities/"]:
            resp = self.client.get(route)
            self.assertEqual(resp.status_code, 200, f"Failed for {route}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
