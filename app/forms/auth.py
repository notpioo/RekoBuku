from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email atau Nama', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Masuk')

class RegisterForm(FlaskForm):
    nama = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama harus diisi'),
        Length(min=2, max=50, message='Nama harus antara 2-50 karakter')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email harus diisi'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password harus diisi'),
        Length(min=6, message='Password minimal 6 karakter')
    ])
    confirm_password = PasswordField('Konfirmasi Password', validators=[
        DataRequired(message='Konfirmasi password harus diisi'),
        EqualTo('password', message='Password tidak cocok')
    ])
    submit = SubmitField('Daftar')
    
    def validate_email(self, email):
        user = User.get_by_email(email.data)
        if user:
            raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain.')