"""
Tests - Entity Relationships (SQLAlchemy)
Covers:
- Place → Reviews (one-to-many)
- Place → Amenities (many-to-many)
- Place → owner_id (foreign key to User)
- Add/remove amenity from place
- GET /places/<id>/reviews
- GET /places/<id>/amenities
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestEntityRelationships(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Admin
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.admin_auth = {"Authorization": f"Bearer {login.json.get('access_token', '')}"}

        # Normal user (place owner)
        uid = unique()
        self.client.post("/api/v1/users/", json={
            "first_name": "Rel", "last_name": "User",
            "email": f"rel_{uid}@example.com", "password": "pass"
        }, headers=self.admin_auth)
        rel_login = self.client.post("/api/v1/auth/login", json={
            "email": f"rel_{uid}@example.com", "password": "pass"
        })
        self.user_auth = {"Authorization": f"Bearer {rel_login.json.get('access_token', '')}"}

        # Place owned by user
        place = self.client.post("/api/v1/places/", json={
            "title": f"Rel Place {uid}", "description": "test",
            "price": 80, "latitude": 43.0, "longitude": 5.0
        }, headers=self.user_auth)
        self.place_id = place.json.get("id")

        # Amenity created by admin
        amenity = self.client.post("/api/v1/amenities/", json={
            "name": f"Rel Amenity {uid}"
        }, headers=self.admin_auth)
        self.amenity_id = amenity.json.get("id")
        self.amenity_name = f"Rel Amenity {uid}"

    def test_place_has_owner_id(self):
        """Place response includes owner_id."""
        resp = self.client.get(f"/api/v1/places/{self.place_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("owner_id", resp.json)
        self.assertIsNotNone(resp.json["owner_id"])

    def test_place_has_reviews(self):
        """GET /places/<id>/reviews returns reviews for that place."""
        self.client.post("/api/v1/reviews/", json={
            "text": "Lovely!", "rating": 5,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=self.admin_auth)

        resp = self.client.get(f"/api/v1/places/{self.place_id}/reviews")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json, list)
        self.assertGreater(len(resp.json), 0)

    def test_place_reviews_empty_initially(self):
        """New place has no reviews."""
        uid = unique()
        place = self.client.post("/api/v1/places/", json={
            "title": f"Empty {uid}", "description": "test",
            "price": 50, "latitude": 45.0, "longitude": 5.0
        }, headers=self.user_auth)
        place_id = place.json.get("id")

        resp = self.client.get(f"/api/v1/places/{place_id}/reviews")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [])

    def test_add_amenity_to_place(self):
        """Owner can add amenity to place → 200."""
        resp = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers=self.user_auth
        )
        self.assertEqual(resp.status_code, 200)

    def test_place_amenity_visible_in_get(self):
        """Added amenity appears in GET /places/<id>/amenities."""
        self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers=self.user_auth
        )
        resp = self.client.get(f"/api/v1/places/{self.place_id}/amenities")
        self.assertEqual(resp.status_code, 200)
        ids = [a["id"] for a in resp.json]
        self.assertIn(self.amenity_id, ids)

    def test_place_amenities_empty_initially(self):
        """New place has no amenities."""
        uid = unique()
        place = self.client.post("/api/v1/places/", json={
            "title": f"No Amenity {uid}", "description": "test",
            "price": 50, "latitude": 45.0, "longitude": 5.0
        }, headers=self.user_auth)
        place_id = place.json.get("id")

        resp = self.client.get(f"/api/v1/places/{place_id}/amenities")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, [])

    def test_remove_amenity_from_place(self):
        """Owner can remove amenity from place → 200."""
        self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers=self.user_auth
        )
        resp = self.client.delete(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers=self.user_auth
        )
        self.assertEqual(resp.status_code, 200)

    def test_cannot_add_amenity_without_token(self):
        """Adding amenity without token → 401."""
        resp = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}"
        )
        self.assertEqual(resp.status_code, 401)

    def test_non_owner_cannot_add_amenity(self):
        """Non-owner cannot add amenity to place → 403."""
        uid = unique()
        self.client.post("/api/v1/users/", json={
            "first_name": "Other", "last_name": "User",
            "email": f"other_rel_{uid}@example.com", "password": "pass"
        }, headers=self.admin_auth)
        other_login = self.client.post("/api/v1/auth/login", json={
            "email": f"other_rel_{uid}@example.com", "password": "pass"
        })
        other_auth = {"Authorization": f"Bearer {other_login.json.get('access_token', '')}"}

        resp = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers=other_auth
        )
        self.assertEqual(resp.status_code, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
