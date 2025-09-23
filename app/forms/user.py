
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models.user import User

class UserForm(FlaskForm):
    nama = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama harus diisi'),
        Length(min=2, max=50, message='Nama harus antara 2-50 karakter')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email harus diisi'),
        Email(message='Format email tidak valid')
    ])
    role = SelectField('Role', choices=[
        ('pengguna', 'Pengguna'),
        ('admin', 'Admin')
    ], validators=[DataRequired(message='Role harus dipilih')])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password harus diisi'),
        Length(min=6, message='Password minimal 6 karakter')
    ])
    submit = SubmitField('Simpan')
    
    def validate_email(self, email):
        user = User.get_by_email(email.data)
        if user:
            raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain.')

class EditUserForm(FlaskForm):
    nama = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama harus diisi'),
        Length(min=2, max=50, message='Nama harus antara 2-50 karakter')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email harus diisi'),
        Email(message='Format email tidak valid')
    ])
    role = SelectField('Role', choices=[
        ('pengguna', 'Pengguna'),
        ('admin', 'Admin')
    ], validators=[DataRequired(message='Role harus dipilih')])
    password = PasswordField('Password Baru', validators=[
        Optional(),
        Length(min=6, message='Password minimal 6 karakter')
    ])
    submit = SubmitField('Update')
    
    def __init__(self, original_email=None, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.get_by_email(email.data)
            if user:
                raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain.')
