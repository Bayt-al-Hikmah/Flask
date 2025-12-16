from flask import request
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils import verify_and_save_avatar

ph = PasswordHasher()

class UserResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity() 
        user = User.query.get(current_user_id)
        print("here")
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
        username = request.form.get('username', user.username)
        email = request.form.get('email', user.email)
        avatar_file = request.files.get('avatar')
        if avatar_file != None:
            (state,name) = verify_and_save_avatar(avatar_file)
            print(name)
            user.avatar = name or user.avatar
            if not state:
                return {"message": "not allowed file formate"}, 403
        
        user.username = username
        user.email = email
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