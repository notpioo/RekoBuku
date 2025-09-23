
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length

class BookForm(FlaskForm):
    judul = StringField('Judul Buku', validators=[
        DataRequired(message='Judul buku harus diisi'),
        Length(min=1, max=200, message='Judul buku maksimal 200 karakter')
    ])
    penulis = StringField('Penulis', validators=[
        DataRequired(message='Penulis harus diisi'),
        Length(min=1, max=100, message='Nama penulis maksimal 100 karakter')
    ])
    tag = SelectMultipleField('Tag', choices=[
        ('Algoritma', 'Algoritma'),
        ('Struktur Data', 'Struktur Data'),
        ('Pemrograman', 'Pemrograman'),
        ('Basis Data', 'Basis Data'),
        ('Kecerdasan Buatan', 'Kecerdasan Buatan'),
        ('Pembelajaran Mesin', 'Pembelajaran Mesin'),
        ('Sistem Operasi', 'Sistem Operasi'),
        ('Jaringan Komputer', 'Jaringan Komputer'),
        ('Keamanan Informatika', 'Keamanan Informatika'),
        ('Komputasi Awan', 'Komputasi Awan'),
        ('Data Science', 'Data Science'),
        ('Sistem Tertanam', 'Sistem Tertanam'),
        ('Rekayasa Perangkat Lunak', 'Rekayasa Perangkat Lunak'),
        ('Manajemen Proyek', 'Manajemen Proyek'),
        ('Manajemen Sumber Daya Manusia', 'Manajemen Sumber Daya Manusia'),
        ('Akuntansi', 'Akuntansi'),
        ('Keuangan', 'Keuangan'),
        ('Analisis Bisnis', 'Analisis Bisnis'),
        ('Bisnis Digital', 'Bisnis Digital'),
        ('Pemasaran', 'Pemasaran'),
        ('Ekonomi Mikro/Makro', 'Ekonomi Mikro/Makro'),
        ('Perilaku Organisasi', 'Perilaku Organisasi'),
        ('Audit Internal', 'Audit Internal'),
        ('Teknik Lingkungan', 'Teknik Lingkungan'),
        ('Teknik Pertambangan', 'Teknik Pertambangan'),
        ('Teknik Elektro', 'Teknik Elektro'),
        ('Teknik Mesin', 'Teknik Mesin'),
        ('Sistem Proses', 'Sistem Proses'),
        ('Kontrol Otomatis', 'Kontrol Otomatis'),
        ('Robotika', 'Robotika')
    ], validators=[DataRequired(message='Pilih minimal satu tag')])
    
    foto = FileField('Foto Cover', validators=[
        DataRequired(message='Foto cover harus diupload'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message='Format file harus JPG, JPEG, PNG, atau GIF')
    ])
    deskripsi_singkat = TextAreaField('Deskripsi Singkat', validators=[
        DataRequired(message='Deskripsi singkat harus diisi'),
        Length(min=10, max=800, message='Deskripsi harus antara 10-800 karakter')
    ])
    submit = SubmitField('Simpan Buku')

class EditBookForm(FlaskForm):
    judul = StringField('Judul Buku', validators=[
        DataRequired(message='Judul buku harus diisi'),
        Length(min=1, max=200, message='Judul buku maksimal 200 karakter')
    ])
    penulis = StringField('Penulis', validators=[
        DataRequired(message='Penulis harus diisi'),
        Length(min=1, max=100, message='Nama penulis maksimal 100 karakter')
    ])
    tag = SelectMultipleField('Tag', choices=[
        ('Algoritma', 'Algoritma'),
        ('Struktur Data', 'Struktur Data'),
        ('Pemrograman', 'Pemrograman'),
        ('Basis Data', 'Basis Data'),
        ('Kecerdasan Buatan', 'Kecerdasan Buatan'),
        ('Pembelajaran Mesin', 'Pembelajaran Mesin'),
        ('Sistem Operasi', 'Sistem Operasi'),
        ('Jaringan Komputer', 'Jaringan Komputer'),
        ('Keamanan Informatika', 'Keamanan Informatika'),
        ('Komputasi Awan', 'Komputasi Awan'),
        ('Data Science', 'Data Science'),
        ('Sistem Tertanam', 'Sistem Tertanam'),
        ('Rekayasa Perangkat Lunak', 'Rekayasa Perangkat Lunak'),
        ('Manajemen Proyek', 'Manajemen Proyek'),
        ('Manajemen Sumber Daya Manusia', 'Manajemen Sumber Daya Manusia'),
        ('Akuntansi', 'Akuntansi'),
        ('Keuangan', 'Keuangan'),
        ('Analisis Bisnis', 'Analisis Bisnis'),
        ('Bisnis Digital', 'Bisnis Digital'),
        ('Pemasaran', 'Pemasaran'),
        ('Ekonomi Mikro/Makro', 'Ekonomi Mikro/Makro'),
        ('Perilaku Organisasi', 'Perilaku Organisasi'),
        ('Audit Internal', 'Audit Internal'),
        ('Teknik Lingkungan', 'Teknik Lingkungan'),
        ('Teknik Pertambangan', 'Teknik Pertambangan'),
        ('Teknik Elektro', 'Teknik Elektro'),
        ('Teknik Mesin', 'Teknik Mesin'),
        ('Sistem Proses', 'Sistem Proses'),
        ('Kontrol Otomatis', 'Kontrol Otomatis'),
        ('Robotika', 'Robotika')
    ], validators=[DataRequired(message='Pilih minimal satu tag')])
    
    foto = FileField('Foto Cover (Opsional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message='Format file harus JPG, JPEG, PNG, atau GIF')
    ])
    deskripsi_singkat = TextAreaField('Deskripsi Singkat', validators=[
        DataRequired(message='Deskripsi singkat harus diisi'),
        Length(min=10, max=800, message='Deskripsi harus antara 10-800 karakter')
    ])
    submit = SubmitField('Update Buku')
