from flask import request
from flask_restful import Resource
from models import db
from models.Task import Task
from flask_jwt_extended import jwt_required, get_jwt_identity
from limiter import limiter

class TaskListResource(Resource):
    @jwt_required()
    @limiter.limit("100 per minute", override_defaults=True)
    def get(self):
        current_user_id = get_jwt_identity() 
        tasks = Task.query.filter_by(user_id=current_user_id).all()
        return [
            {
                "id": task.id,
                "name": task.name,
                "state": task.state,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ], 200

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity() 
        data = request.get_json()
        task = Task(
            name=data['name'],
            user_id=current_user_id
        )
        db.session.add(task)
        db.session.commit()
        return {"message": "Task created successfully"}, 201

class TaskResource(Resource):
    @jwt_required()
    def put(self, task_id):
        current_user_id = get_jwt_identity() 
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()

        if not task:
            return {"message": "Task not found"}, 404

        data = request.get_json()
        task.name = data.get('name', task.name)
        task.state = data.get('state', task.state)
        db.session.commit()
        return {"message": "Task updated successfully"}, 200
    @jwt_required()
    def delete(self, task_id):
        current_user_id = get_jwt_identity() 
    
        task = Task.query.filter_by(
            id=task_id,
            user_id=current_user_id
        ).first()
        if not task:
            return {"message": "Task not found"}, 404
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deleted successfully"}, 200