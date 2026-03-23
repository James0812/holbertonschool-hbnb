"""
Review endpoint tests.
"""
import unittest
import uuid
from hbnb.app import create_app


class TestReviewEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Login admin
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io",
            "password": "admin1234"
        })
        self.admin_token = login.json.get("access_token", "")
        self.admin_auth = {"Authorization": f"Bearer {self.admin_token}"}

        uid = str(uuid.uuid4())[:8]

        # Créer un reviewer (user normal)
        self.client.post("/api/v1/users/", json={
            "first_name": "Reviewer",
            "last_name": "User",
            "email": f"reviewer_{uid}@example.com",
            "password": "pass123"
        }, headers=self.admin_auth)

        reviewer_login = self.client.post("/api/v1/auth/login", json={
            "email": f"reviewer_{uid}@example.com",
            "password": "pass123"
        })
        self.reviewer_token = reviewer_login.json.get("access_token", "")
        self.reviewer_auth = {"Authorization": f"Bearer {self.reviewer_token}"}

        # Admin crée une place (owned by admin, reviewer can review it)
        place_resp = self.client.post("/api/v1/places/", json={
            "title": f"Test Place {uid}",
            "description": "For review tests",
            "price": 50,
            "latitude": 45.0,
            "longitude": 10.0
        }, headers=self.admin_auth)
        self.place_id = place_resp.json.get("id")

    def test_create_review_valid(self):
        """Reviewer can review a place they don't own."""
        response = self.client.post("/api/v1/reviews/", json={
            "text": "Great stay!",
            "rating": 5,
            # ✅ user_id est requis dans le modèle Flask-RESTX même si écrasé
            "user_id": "placeholder",
            "place_id": self.place_id
        }, headers=self.reviewer_auth)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)

    def test_create_review_invalid_rating(self):
        """Rating must be between 1 and 5."""
        response = self.client.post("/api/v1/reviews/", json={
            "text": "Bad rating",
            "rating": 10,
            "user_id": "placeholder",
            "place_id": self.place_id
        }, headers=self.reviewer_auth)
        self.assertEqual(response.status_code, 400)

    def test_create_review_no_token(self):
        """Without token, Flask-RESTX validates payload first → 400 or 401."""
        response = self.client.post("/api/v1/reviews/", json={
            "text": "No auth",
            "rating": 3,
            "user_id": "placeholder",
            "place_id": self.place_id
        })
        # jwt_required() retourne 401, mais validate=True peut retourner 400
        # selon l'ordre d'exécution des décorateurs
        self.assertIn(response.status_code, [400, 401])

    def test_delete_review(self):
        """User can delete their own review."""
        # Créer la review d'abord
        review_resp = self.client.post("/api/v1/reviews/", json={
            "text": "To delete",
            "rating": 4,
            "user_id": "placeholder",
            "place_id": self.place_id
        }, headers=self.reviewer_auth)
        self.assertEqual(review_resp.status_code, 201)
        review_id = review_resp.json.get("id")

        response = self.client.delete(f"/api/v1/reviews/{review_id}",
                                      headers=self.reviewer_auth)
        self.assertEqual(response.status_code, 200)

    def test_cannot_review_own_place(self):
        """Owner cannot review their own place."""
        uid = str(uuid.uuid4())[:8]
        # Owner crée sa propre place
        self.client.post("/api/v1/users/", json={
            "first_name": "Owner",
            "last_name": "Test",
            "email": f"owner_{uid}@example.com",
            "password": "pass123"
        }, headers=self.admin_auth)
        owner_login = self.client.post("/api/v1/auth/login", json={
            "email": f"owner_{uid}@example.com",
            "password": "pass123"
        })
        owner_token = owner_login.json.get("access_token", "")
        owner_auth = {"Authorization": f"Bearer {owner_token}"}

        place_resp = self.client.post("/api/v1/places/", json={
            "title": f"My Place {uid}",
            "description": "My own place",
            "price": 100,
            "latitude": 45.0,
            "longitude": 10.0
        }, headers=owner_auth)
        own_place_id = place_resp.json.get("id")

        response = self.client.post("/api/v1/reviews/", json={
            "text": "My own review",
            "rating": 5,
            "user_id": "placeholder",
            "place_id": own_place_id
        }, headers=owner_auth)
        self.assertEqual(response.status_code, 400)

    def test_cannot_review_same_place_twice(self):
        """User cannot review same place twice."""
        uid = str(uuid.uuid4())[:8]
        # Créer un user et une place dédiés
        self.client.post("/api/v1/users/", json={
            "first_name": "Double",
            "last_name": "Reviewer",
            "email": f"double_{uid}@example.com",
            "password": "pass123"
        }, headers=self.admin_auth)
        dbl_login = self.client.post("/api/v1/auth/login", json={
            "email": f"double_{uid}@example.com",
            "password": "pass123"
        })
        dbl_token = dbl_login.json.get("access_token", "")
        dbl_auth = {"Authorization": f"Bearer {dbl_token}"}

        # Premier avis
        self.client.post("/api/v1/reviews/", json={
            "text": "First review",
            "rating": 4,
            "user_id": "placeholder",
            "place_id": self.place_id
        }, headers=dbl_auth)

        # Deuxième avis → doit échouer
        response = self.client.post("/api/v1/reviews/", json={
            "text": "Second review",
            "rating": 3,
            "user_id": "placeholder",
            "place_id": self.place_id
        }, headers=dbl_auth)
        self.assertEqual(response.status_code, 400)
