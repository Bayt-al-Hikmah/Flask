from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class SearchForm(FlaskForm):
    author = StringField('Author', validators=[DataRequired(), Length(min=3, max=25)])
    submit = SubmitField('Submit')

class ShareForm(FlaskForm):
    author = StringField('Author', validators=[DataRequired(), Length(min=3, max=25)])
    quote = TextAreaField('Quote', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')