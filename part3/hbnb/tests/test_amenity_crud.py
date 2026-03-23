"""
Tests - Amenity CRUD
Covers:
- Admin creates/updates amenity
- Non-admin cannot create amenity
- Get amenity by ID
- Not found returns 404
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestAmenityCRUD(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.auth = {"Authorization": f"Bearer {login.json.get('access_token', '')}"}

        # Normal user
        uid = unique()
        self.client.post("/api/v1/users/", json={
            "first_name": "Normal", "last_name": "User",
            "email": f"normal_{uid}@example.com", "password": "pass"
        }, headers=self.auth)
        user_login = self.client.post("/api/v1/auth/login", json={
            "email": f"normal_{uid}@example.com", "password": "pass"
        })
        self.user_auth = {"Authorization": f"Bearer {user_login.json.get('access_token', '')}"}

    def test_create_amenity(self):
        """Admin creates amenity → 201."""
        resp = self.client.post("/api/v1/amenities/", json={
            "name": f"Amenity {unique()}"
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.json)

    def test_get_amenity(self):
        """GET /amenities/<id> returns correct amenity."""
        uid = unique()
        create = self.client.post("/api/v1/amenities/", json={
            "name": f"Get Me {uid}"
        }, headers=self.auth)
        amenity_id = create.json.get("id")

        get = self.client.get(f"/api/v1/amenities/{amenity_id}")
        self.assertEqual(get.status_code, 200)
        self.assertEqual(get.json["name"], f"Get Me {uid}")

    def test_get_all_amenities(self):
        """GET /amenities/ returns a list."""
        resp = self.client.get("/api/v1/amenities/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json, list)

    def test_update_amenity(self):
        """Admin updates amenity → 200."""
        uid = unique()
        create = self.client.post("/api/v1/amenities/", json={
            "name": f"Old {uid}"
        }, headers=self.auth)
        amenity_id = create.json.get("id")

        resp = self.client.put(f"/api/v1/amenities/{amenity_id}", json={
            "name": f"New {uid}"
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["name"], f"New {uid}")

    def test_non_admin_cannot_create_amenity(self):
        """Non-admin cannot create amenity → 403."""
        resp = self.client.post("/api/v1/amenities/", json={
            "name": f"Forbidden {unique()}"
        }, headers=self.user_auth)
        self.assertEqual(resp.status_code, 403)

    def test_create_amenity_no_token(self):
        """No token → 401."""
        resp = self.client.post("/api/v1/amenities/", json={
            "name": f"NoToken {unique()}"
        })
        self.assertEqual(resp.status_code, 401)

    def test_amenity_not_found(self):
        """GET /amenities/<fake-id> → 404."""
        resp = self.client.get("/api/v1/amenities/fake-id")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
