import os
from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory
from pathlib import Path
from models import db
from flask_restful import Api
from datetime import timedelta
from api.Auth import RegisterResource, LoginResource
from api.User import UserResource
from api.Tasks import TaskListResource, TaskResource
from flask_jwt_extended import JWTManager
from limiter import limiter
load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.config.update(
    JWT_SECRET_KEY=os.getenv("JWT_SECRET"),
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1)
)

jwt = JWTManager(app)

api = Api(app)
limiter.init_app(app)

api.add_resource(RegisterResource, '/api/register')
api.add_resource(LoginResource, '/api/login')
api.add_resource(UserResource, '/api/user')
api.add_resource(TaskListResource, '/api/tasks')
api.add_resource(TaskResource, '/api/tasks/<int:task_id>')


@app.route('/')
def index():
    return render_template('index.html')


UPLOAD_DIR = Path('./uploads/avatars')

@app.route('/uploads/avatars/<filename>')
def get_avatar(filename):
    return send_from_directory(UPLOAD_DIR, filename)


if __name__ == '__main__':
    app.run(debug=True)



