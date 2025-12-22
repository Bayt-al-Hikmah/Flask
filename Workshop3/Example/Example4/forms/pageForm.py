from wtforms import StringField, validators 
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField


class PageForm(FlaskForm):
    title = StringField("Title", validators=[validators.DataRequired()])
    content = CKEditorField("Content", validators=[validators.DataRequired()])