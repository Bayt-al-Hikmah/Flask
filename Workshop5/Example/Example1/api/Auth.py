from flask import request, session
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher

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
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        try:
            verified = ph.verify(user.password , data['password'])
        except:
            verified = False
        if not user or not verified :
            return {"message": "Invalid email or password"}, 401
        
        session['user_id'] = user.id

        return {"message": "Login successful"}, 200