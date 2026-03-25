"""
Repository implementations for data persistence.
Supports both in-memory and SQLAlchemy-based persistence.
"""
from abc import ABC, abstractmethod

# Global storage for InMemoryRepository (persists across instances)
_GLOBAL_STORAGE = {}

class Repository(ABC):
    """Abstract base repository interface"""
    @abstractmethod
    def add(self, obj):
        pass
    @abstractmethod
    def get(self, obj_id):
        pass
    @abstractmethod
    def get_all(self):
        pass
    @abstractmethod
    def update(self, obj_id, data):
        pass
    @abstractmethod
    def delete(self, obj_id):
        pass
    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass

class InMemoryRepository(Repository):
    """In-memory repository implementation with global storage"""
    def __init__(self, model_class=None):
        self._model_class = model_class

    def add(self, obj):
        """Add object to global storage"""
        _GLOBAL_STORAGE[obj.id] = obj

    def get(self, obj_id):
        """Get object by ID from global storage"""
        return _GLOBAL_STORAGE.get(obj_id)

    def get_all(self):
        """Get all objects from global storage filtered by type"""
        if self._model_class:
            return [obj for obj in _GLOBAL_STORAGE.values() if isinstance(obj, self._model_class)]
        return list(_GLOBAL_STORAGE.values())

    def update(self, obj_id, data):
        """Update object in global storage"""
        obj = self.get(obj_id)
        if obj:
            obj.update(data)
            return obj
        return None

    def delete(self, obj_id):
        """Delete object from global storage"""
        if obj_id in _GLOBAL_STORAGE:
            del _GLOBAL_STORAGE[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        """Get object by attribute from global storage"""
        objects = self.get_all() if self._model_class else _GLOBAL_STORAGE.values()
        for obj in objects:
            if getattr(obj, attr_name, None) == attr_value:
                return obj
        return None

class SQLAlchemyRepository(Repository):
    """SQLAlchemy-based repository implementation"""
    def __init__(self, model):
        self.model = model

    def add(self, obj):
        """Add an object to the database"""
        from hbnb.app import db
        db.session.add(obj)
        db.session.commit()

    def get(self, obj_id):
        """Get an object by ID"""
        from hbnb.app import db
        return db.session.get(self.model, obj_id)

    def get_all(self):
        """Get all objects"""
        return self.model.query.all()

    def update(self, obj_id, data):
        """Update an object with new data"""
        from hbnb.app import db
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()
            return obj
        return None

    def delete(self, obj_id):
        """Delete an object by ID"""
        from hbnb.app import db
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()

    def get_by_attribute(self, attr_name, attr_value):
        """Get an object by a specific attribute"""
        return self.model.query.filter_by(**{attr_name: attr_value}).first()
