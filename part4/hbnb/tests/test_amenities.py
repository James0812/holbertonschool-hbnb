"""
Amenity endpoint tests.
"""
import unittest
import uuid
from hbnb.app import create_app


class TestAmenityEndpoints(unittest.TestCase):

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

        # Suffixe unique pour éviter UNIQUE constraint
        self.uid = str(uuid.uuid4())[:8]

    def test_create_amenity_valid(self):
        """Admin can create an amenity."""
        response = self.client.post("/api/v1/amenities/", json={
            "name": f"Amenity {self.uid}"
        }, headers=self.auth)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)

    def test_create_amenity_invalid(self):
        """Empty name should return 400."""
        response = self.client.post("/api/v1/amenities/", json={
            "name": ""
        }, headers=self.auth)
        self.assertEqual(response.status_code, 400)

    def test_create_amenity_no_token(self):
        """Without token should return 401."""
        response = self.client.post("/api/v1/amenities/", json={
            "name": f"NoToken {self.uid}"
        })
        self.assertEqual(response.status_code, 401)

    def test_get_amenities(self):
        """GET /amenities/ is public and returns 200."""
        response = self.client.get("/api/v1/amenities/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_create_amenity_non_admin(self):
        """Non-admin user should get 403."""
        uid = str(uuid.uuid4())[:8]
        self.client.post("/api/v1/users/", json={
            "first_name": "Normal",
            "last_name": "User",
            "email": f"normal_{uid}@example.com",
            "password": "pass123"
        }, headers=self.auth)

        login = self.client.post("/api/v1/auth/login", json={
            "email": f"normal_{uid}@example.com",
            "password": "pass123"
        })
        user_token = login.json.get("access_token", "")

        response = self.client.post("/api/v1/amenities/", json={
            "name": f"Forbidden {uid}"
        }, headers={"Authorization": f"Bearer {user_token}"})
        self.assertEqual(response.status_code, 403)
