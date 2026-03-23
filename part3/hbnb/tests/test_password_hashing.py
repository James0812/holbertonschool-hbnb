"""
Tests - Password Hashing (bcrypt)
"""
import unittest
import uuid
from hbnb.app import create_app


def unique(prefix=""):
    return f"{prefix}{str(uuid.uuid4())[:8]}"


class TestPasswordHashing(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        login = self.client.post("/api/v1/auth/login", json={
            "email": "admin@hbnb.io", "password": "admin1234"
        })
        self.auth = {"Authorization": f"Bearer {login.json.get('access_token', '')}"}

    def test_post_user_hashes_password(self):
        """POST /users/ stores hashed password, not plaintext."""
        email = f"{unique('hash_')}@example.com"
        self.client.post("/api/v1/users/", json={
            "first_name": "Hash", "last_name": "User",
            "email": email, "password": "plaintext123"
        }, headers=self.auth)

        from hbnb.app.services import facade
        with self.app.app_context():
            user = facade.get_user_by_email(email)
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password, "plaintext123")
            self.assertTrue(user.password.startswith("$2b$"),
                            "Password must be bcrypt hashed")

    def test_get_user_does_not_return_password(self):
        """GET /users/<id> must not return password field."""
        email = f"{unique('nopwd_')}@example.com"
        resp = self.client.post("/api/v1/users/", json={
            "first_name": "NoPwd", "last_name": "Test",
            "email": email, "password": "secret123"
        }, headers=self.auth)
        user_id = resp.json.get("id")

        get_resp = self.client.get(f"/api/v1/users/{user_id}")
        self.assertEqual(get_resp.status_code, 200)
        self.assertNotIn("password", get_resp.json)

    def test_get_users_list_no_password(self):
        """GET /users/ must not expose password in any user."""
        resp = self.client.get("/api/v1/users/")
        self.assertEqual(resp.status_code, 200)
        for user in resp.json:
            self.assertNotIn("password", user)

    def test_verify_password_correct(self):
        """verify_password() returns True for correct password (via API)."""
        email = f"{unique('vfy_')}@example.com"
        # ✅ Créer via l'API pour que le password soit haché correctement
        self.client.post("/api/v1/users/", json={
            "first_name": "Verify", "last_name": "Me",
            "email": email, "password": "correctpass"
        }, headers=self.auth)

        from hbnb.app.services import facade
        with self.app.app_context():
            user = facade.get_user_by_email(email)
            self.assertIsNotNone(user)
            self.assertTrue(user.verify_password("correctpass"))

    def test_verify_password_wrong(self):
        """verify_password() returns False for wrong password."""
        email = f"{unique('vfy2_')}@example.com"
        # ✅ Créer via l'API pour que le password soit haché correctement
        self.client.post("/api/v1/users/", json={
            "first_name": "Verify", "last_name": "Wrong",
            "email": email, "password": "correctpass"
        }, headers=self.auth)

        from hbnb.app.services import facade
        with self.app.app_context():
            user = facade.get_user_by_email(email)
            self.assertIsNotNone(user)
            self.assertFalse(user.verify_password("wrongpass"))

    def test_login_validates_bcrypt_password(self):
        """Login endpoint correctly validates bcrypt-hashed password."""
        email = f"{unique('login_')}@example.com"
        self.client.post("/api/v1/users/", json={
            "first_name": "Login", "last_name": "Test",
            "email": email, "password": "mypassword"
        }, headers=self.auth)

        # Correct password → 200
        resp = self.client.post("/api/v1/auth/login", json={
            "email": email, "password": "mypassword"
        })
        self.assertEqual(resp.status_code, 200)

        # Wrong password → 401
        resp2 = self.client.post("/api/v1/auth/login", json={
            "email": email, "password": "wrongpassword"
        })
        self.assertEqual(resp2.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
