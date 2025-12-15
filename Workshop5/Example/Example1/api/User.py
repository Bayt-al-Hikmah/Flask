from flask import request, session
from flask_restful import Resource
from models import db
from models.User import User
from argon2 import PasswordHasher

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
          data = request.get_json()
          user.username = data.get('username', user.username)
          user.email = data.get('email', user.email)
          user.avatar = data.get('avatar', user.avatar)
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