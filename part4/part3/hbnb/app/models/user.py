"""
hbnb/app/models/user.py
"""
import re
import uuid
from datetime import datetime
 
from hbnb.app import db
from hbnb.app.models.base_model import BaseModel
 
 
class User(BaseModel, db.Model):
    """Utilisateur du système."""
    __tablename__ = "users"
 
    # Évite "Table already defined" lors de multiples appels à create_app()
    __table_args__ = {"extend_existing": True}
 
    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(50),  nullable=False)
    last_name  = db.Column(db.String(50),  nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False,
                           index=True)
    password   = db.Column(db.String(255), nullable=False)
    is_admin   = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)
 
    # -------------------------------------------------------------------------
    # Relations
    # -------------------------------------------------------------------------
    places = db.relationship(
        'Place',
        back_populates='owner',
        cascade='all, delete-orphan',
        lazy='select',
        foreign_keys='Place.owner_id',
    )
    reviews = db.relationship(
        'Review',
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='select',
        foreign_keys='Review.user_id',
    )
 
    # -------------------------------------------------------------------------
    # Constructeur
    # -------------------------------------------------------------------------
    def __init__(self, first_name, last_name, email, password,
                 is_admin=False, **kwargs):
        super().__init__(**kwargs)
 
        if not isinstance(first_name, str) or not first_name.strip():
            raise ValueError("First name is required")
        if len(first_name) > 50:
            raise ValueError("First name must not exceed 50 characters")
 
        if not isinstance(last_name, str) or not last_name.strip():
            raise ValueError("Last name is required")
        if len(last_name) > 50:
            raise ValueError("Last name must not exceed 50 characters")
 
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email is required")
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError("Invalid email format")
 
        if not isinstance(password, str) or not password.strip():
            raise ValueError("Password is required")
 
        self.first_name = first_name
        self.last_name  = last_name
        self.email      = email
        self.password   = password
        self.is_admin   = is_admin
 
    # -------------------------------------------------------------------------
    # Méthodes publiques
    # -------------------------------------------------------------------------
    def verify_password(self, raw_password: str) -> bool:
        """Vérifie un mot de passe en clair contre le hash stocké."""
        from hbnb.app.utils import check_password
        return check_password(self.password, raw_password)
 
    def to_dict(self) -> dict:
        """Sérialisation — le mot de passe est TOUJOURS exclu."""
        return {
            'id':         self.id,
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'email':      self.email,
            'is_admin':   self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
 
    def update(self, data: dict):
        """Mise à jour avec validations métier."""
        if 'first_name' in data:
            if not isinstance(data['first_name'], str) or not data['first_name'].strip():
                raise ValueError("First name is required")
            if len(data['first_name']) > 50:
                raise ValueError("First name must not exceed 50 characters")
 
        if 'last_name' in data:
            if not isinstance(data['last_name'], str) or not data['last_name'].strip():
                raise ValueError("Last name is required")
            if len(data['last_name']) > 50:
                raise ValueError("Last name must not exceed 50 characters")
 
        # email et password intentionnellement non modifiables ici
        allowed = {'first_name', 'last_name', 'is_admin'}
        for key, value in data.items():
            if key in allowed:
                setattr(self, key, value)
        self.save()
 
    def __repr__(self):
        return f'<User {self.email}>'
 