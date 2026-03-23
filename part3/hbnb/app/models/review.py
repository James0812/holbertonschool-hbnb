"""
hbnb/app/models/review.py
"""
import uuid
from datetime import datetime
 
from hbnb.app import db
from hbnb.app.models.base_model import BaseModel
 
 
class Review(BaseModel, db.Model):
    """Avis/évaluation d'un logement."""
    __tablename__ = "reviews"
 
    __table_args__ = (
        db.UniqueConstraint('user_id', 'place_id', name='uq_user_place_review'),
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_review_rating'),
        # extend_existing doit être dans le même tuple que les autres contraintes
        {"extend_existing": True},
    )
 
    id       = db.Column(db.String(36), primary_key=True,
                         default=lambda: str(uuid.uuid4()))
    text     = db.Column(db.Text,    nullable=False)
    rating   = db.Column(db.Integer, nullable=False)
    user_id  = db.Column(
        db.String(36),
        db.ForeignKey('users.id',  ondelete='CASCADE'),
        nullable=False,
    )
    place_id = db.Column(
        db.String(36),
        db.ForeignKey('places.id', ondelete='CASCADE'),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)
 
    # -------------------------------------------------------------------------
    # Relations
    # -------------------------------------------------------------------------
    user = db.relationship(
        'User',
        back_populates='reviews',
        lazy='select',
        foreign_keys=[user_id],
    )
    place = db.relationship(
        'Place',
        back_populates='reviews',
        lazy='select',
        foreign_keys=[place_id],
    )
 
    # -------------------------------------------------------------------------
    # Constructeur
    # -------------------------------------------------------------------------
    def __init__(self, text, rating, user_id, place_id, **kwargs):
        super().__init__(**kwargs)
 
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Review text is required")
        if len(text) > 1000:
            raise ValueError("Review text must not exceed 1000 characters")
 
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")
 
        self.text     = text
        self.rating   = rating
        self.user_id  = user_id
        self.place_id = place_id
 
    # -------------------------------------------------------------------------
    # Méthodes publiques
    # -------------------------------------------------------------------------
    def to_dict(self, include_user=False, include_place=False) -> dict:
        data = {
            'id':         self.id,
            'text':       self.text,
            'rating':     self.rating,
            'user_id':    self.user_id,
            'place_id':   self.place_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        if include_place and self.place:
            data['place'] = self.place.to_dict()
        return data
 
    def update(self, data: dict):
        if 'text' in data:
            if not isinstance(data['text'], str) or not data['text'].strip():
                raise ValueError("Review text is required")
            if len(data['text']) > 1000:
                raise ValueError("Review text must not exceed 1000 characters")
 
        if 'rating' in data:
            if not isinstance(data['rating'], int) or not (1 <= data['rating'] <= 5):
                raise ValueError("Rating must be an integer between 1 and 5")
 
        allowed = {'text', 'rating'}
        for key, value in data.items():
            if key in allowed:
                setattr(self, key, value)
        self.save()
 
    def __repr__(self):
        return f'<Review {self.rating}★ place={self.place_id}>'
 