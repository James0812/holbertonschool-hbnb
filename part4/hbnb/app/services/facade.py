"""
Facade layer connecting API and business logic.
Supports both in-memory and database persistence.
"""
import os
from hbnb.app.models import User, Place, Review, Amenity
from sqlalchemy.exc import IntegrityError

# ---------------------------------------------
# STORAGE MODE
# ---------------------------------------------
# SQL PAR DÉFAUT
USE_DATABASE = os.getenv('USE_DATABASE', 'true').lower() == 'true'

if USE_DATABASE:
    from hbnb.app.persistence.repository import SQLAlchemyRepository as RepositoryClass
    print("Using SQLAlchemy Repository")
else:
    from hbnb.app.persistence.repository import InMemoryRepository as RepositoryClass
    print("Using InMemory Repository")


class HBnBFacade:
    def __init__(self):
        """Initialize repositories based on configuration"""
        self.user_repo = RepositoryClass(User)
        self.place_repo = RepositoryClass(Place)
        self.review_repo = RepositoryClass(Review)
        self.amenity_repo = RepositoryClass(Amenity)

    # =========================
    # UTILS
    # =========================

    def save(self):
        """Sauvegarder les changements en base"""
        if USE_DATABASE:
            from hbnb.app import db
            db.session.commit()

    # =========================
    # USER
    # =========================

    def create_user(self, user_data):
        """Create a new user with validation"""
        existing_user = self.get_user_by_email(user_data["email"])
        if existing_user:
            raise ValueError("Email already exists")
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute("email", email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, update_data):
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        user.update(update_data)
        return user

    # =========================
    # AMENITY
    # =========================

    def create_amenity(self, amenity_data):
        existing = self.amenity_repo.get_by_attribute('name', amenity_data.get('name'))
        if existing:
            raise ValueError(f"Amenity '{amenity_data['name']}' already exists")

        amenity = Amenity(**amenity_data)
        try:
            self.amenity_repo.add(amenity)
        except IntegrityError:
            if USE_DATABASE:
                from hbnb.app import db
                db.session.rollback()
            raise ValueError(f"Amenity '{amenity_data['name']}' already exists")
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, update_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            raise ValueError("Amenity not found")

        new_name = update_data.get('name')
        if new_name and new_name != amenity.name:
            existing = self.amenity_repo.get_by_attribute('name', new_name)
            if existing:
                raise ValueError(f"Amenity '{new_name}' already exists")

        try:
            amenity.update(update_data)
        except IntegrityError:
            if USE_DATABASE:
                from hbnb.app import db
                db.session.rollback()
            raise ValueError(f"Amenity '{new_name}' already exists")
        return amenity

    # =========================
    # PLACE
    # =========================

    def create_place(self, place_data):
        owner = self.user_repo.get(place_data["owner_id"])
        if not owner:
            raise ValueError("Owner not found")
        place = Place(**place_data)
        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, update_data):
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")
        place.update(update_data)
        return place

    def delete_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")

        if hasattr(place, 'reviews') and place.reviews:
            for review in place.reviews[:]:
                self.review_repo.delete(review.id)

        self.place_repo.delete(place_id)

    # =========================
    # REVIEW
    # =========================

    def create_review(self, review_data):
        user = self.user_repo.get(review_data["user_id"])
        place = self.place_repo.get(review_data["place_id"])

        if not place:
            raise ValueError("Place not found")
        if not user:
            raise ValueError("User not found")

        review = Review(**review_data)
        self.review_repo.add(review)

        if hasattr(place, 'add_review'):
            place.add_review(review)

        if USE_DATABASE:
            from hbnb.app import db
            db.session.commit()

        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [r for r in self.review_repo.get_all() if r.place_id == place_id]

    def get_reviews_by_user(self, user_id):
        return [r for r in self.review_repo.get_all() if r.user_id == user_id]

    def update_review(self, review_id, update_data):
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError("Review not found")
        review.update(update_data)
        return review

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError("Review not found")

        self.review_repo.delete(review_id)


# Singleton
facade = HBnBFacade()

