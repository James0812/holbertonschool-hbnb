"""
hbnb/app/models/place_amenity.py
 
Ce fichier est conservé pour documentation.
La table d'association est définie dans hbnb/app/models/__init__.py
afin d'éviter les imports circulaires.
 
Schéma :
    place_amenity
    ├── place_id   FK → places.id   CASCADE DELETE
    └── amenity_id FK → amenities.id CASCADE DELETE
 
Les deux colonnes forment la clé primaire composite.
"""
 
# La table réelle est dans models/__init__.py :
#
#   place_amenity = db.Table(
#       'place_amenity',
#       db.Column('place_id',   db.String(36),
#                 db.ForeignKey('places.id',   ondelete='CASCADE'),
#                 primary_key=True),
#       db.Column('amenity_id', db.String(36),
#                 db.ForeignKey('amenities.id', ondelete='CASCADE'),
#                 primary_key=True),
#       extend_existing=True,
#   )
#
# Place.amenities et Amenity.places utilisent secondary='place_amenity'
# (référence par nom de table → aucun import circulaire).
