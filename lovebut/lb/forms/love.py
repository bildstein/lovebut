"""
Form for change of screenname page
"""
from flask_wtf.form import Form
from wtforms.fields.simple import TextAreaField
from wtforms.validators import Length

class LoveForm(Form):  #IGNORE:R0924
    """
    Say something about someone
    """
    but = TextAreaField(validators=[Length(min=1)])