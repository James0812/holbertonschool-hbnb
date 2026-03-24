"""
User endpoint tests.
"""
import unittest
import uuid
from hbnb.app import create_app


class TestUserEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Login admin
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io",
            "password": "admin1234"
        })
        self.token = login.json.get("access_token", "")
        self.auth = {"Authorization": f"Bearer {self.token}"}

        # Suffixe unique par test
        self.uid = str(uuid.uuid4())[:8]

    def test_create_user_valid(self):
        """Admin can create a user."""
        response = self.client.post("/api/v1/users/", json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": f"alice_{self.uid}@example.com",
            "password": "pass123"   # ✅ password requis
        }, headers=self.auth)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)

    def test_create_user_no_token(self):
        """Without token should return 401."""
        response = self.client.post("/api/v1/users/", json={
            "first_name": "No",
            "last_name": "Token",
            "email": f"notoken_{self.uid}@example.com",
            "password": "pass123"
        })
        self.assertEqual(response.status_code, 401)

    def test_create_user_missing_password(self):
        """User creation without password should fail with 400."""
        response = self.client.post("/api/v1/users/", json={
            "first_name": "Bob",
            "last_name": "Brown",
            "email": f"bob_{self.uid}@example.com"
            # password manquant
        }, headers=self.auth)
        self.assertEqual(response.status_code, 400)

    def test_get_users(self):
        """GET /users/ should return 200 and a list."""
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_user_not_found(self):
        """GET /users/<invalid-id> should return 404."""
        response = self.client.get("/api/v1/users/invalid-id")
        self.assertEqual(response.status_code, 404)

    def test_create_duplicate_email(self):
        """Creating user with existing email should return 400."""
        data = {
            "first_name": "Dup",
            "last_name": "User",
            "email": f"dup_{self.uid}@example.com",
            "password": "pass123"
        }
        self.client.post("/api/v1/users/", json=data, headers=self.auth)
        response = self.client.post("/api/v1/users/", json=data,
                                    headers=self.auth)
        self.assertEqual(response.status_code, 400)

    def test_non_admin_cannot_create_user(self):
        """Non-admin user cannot create users → 403."""
        uid2 = str(uuid.uuid4())[:8]
        # Créer un user normal
        self.client.post("/api/v1/users/", json={
            "first_name": "Normal",
            "last_name": "User",
            "email": f"normal_{self.uid}@example.com",
            "password": "pass123"
        }, headers=self.auth)
        login = self.client.post("/api/v1/auth/login", json={
            "email": f"normal_{self.uid}@example.com",
            "password": "pass123"
        })
        user_token = login.json.get("access_token", "")

        response = self.client.post("/api/v1/users/", json={
            "first_name": "New",
            "last_name": "User",
            "email": f"new_{uid2}@example.com",
            "password": "pass123"
        }, headers={"Authorization": f"Bearer {user_token}"})
        self.assertEqual(response.status_code, 403)
