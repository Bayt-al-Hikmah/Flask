from wtforms import StringField, validators, TextAreaField
from flask_wtf import FlaskForm


class PageForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    content = TextAreaField('Content', [validators.DataRequired()])