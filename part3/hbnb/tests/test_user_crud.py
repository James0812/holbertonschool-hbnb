"""
Tests - User CRUD
Covers:
- Create and retrieve user
- Update user
- Duplicate email rejected
- Non-existent user returns 404
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestUserCRUD(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.auth = {"Authorization": f"Bearer {login.json.get('access_token', '')}"}

    def test_create_user(self):
        """POST /users/ creates user and returns 201."""
        resp = self.client.post("/api/v1/users/", json={
            "first_name": "Test", "last_name": "User",
            "email": f"{unique()}@example.com", "password": "pass123"
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.json)

    def test_get_user(self):
        """GET /users/<id> returns correct user."""
        uid = unique()
        email = f"{uid}@example.com"
        create = self.client.post("/api/v1/users/", json={
            "first_name": "Get", "last_name": "Me",
            "email": email, "password": "pass"
        }, headers=self.auth)
        user_id = create.json.get("id")

        get = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(get.status_code, 200)
        self.assertEqual(get.json["email"], email)

    def test_get_all_users(self):
        """GET /users/ returns a list."""
        resp = self.client.get("/api/v1/users/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json, list)

    def test_update_user(self):
        """PUT /users/<id> updates user fields."""
        uid = unique()
        create = self.client.post("/api/v1/users/", json={
            "first_name": "Before", "last_name": "Update",
            "email": f"{uid}@example.com", "password": "pass"
        }, headers=self.auth)
        user_id = create.json.get("id")

        resp = self.client.put(f"/api/v1/users/{user_id}", json={
            "first_name": "After"
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["first_name"], "After")

    def test_duplicate_email_rejected(self):
        """Creating user with existing email → 400."""
        uid = unique()
        data = {"first_name": "A", "last_name": "B",
                "email": f"{uid}@example.com", "password": "p"}
        self.client.post("/api/v1/users/", json=data, headers=self.auth)
        resp = self.client.post("/api/v1/users/", json=data, headers=self.auth)
        self.assertEqual(resp.status_code, 400)

    def test_get_nonexistent_user(self):
        """GET /users/<invalid-id> → 404."""
        resp = self.client.get("/api/v1/users/nonexistent-id")
        self.assertEqual(resp.status_code, 404)

    def test_create_user_missing_password(self):
        """POST /users/ without password → 400."""
        resp = self.client.post("/api/v1/users/", json={
            "first_name": "No", "last_name": "Pass",
            "email": f"{unique()}@example.com"
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
