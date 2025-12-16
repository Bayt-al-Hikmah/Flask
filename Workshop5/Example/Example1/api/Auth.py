from flask import request, session
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher
from utils import verify_and_save_avatar

ph = PasswordHasher()

class RegisterResource(Resource):
    def post(self):
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        avatar_file = request.files.get('avatar')
        (state,filename) = verify_and_save_avatar(avatar_file)
        if not state:
            return {"message": "not allowed file formate"}, 403
        user = User(
            username=username,
            email=email,
            password=ph.hash(password), 
            avatar=filename
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