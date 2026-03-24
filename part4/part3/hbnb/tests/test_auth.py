"""
Authentication & JWT token tests.
"""
import unittest
import uuid
from hbnb.app import create_app


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io",
            "password": "admin1234"
        })
        self.admin_token = login.json.get("access_token", "")
        self.admin_auth = {"Authorization": f"Bearer {self.admin_token}"}

        # User normal pour les tests (email unique)
        uid = str(uuid.uuid4())[:8]
        self.test_email = f"auth_{uid}@example.com"
        self.client.post("/api/v1/users/", json={
            "first_name": "Auth",
            "last_name": "Tester",
            "email": self.test_email,
            "password": "mypass123"
        }, headers=self.admin_auth)

    # ==================================================
    # LOGIN
    # ==================================================

    def test_login_valid(self):
        """Valid credentials return a JWT token."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io",
            "password": "admin1234"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json)

    def test_login_wrong_password(self):
        """Wrong password should return 401."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io",
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, 401)

    def test_login_unknown_email(self):
        """Unknown email should return 401."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "ghost@example.com",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, 401)

    def test_login_missing_password(self):
        """Missing password field should return 400 (validation error)."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io"
            # password manquant → Flask-RESTX retourne 400
        })
        self.assertEqual(response.status_code, 400)

    # ==================================================
    # TOKEN
    # ==================================================

    def test_token_required_on_protected_route(self):
        """Creating user without token returns 401."""
        uid = str(uuid.uuid4())[:8]
        response = self.client.post("/api/v1/users/", json={
            "first_name": "No",
            "last_name": "Token",
            "email": f"notoken_{uid}@example.com",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_rejected(self):
        """Fake token on a JWT-protected route should return 401/422."""
        uid = str(uuid.uuid4())[:8]
        # POST /users/ est protégé par jwt_required()
        response = self.client.post("/api/v1/users/", json={
            "first_name": "Fake",
            "last_name": "Token",
            "email": f"fake_{uid}@example.com",
            "password": "pass123"
        }, headers={"Authorization": "Bearer fake.token.here"})
        self.assertIn(response.status_code, [401, 422])

    def test_admin_token_has_admin_access(self):
        """Admin token can create amenities."""
        uid = str(uuid.uuid4())[:8]
        response = self.client.post("/api/v1/amenities/", json={
            "name": f"Auth Amenity {uid}"
        }, headers=self.admin_auth)
        self.assertEqual(response.status_code, 201)

    def test_normal_user_token_denied_admin_route(self):
        """Normal user token cannot create amenities → 403."""
        login = self.client.post("/api/v1/auth/login", json={
            "email": self.test_email,
            "password": "mypass123"
        })
        token = login.json.get("access_token", "")
        uid = str(uuid.uuid4())[:8]

        response = self.client.post("/api/v1/amenities/", json={
            "name": f"Forbidden {uid}"
        }, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 403)

    def test_public_route_no_token_needed(self):
        """Public routes accessible without token."""
        response = self.client.get("/api/v1/places/")
        self.assertEqual(response.status_code, 200)

    def test_protected_route_accessible_with_token(self):
        """Protected route accessible with valid token."""
        response = self.client.get("/api/v1/auth/protected",
                                   headers=self.admin_auth)
        self.assertEqual(response.status_code, 200)
