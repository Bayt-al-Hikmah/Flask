from wtforms import StringField, PasswordField, validators, TextAreaField
from flask_wtf import FlaskForm

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class PageForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    content = TextAreaField('Content', [validators.DataRequired()])