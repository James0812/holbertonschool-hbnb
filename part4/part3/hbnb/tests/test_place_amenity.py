"""
Place-Amenity relationship tests.
Tests adding/removing amenities to/from places.
"""
import unittest
import uuid
from hbnb.app import create_app


class TestPlaceAmenity(unittest.TestCase):

    def setUp(self):
        """Setup admin, normal user, place and amenity."""
        self.app = create_app()
        self.client = self.app.test_client()

        # Login admin
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io",
            "password": "admin1234"
        })
        self.admin_token = login.json.get("access_token", "")
        self.admin_auth = {"Authorization": f"Bearer {self.admin_token}"}

        # Suffixe unique par test pour éviter UNIQUE constraint
        uid = str(uuid.uuid4())[:8]

        # Créer un user normal (owner) avec email unique
        self.client.post("/api/v1/users/", json={
            "first_name": "Owner",
            "last_name": "Place",
            "email": f"owner_pa_{uid}@example.com",
            "password": "pass123"
        }, headers=self.admin_auth)

        owner_login = self.client.post("/api/v1/auth/login", json={
            "email": f"owner_pa_{uid}@example.com",
            "password": "pass123"
        })
        self.owner_token = owner_login.json.get("access_token", "")
        self.owner_auth = {"Authorization": f"Bearer {self.owner_token}"}

        # Owner crée une place
        place_resp = self.client.post("/api/v1/places/", json={
            "title": f"Amenity Test Place {uid}",
            "description": "For amenity tests",
            "price": 80,
            "latitude": 43.3,
            "longitude": 5.4
        }, headers=self.owner_auth)
        self.place_id = place_resp.json.get("id")

        # Admin crée une amenity avec nom unique
        amenity_resp = self.client.post("/api/v1/amenities/", json={
            "name": f"Test Pool {uid}"
        }, headers=self.admin_auth)
        self.amenity_id = amenity_resp.json.get("id")
        self.amenity_name = f"Test Pool {uid}"

        # Admin crée une 2e amenity avec nom unique
        uid2 = str(uuid.uuid4())[:8]
        amenity2_resp = self.client.post("/api/v1/amenities/", json={
            "name": f"Test Sauna {uid2}"
        }, headers=self.admin_auth)
        self.amenity2_id = amenity2_resp.json.get("id")

    def test_add_amenity_to_place_as_owner(self):
        """Owner can add an amenity to their place."""
        response = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers=self.owner_auth
        )
        self.assertEqual(response.status_code, 200)

    def test_add_amenity_to_place_as_admin(self):
        """Admin can add an amenity to any place."""
        response = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity2_id}",
            headers=self.admin_auth
        )
        self.assertEqual(response.status_code, 200)

    def test_add_amenity_no_token(self):
        """Without token should return 401."""
        response = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}"
        )
        self.assertEqual(response.status_code, 401)

    def test_add_amenity_wrong_user(self):
        """Non-owner cannot add amenity to someone else's place."""
        uid = str(uuid.uuid4())[:8]
        self.client.post("/api/v1/users/", json={
            "first_name": "Other",
            "last_name": "User",
            "email": f"other_pa_{uid}@example.com",
            "password": "pass123"
        }, headers=self.admin_auth)
        other_login = self.client.post("/api/v1/auth/login", json={
            "email": f"other_pa_{uid}@example.com",
            "password": "pass123"
        })
        other_token = other_login.json.get("access_token", "")

        response = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        self.assertEqual(response.status_code, 403)

    def test_add_nonexistent_amenity(self):
        """Adding a non-existent amenity should return 404."""
        response = self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/fake-amenity-id",
            headers=self.owner_auth
        )
        self.assertEqual(response.status_code, 404)

    def test_add_amenity_nonexistent_place(self):
        """Adding amenity to a non-existent place should return 404."""
        response = self.client.post(
            f"/api/v1/places/fake-place-id/amenities/{self.amenity_id}",
            headers=self.owner_auth
        )
        self.assertEqual(response.status_code, 404)

    def test_get_place_amenities(self):
        """GET /places/<id>/amenities returns list with added amenity."""
        self.client.post(
            f"/api/v1/places/{self.place_id}/amenities/{self.amenity_id}",
            headers=self.owner_auth
        )
        response = self.client.get(
            f"/api/v1/places/{self.place_id}/amenities"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        names = [a["name"] for a in response.json]
        self.assertIn(self.amenity_name, names)

    def test_get_amenities_empty_place(self):
        """New place has no amenities."""
        uid = str(uuid.uuid4())[:8]
        place_resp = self.client.post("/api/v1/places/", json={
            "title": f"Empty Place {uid}",
            "description": "No amenities",
            "price": 50,
            "latitude": 40.0,
            "longitude": 2.0
        }, headers=self.owner_auth)
        empty_place_id = place_resp.json.get("id")

        response = self.client.get(
            f"/api/v1/places/{empty_place_id}/amenities"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])
