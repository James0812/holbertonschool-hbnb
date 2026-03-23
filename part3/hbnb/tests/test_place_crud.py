"""
Tests - Place CRUD
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestPlaceCRUD(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.auth = {"Authorization": f"Bearer {login.json.get('access_token', '')}"}

    def test_create_place(self):
        """POST /places/ creates place and returns 201."""
        resp = self.client.post("/api/v1/places/", json={
            "title": f"Place {unique()}", "description": "test",
            "price": 100, "latitude": 45.0, "longitude": 5.0
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.json)

    def test_get_place(self):
        """GET /places/<id> returns correct place."""
        uid = unique()
        create = self.client.post("/api/v1/places/", json={
            "title": f"Get Place {uid}", "description": "test",
            "price": 100, "latitude": 45.0, "longitude": 5.0
        }, headers=self.auth)
        place_id = create.json.get("id")

        get = self.client.get(f"/api/v1/places/{place_id}")
        self.assertEqual(get.status_code, 200)
        self.assertEqual(get.json["id"], place_id)

    def test_get_all_places(self):
        """GET /places/ returns a list."""
        resp = self.client.get("/api/v1/places/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json, list)

    def test_update_place(self):
        """PUT /places/<id> updates place title."""
        uid = unique()
        create = self.client.post("/api/v1/places/", json={
            "title": f"Old {uid}", "description": "test",
            "price": 50, "latitude": 45.0, "longitude": 5.0
        }, headers=self.auth)
        place_id = create.json.get("id")

        # ✅ FIX: place_update_model a owner_id required=True → l'envoyer
        resp = self.client.put(f"/api/v1/places/{place_id}", json={
            "title": f"New {uid}",
            "owner_id": "placeholder"  # requis par le modèle Flask-RESTX
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["title"], f"New {uid}")

    def test_place_invalid_price(self):
        """Negative price → 400."""
        resp = self.client.post("/api/v1/places/", json={
            "title": "Bad", "description": "bad",
            "price": -10, "latitude": 45.0, "longitude": 5.0
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 400)

    def test_place_invalid_latitude(self):
        """Latitude > 90 → 400."""
        resp = self.client.post("/api/v1/places/", json={
            "title": "Bad", "description": "bad",
            "price": 50, "latitude": 200.0, "longitude": 5.0
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 400)

    def test_place_invalid_longitude(self):
        """Longitude > 180 → 400."""
        resp = self.client.post("/api/v1/places/", json={
            "title": "Bad", "description": "bad",
            "price": 50, "latitude": 45.0, "longitude": 200.0
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 400)

    def test_place_owner_set_from_token(self):
        """owner_id in response matches authenticated user."""
        from hbnb.app.services import facade
        with self.app.app_context():
            admin = facade.get_user_by_email("admin@hbnb.io")
            admin_id = admin.id

        resp = self.client.post("/api/v1/places/", json={
            "title": f"Owner Test {unique()}", "description": "test",
            "price": 50, "latitude": 45.0, "longitude": 5.0
        }, headers=self.auth)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json.get("owner_id"), admin_id)

    def test_non_owner_cannot_update_place(self):
        """Non-owner cannot update place → 403."""
        uid = unique()
        # Créer un autre user
        self.client.post("/api/v1/users/", json={
            "first_name": "Other", "last_name": "User",
            "email": f"other_place_{uid}@example.com", "password": "pass"
        }, headers=self.auth)
        other_login = self.client.post("/api/v1/auth/login", json={
            "email": f"other_place_{uid}@example.com", "password": "pass"
        })
        other_auth = {"Authorization": f"Bearer {other_login.json.get('access_token', '')}"}

        # Admin crée une place
        create = self.client.post("/api/v1/places/", json={
            "title": f"Admin Place {uid}", "description": "test",
            "price": 50, "latitude": 45.0, "longitude": 5.0
        }, headers=self.auth)
        place_id = create.json.get("id")

        # ✅ FIX: envoyer owner_id pour passer la validation Flask-RESTX
        resp = self.client.put(f"/api/v1/places/{place_id}", json={
            "title": "Stolen",
            "owner_id": "placeholder"
        }, headers=other_auth)
        self.assertEqual(resp.status_code, 403)

    def test_get_nonexistent_place(self):
        """GET /places/<invalid-id> → 404."""
        resp = self.client.get("/api/v1/places/nonexistent-id")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
