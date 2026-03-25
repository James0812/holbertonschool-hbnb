"""
Authentication endpoints.
Handles user registration, login and JWT token generation.
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from hbnb.app.services import facade
from hbnb.app.utils import hash_password

api = Namespace('auth', description='Authentication operations')

# ============================
# MODELS
# ============================

register_model = api.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})


# ============================
# REGISTER
# ============================

@api.route('/register')
class Register(Resource):
    @api.expect(register_model, validate=True)
    def post(self):
        """Register a new user"""
        data = api.payload

        # Check if email already exists
        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400

        # Hash password
        data['password'] = hash_password(data['password'])

        # Create user
        user = facade.create_user(data)

        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }, 201


# ============================
# LOGIN
# ============================

@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload

        user = facade.get_user_by_email(credentials['email'])

        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )

        return {'access_token': access_token}, 200


# ============================
# PROTECTED TEST ROUTE
# ============================

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        """A protected endpoint that requires a valid JWT token"""
        current_user = get_jwt_identity()
        claims = get_jwt()

        return {
            'message': f'Hello, user {current_user}',
            'is_admin': claims.get('is_admin', False)
        }, 200

