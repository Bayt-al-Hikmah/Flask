from flask import request, session
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher
from utils import verify_and_save_avatar

ph = PasswordHasher()

def require_login():
     return 'user_id' in session


class UserResource(Resource):
     def get(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          user = User.query.get(session['user_id'])
          return {
               "id": user.id,
               "username": user.username,
               "email": user.email,
               "avatar": user.avatar
          }, 200

     def put(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          user = User.query.get(session['user_id'])
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

     def patch(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          user = User.query.get(session['user_id'])
          data = request.get_json()
          user.password = ph.hash(data['password'])
          db.session.commit()
          return {"message": "Password updated successfully"}, 200