from flask_wtf import Form
from wtforms.fields import TextField, PasswordField
from wtforms.validators import Required, Email


class RegisterForm(Form):
	email = TextField('Email', validators=[Required(), Email()])
	password = PasswordField('Password', validators=[Required()])

