from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, TextField
from wtforms.validators import DataRequired, length as form_length
from flask_wtf.file import FileField, FileRequired


class UploadForm(FlaskForm):
    f = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Upload')


class PasteForm(FlaskForm):
    t = TextAreaField('Text', [DataRequired(), form_length(max=100000)])
    fname = TextField('Filename', [form_length(max=128)])
    submit = SubmitField('Paste')
