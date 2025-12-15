from flask import request
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher
from flask_jwt_extended import jwt_required, get_jwt_identity

ph = PasswordHasher()

class UserResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity() 
        user = User.query.get(current_user_id)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar
        }, 200

    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity() 
        user = User.query.get(current_user_id)
        data = request.get_json()

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.avatar = data.get('avatar', user.avatar)
        db.session.commit()
        return {"message": "User profile updated successfully"}, 200
    @jwt_required()
    def patch(self):
        current_user_id = get_jwt_identity() 
        user = User.query.get(current_user_id)
        data = request.get_json()

        user.password = ph.hash(data['password'])
        db.session.commit()
        return {"message": "Password updated successfully"}, 200