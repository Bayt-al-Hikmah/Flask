from flask import request, session
from flask_restful import Resource
from models import db
from models.Task import Task


def require_login():
     return 'user_id' in session

class TaskListResource(Resource):
     def get(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          tasks = Task.query.filter_by(user_id=session['user_id']).all()
          return [
               {
                    "id": task.id,
                    "name": task.name,
                    "state": task.state,
                    "created_at": task.created_at.isoformat()
               }
               for task in tasks
          ], 200

     def post(self):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          data = request.get_json()
          task = Task(
               name=data['name'],
               user_id=session['user_id']
          )
          db.session.add(task)
          db.session.commit()
          return {"message": "Task created successfully"}, 201

class TaskResource(Resource):
     def put(self, task_id):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          task = Task.query.filter_by(
               id=task_id,
               user_id=session['user_id']
          ).first()
          if not task:
               return {"message": "Task not found"}, 404
          data = request.get_json()
          task.name = data.get('name', task.name)
          task.state = data.get('state', task.state)
          db.session.commit()
          return {"message": "Task updated successfully"}, 200

     def delete(self, task_id):
          if not require_login():
               return {"message": "Unauthorized"}, 401
          task = Task.query.filter_by(
               id=task_id,
               user_id=session['user_id']
          ).first()
          if not task:
               return {"message": "Task not found"}, 404
          db.session.delete(task)
          db.session.commit()
          return {"message": "Task deleted successfully"}, 200