"""
Tests - RBAC (Role-Based Access Control)
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestRBAC(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.admin_auth = {"Authorization": f"Bearer {login.json.get('access_token', '')}"}

        uid = unique()
        self.user_email = f"rbac_{uid}@example.com"
        self.client.post("/api/v1/users/", json={
            "first_name": "RBAC", "last_name": "User",
            "email": self.user_email, "password": "pass123"
        }, headers=self.admin_auth)
        user_login = self.client.post("/api/v1/auth/login", json={
            "email": self.user_email, "password": "pass123"
        })
        self.user_auth = {"Authorization": f"Bearer {user_login.json.get('access_token', '')}"}

    def test_admin_can_create_user(self):
        resp = self.client.post("/api/v1/users/", json={
            "first_name": "New", "last_name": "User",
            "email": f"{unique()}@example.com", "password": "pass"
        }, headers=self.admin_auth)
        self.assertEqual(resp.status_code, 201)

    def test_non_admin_cannot_create_user(self):
        resp = self.client.post("/api/v1/users/", json={
            "first_name": "A", "last_name": "B",
            "email": f"{unique()}@example.com", "password": "pass"
        }, headers=self.user_auth)
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_create_amenity(self):
        resp = self.client.post("/api/v1/amenities/", json={
            "name": f"Admin Amenity {unique()}"
        }, headers=self.admin_auth)
        self.assertEqual(resp.status_code, 201)

    def test_non_admin_cannot_create_amenity(self):
        resp = self.client.post("/api/v1/amenities/", json={
            "name": f"User Amenity {unique()}"
        }, headers=self.user_auth)
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_update_any_user(self):
        uid = unique()
        create = self.client.post("/api/v1/users/", json={
            "first_name": "Target", "last_name": "User",
            "email": f"target_{uid}@example.com", "password": "pass"
        }, headers=self.admin_auth)
        user_id = create.json.get("id")

        resp = self.client.put(f"/api/v1/users/{user_id}", json={
            "first_name": "AdminUpdated"
        }, headers=self.admin_auth)
        self.assertEqual(resp.status_code, 200)

    def test_user_cannot_update_another_user(self):
        uid = unique()
        create = self.client.post("/api/v1/users/", json={
            "first_name": "Other", "last_name": "User",
            "email": f"other_{uid}@example.com", "password": "pass"
        }, headers=self.admin_auth)
        other_id = create.json.get("id")

        resp = self.client.put(f"/api/v1/users/{other_id}", json={
            "first_name": "Hacked"
        }, headers=self.user_auth)
        self.assertEqual(resp.status_code, 403)

    def test_user_cannot_modify_email(self):
        from hbnb.app.services import facade
        with self.app.app_context():
            user = facade.get_user_by_email(self.user_email)
            user_id = user.id

        resp = self.client.put(f"/api/v1/users/{user_id}", json={
            "email": "hacked@example.com"
        }, headers=self.user_auth)
        self.assertEqual(resp.status_code, 400)

    def test_user_cannot_modify_password(self):
        from hbnb.app.services import facade
        with self.app.app_context():
            user = facade.get_user_by_email(self.user_email)
            user_id = user.id

        resp = self.client.put(f"/api/v1/users/{user_id}", json={
            "password": "newpassword"
        }, headers=self.user_auth)
        self.assertEqual(resp.status_code, 400)

    def test_admin_can_update_amenity(self):
        uid = unique()
        create = self.client.post("/api/v1/amenities/", json={
            "name": f"To Update {uid}"
        }, headers=self.admin_auth)
        amenity_id = create.json.get("id")

        resp = self.client.put(f"/api/v1/amenities/{amenity_id}", json={
            "name": f"Updated {uid}"
        }, headers=self.admin_auth)
        self.assertEqual(resp.status_code, 200)

    def test_admin_bypasses_place_ownership(self):
        """Admin can update a place they don't own → 200."""
        uid = unique()
        place_resp = self.client.post("/api/v1/places/", json={
            "title": f"User Place {uid}", "description": "test",
            "price": 50, "latitude": 45.0, "longitude": 5.0
        }, headers=self.user_auth)
        place_id = place_resp.json.get("id")

        # ✅ FIX: owner_id requis par place_update_model
        resp = self.client.put(f"/api/v1/places/{place_id}", json={
            "title": f"Admin Updated {uid}",
            "owner_id": "placeholder"
        }, headers=self.admin_auth)
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
