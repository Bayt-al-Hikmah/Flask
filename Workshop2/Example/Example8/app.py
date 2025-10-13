from flask import Flask
from routes import main,profile,tasks,dashboard,contact

# Create the Flask app instance
app = Flask(__name__)

# Register the blueprint with the main app
app.register_blueprint(main.main_bp)
app.register_blueprint(profile.profile_bp)
app.register_blueprint(tasks.tasks_bp)
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(contact.contact_bp)

if __name__ == '__main__':
    app.run(debug=True, port=3000)