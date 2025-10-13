from flask import Blueprint, render_template

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks')
def tasks():
    task_list = [
        'Buy groceries',
        'Finish Flask workshop',
        'Go for a run'
    ]
    return render_template('tasks.html', tasks=task_list)