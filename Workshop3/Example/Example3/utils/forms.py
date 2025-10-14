from wtforms import StringField, PasswordField, validators 
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=6)])

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class PageForm(FlaskForm):
    title = StringField("Title", validators=[validators.DataRequired()])
    content = CKEditorField("Content", validators=[validators.DataRequired()])