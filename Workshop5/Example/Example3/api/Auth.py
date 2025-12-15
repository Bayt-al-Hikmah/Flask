from flask import request
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher
from flask_jwt_extended import create_access_token
from limiter import limiter

ph = PasswordHasher()


class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        user = User(
            username=data['username'],
            email=data['email'],
            password=ph.hash(data['password']),   
            avatar=data.get('avatar')
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201

class LoginResource(Resource):
    @limiter.limit("5 per minute")
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        try:
            verified = ph.verify(user.password , data['password'])
        except:
            verified = False
        if not user or not verified :
            return {"message": "Invalid email or password"}, 401
        
        access_token = create_access_token(identity=user.id)
        return {"message": "Login successful", "access_token": access_token}, 200