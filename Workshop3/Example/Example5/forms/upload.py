from wtforms import  validators,FileField
from flask_wtf import FlaskForm

class UploadForm(FlaskForm):
    avatar = FileField('Upload Avatar', validators=[validators.DataRequired()])