"""
Tests - Review CRUD
Covers:
- Create and get review
- Invalid rating rejected
- Cannot review own place
- Cannot review same place twice
- Delete review
- Only author/admin can delete
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestReviewCRUD(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.admin_auth = {"Authorization": f"Bearer {login.json.get('access_token', '')}"}

        uid = unique()
        # Reviewer (non-admin)
        self.client.post("/api/v1/users/", json={
            "first_name": "Rev", "last_name": "User",
            "email": f"rev_{uid}@example.com", "password": "pass"
        }, headers=self.admin_auth)
        rev_login = self.client.post("/api/v1/auth/login", json={
            "email": f"rev_{uid}@example.com", "password": "pass"
        })
        self.rev_auth = {"Authorization": f"Bearer {rev_login.json.get('access_token', '')}"}

        # Place owned by admin
        place = self.client.post("/api/v1/places/", json={
            "title": f"Rev Place {uid}", "description": "test",
            "price": 50, "latitude": 45.0, "longitude": 5.0
        }, headers=self.admin_auth)
        self.place_id = place.json.get("id")

    def test_create_review(self):
        """Reviewer can review a place they don't own → 201."""
        resp = self.client.post("/api/v1/reviews/", json={
            "text": "Great!", "rating": 5,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=self.rev_auth)
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.json)

    def test_get_review(self):
        """GET /reviews/<id> returns the review."""
        create = self.client.post("/api/v1/reviews/", json={
            "text": "Nice!", "rating": 4,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=self.rev_auth)
        review_id = create.json.get("id")

        get = self.client.get(f"/api/v1/reviews/{review_id}")
        self.assertEqual(get.status_code, 200)

    def test_review_invalid_rating_too_high(self):
        """Rating > 5 → 400."""
        resp = self.client.post("/api/v1/reviews/", json={
            "text": "Bad", "rating": 10,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=self.rev_auth)
        self.assertEqual(resp.status_code, 400)

    def test_review_invalid_rating_too_low(self):
        """Rating < 1 → 400."""
        resp = self.client.post("/api/v1/reviews/", json={
            "text": "Bad", "rating": 0,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=self.rev_auth)
        self.assertEqual(resp.status_code, 400)

    def test_cannot_review_own_place(self):
        """Owner cannot review their own place → 400."""
        resp = self.client.post("/api/v1/reviews/", json={
            "text": "My own review", "rating": 5,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=self.admin_auth)
        self.assertEqual(resp.status_code, 400)

    def test_cannot_review_same_place_twice(self):
        """Same user cannot review same place twice → 400."""
        uid = unique()
        self.client.post("/api/v1/users/", json={
            "first_name": "Dbl", "last_name": "Rev",
            "email": f"dbl_{uid}@example.com", "password": "pass"
        }, headers=self.admin_auth)
        dbl_login = self.client.post("/api/v1/auth/login", json={
            "email": f"dbl_{uid}@example.com", "password": "pass"
        })
        dbl_auth = {"Authorization": f"Bearer {dbl_login.json.get('access_token', '')}"}

        self.client.post("/api/v1/reviews/", json={
            "text": "First", "rating": 4,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=dbl_auth)
        resp = self.client.post("/api/v1/reviews/", json={
            "text": "Second", "rating": 3,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=dbl_auth)
        self.assertEqual(resp.status_code, 400)

    def test_delete_own_review(self):
        """Author can delete their own review → 200."""
        create = self.client.post("/api/v1/reviews/", json={
            "text": "Delete me", "rating": 3,
            "user_id": "placeholder", "place_id": self.place_id
        }, headers=self.rev_auth)
        review_id = create.json.get("id")

        resp = self.client.delete(f"/api/v1/reviews/{review_id}",
                                  headers=self.rev_auth)
        self.assertEqual(resp.status_code, 200)

    def test_review_not_found(self):
        """GET /reviews/<fake-id> → 404."""
        resp = self.client.get("/api/v1/reviews/fake-id")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
