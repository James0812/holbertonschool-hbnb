"""
Place model tests.
"""
import unittest
from hbnb.app.models.place import Place
from hbnb.app.models.user import User
from hbnb.app.models.review import Review
from hbnb.app.models.amenity import Amenity


class TestPlaceModel(unittest.TestCase):

    def setUp(self):
        """Create a user used as owner for places."""
        self.owner = User(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            password="pass123"   # ✅ FIX: password manquant dans l'original
        )

    def test_create_place_valid(self):
        """Test valid place creation."""
        place = Place(
            title="Cozy Apartment",
            description="Nice place",
            price=120,
            latitude=45.0,
            longitude=5.0,
            owner_id=self.owner.id   # ✅ FIX: owner_id au lieu de owner=
        )
        self.assertEqual(place.title, "Cozy Apartment")
        self.assertEqual(place.price, 120)
        self.assertEqual(place.owner_id, self.owner.id)

    def test_place_invalid_price(self):
        """Price cannot be negative."""
        with self.assertRaises(ValueError):
            Place(
                title="Bad Place",
                description="Invalid price",
                price=-10,
                latitude=45.0,
                longitude=5.0,
                owner_id=self.owner.id
            )

    def test_place_invalid_latitude(self):
        """Latitude must be between -90 and 90."""
        with self.assertRaises(ValueError):
            Place(
                title="Bad Latitude",
                description="Invalid",
                price=50,
                latitude=100,
                longitude=5,
                owner_id=self.owner.id
            )

    def test_place_invalid_longitude(self):
        """Longitude must be between -180 and 180."""
        with self.assertRaises(ValueError):
            Place(
                title="Bad Longitude",
                description="Invalid",
                price=50,
                latitude=45,
                longitude=200,
                owner_id=self.owner.id
            )

    def test_place_title_too_long(self):
        """Title must not exceed 255 characters."""
        with self.assertRaises(ValueError):
            Place(
                title="A" * 256,
                description="Too long",
                price=50,
                latitude=45,
                longitude=5,
                owner_id=self.owner.id
            )
