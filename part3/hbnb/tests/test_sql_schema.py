"""
Tests - SQL Schema Integrity
Uses Flask app context + SQLAlchemy ORM to avoid all table naming issues.
"""
import unittest
import uuid
from hbnb.app import create_app, db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
 
 
def uid():
    return str(uuid.uuid4())
 
 
def get_admin(session):
    """
    Récupère l'admin DIRECTEMENT dans la session courante.
    Ne pas utiliser facade.get_user_by_email() ici — retourne des objets
    détachés dont l'id n'est pas reconnu par SQLite avec PRAGMA foreign_keys=ON.
    """
    from hbnb.app.models.user import User
    return session.query(User).filter_by(email="admin@hbnb.io").first()
 
 
class TestSQLSchema(unittest.TestCase):
 
    def setUp(self):
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
 
    def tearDown(self):
        db.session.remove()
        self.ctx.pop()
 
    # ------------------------------------------------------------------
    # Tables
    # ------------------------------------------------------------------
 
    def test_all_tables_exist(self):
        """All required tables exist."""
        inspector = db.inspect(db.engine)
        tables = {t.lower() for t in inspector.get_table_names()}
        for t in ["users", "places", "reviews", "amenities", "place_amenity"]:
            self.assertIn(t.lower(), tables,
                          f"Table '{t}' missing. Found: {tables}")
 
    # ------------------------------------------------------------------
    # Initial data
    # ------------------------------------------------------------------
 
    def test_admin_user_exists(self):
        """Admin user admin@hbnb.io is present and is_admin=1."""
        admin = get_admin(db.session)
        self.assertIsNotNone(admin, "Admin user not found")
        self.assertTrue(admin.is_admin)
 
    def test_admin_password_is_bcrypt(self):
        """Admin password stored as bcrypt hash ($2b$)."""
        admin = get_admin(db.session)
        self.assertIsNotNone(admin)
        self.assertTrue(admin.password.startswith("$2b$"),
                        "Password not bcrypt hashed")
 
    def test_amenities_count(self):
        """At least 3 amenities are present."""
        from hbnb.app.models.amenity import Amenity
        count = db.session.query(Amenity).count()
        self.assertGreaterEqual(count, 3, "Expected at least 3 amenities")
 
    # ------------------------------------------------------------------
    # Constraints via raw SQL
    # ------------------------------------------------------------------
 
    def test_unique_email_constraint(self):
        """Inserting duplicate email raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            with db.engine.begin() as conn:
                conn.execute(text("PRAGMA foreign_keys = ON"))
                conn.execute(text(
                    "INSERT INTO users "
                    "(id, first_name, last_name, email, password, is_admin, "
                    "created_at, updated_at) "
                    "VALUES (:id, 'Dup', 'User', 'admin@hbnb.io', 'x', 0, "
                    "datetime('now'), datetime('now'))"
                ), {"id": uid()})
 
    def test_review_rating_check_too_high(self):
        """Rating > 5 raises IntegrityError."""
        with db.engine.connect() as conn:
            user  = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
            place = conn.execute(text("SELECT id FROM places LIMIT 1")).fetchone()
        if not user or not place:
            self.skipTest("No users or places in DB")
        with self.assertRaises(IntegrityError):
            with db.engine.begin() as conn:
                conn.execute(text(
                    "INSERT INTO reviews "
                    "(id, text, rating, user_id, place_id, created_at, updated_at) "
                    "VALUES (:id, 'Bad', 6, :uid, :pid, "
                    "datetime('now'), datetime('now'))"
                ), {"id": uid(), "uid": user[0], "pid": place[0]})
 
    def test_review_rating_check_too_low(self):
        """Rating < 1 raises IntegrityError."""
        with db.engine.connect() as conn:
            user  = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
            place = conn.execute(text("SELECT id FROM places LIMIT 1")).fetchone()
        if not user or not place:
            self.skipTest("No users or places in DB")
        with self.assertRaises(IntegrityError):
            with db.engine.begin() as conn:
                conn.execute(text(
                    "INSERT INTO reviews "
                    "(id, text, rating, user_id, place_id, created_at, updated_at) "
                    "VALUES (:id, 'Bad', 0, :uid, :pid, "
                    "datetime('now'), datetime('now'))"
                ), {"id": uid(), "uid": user[0], "pid": place[0]})
 
    def test_foreign_key_place_references_user(self):
        """Place.owner_id must reference a valid user (FK)."""
        with self.assertRaises(IntegrityError):
            with db.engine.begin() as conn:
                conn.execute(text("PRAGMA foreign_keys = ON"))
                conn.execute(text(
                    "INSERT INTO places "
                    "(id, title, price, latitude, longitude, owner_id, "
                    "created_at, updated_at) "
                    "VALUES (:id, 'Orphan', 50, 0, 0, 'no-such-user', "
                    "datetime('now'), datetime('now'))"
                ), {"id": uid()})
 
    # ------------------------------------------------------------------
    # Cascade deletes via ORM
    # ------------------------------------------------------------------
 
    def test_cascade_delete_reviews_with_place(self):
        """Deleting a place via ORM cascades to its reviews."""
        from hbnb.app.models.place import Place
        from hbnb.app.models.review import Review
 
        # Récupérer l'admin dans la session courante (pas via facade)
        admin = get_admin(db.session)
        self.assertIsNotNone(admin, "Admin user must exist")
 
        place = Place(
            title=f"Cascade {uid()[:8]}",
            description="test", price=50,
            latitude=45.0, longitude=5.0,
            owner_id=admin.id,
        )
        db.session.add(place)
        db.session.flush()
 
        review = Review(
            text="Will cascade", rating=4,
            user_id=admin.id, place_id=place.id,
        )
        db.session.add(review)
        db.session.commit()
 
        review_id = review.id
 
        db.session.delete(place)
        db.session.commit()
 
        deleted = db.session.get(Review, review_id)
        self.assertIsNone(deleted, "Review should be cascade deleted with place")
 
    def test_cascade_delete_place_amenity_with_place(self):
        """Deleting a place via ORM cascades to place_amenity entries."""
        from hbnb.app.models.place import Place
        from hbnb.app.models.amenity import Amenity
 
        # Récupérer admin et amenity dans la session courante (pas via facade)
        admin = get_admin(db.session)
        self.assertIsNotNone(admin, "Admin user must exist")
 
        amenity = db.session.query(Amenity).first()
        if amenity is None:
            self.skipTest("No amenities in DB")
 
        place = Place(
            title=f"PA Cascade {uid()[:8]}",
            description="test", price=50,
            latitude=45.0, longitude=5.0,
            owner_id=admin.id,
        )
        db.session.add(place)
        db.session.flush()
 
        place.amenities.append(amenity)
        db.session.commit()
 
        place_id = place.id
 
        # Vérifier que l'association existe
        with db.engine.connect() as conn:
            count_before = conn.execute(text(
                "SELECT COUNT(*) FROM place_amenity WHERE place_id=:pid"
            ), {"pid": place_id}).fetchone()[0]
        self.assertGreater(count_before, 0,
                           "Amenity should be linked to place before deletion")
 
        # Supprimer le place → doit cascader sur place_amenity
        db.session.delete(place)
        db.session.commit()
 
        with db.engine.connect() as conn:
            count_after = conn.execute(text(
                "SELECT COUNT(*) FROM place_amenity WHERE place_id=:pid"
            ), {"pid": place_id}).fetchone()[0]
        self.assertEqual(count_after, 0,
                         "place_amenity should be cascade deleted with place")
 
 
if __name__ == "__main__":
    unittest.main(verbosity=2)
    