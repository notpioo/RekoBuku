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
        ('Robotika', 'Robotika'),
        ('Arsitektur Komputer', 'Arsitektur Komputer'),
        ('Sistem Terdistribusi', 'Sistem Terdistribusi'),
        ('Komputasi Paralel', 'Komputasi Paralel'),
        ('Pemrograman Web', 'Pemrograman Web'),
        ('Pemrograman Mobile', 'Pemrograman Mobile'),
        ('Internet of Things (IoT)', 'Internet of Things (IoT)'),
        ('Cloud Native', 'Cloud Native'),
        ('Containerization', 'Containerization'),
        ('Microservices', 'Microservices'),
        ('API Development', 'API Development'),
        ('Testing & QA', 'Testing & QA'),
        ('Code Review', 'Code Review'),
        ('Version Control', 'Version Control'),
        ('Dokumentasi Teknis', 'Dokumentasi Teknis'),
        ('Manajemen Database', 'Manajemen Database'),
        ('Data Warehousing', 'Data Warehousing'),
        ('Business Intelligence', 'Business Intelligence'),
        ('Visualisasi Data', 'Visualisasi Data'),
        ('Statistika Terapan', 'Statistika Terapan'),
        ('Riset Operasi', 'Riset Operasi'),
        ('Optimasi', 'Optimasi'),
        ('Simulasi Sistem', 'Simulasi Sistem'),
        ('Pemodelan Matematika', 'Pemodelan Matematika'),
        ('Kriptografi', 'Kriptografi'),
        ('Forensik Digital', 'Forensik Digital'),
        ('Etika Teknologi', 'Etika Teknologi'),
        ('Hukum Siber', 'Hukum Siber'),
        ('Manajemen Risiko TI', 'Manajemen Risiko TI'),
        ('Tata Kelola TI', 'Tata Kelola TI'),
        ('Audit Sistem', 'Audit Sistem')
    ], validators=[DataRequired(message='Pilih minimal satu tag')])

    foto = FileField('Foto Cover', validators=[
        DataRequired(message='Foto cover harus diupload'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message='Format file harus JPG, JPEG, PNG, atau GIF')
    ])
    deskripsi_singkat = TextAreaField('Deskripsi Singkat', validators=[
        DataRequired(message='Deskripsi singkat harus diisi'),
        Length(min=10, max=2000, message='Deskripsi harus antara 10-2000 karakter')
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
        ('Robotika', 'Robotika'),
        ('Arsitektur Komputer', 'Arsitektur Komputer'),
        ('Sistem Terdistribusi', 'Sistem Terdistribusi'),
        ('Komputasi Paralel', 'Komputasi Paralel'),
        ('Pemrograman Web', 'Pemrograman Web'),
        ('Pemrograman Mobile', 'Pemrograman Mobile'),
        ('Internet of Things (IoT)', 'Internet of Things (IoT)'),
        ('Cloud Native', 'Cloud Native'),
        ('Containerization', 'Containerization'),
        ('Microservices', 'Microservices'),
        ('API Development', 'API Development'),
        ('Testing & QA', 'Testing & QA'),
        ('Code Review', 'Code Review'),
        ('Version Control', 'Version Control'),
        ('Dokumentasi Teknis', 'Dokumentasi Teknis'),
        ('Manajemen Database', 'Manajemen Database'),
        ('Data Warehousing', 'Data Warehousing'),
        ('Business Intelligence', 'Business Intelligence'),
        ('Visualisasi Data', 'Visualisasi Data'),
        ('Statistika Terapan', 'Statistika Terapan'),
        ('Riset Operasi', 'Riset Operasi'),
        ('Optimasi', 'Optimasi'),
        ('Simulasi Sistem', 'Simulasi Sistem'),
        ('Pemodelan Matematika', 'Pemodelan Matematika'),
        ('Kriptografi', 'Kriptografi'),
        ('Forensik Digital', 'Forensik Digital'),
        ('Etika Teknologi', 'Etika Teknologi'),
        ('Hukum Siber', 'Hukum Siber'),
        ('Manajemen Risiko TI', 'Manajemen Risiko TI'),
        ('Tata Kelola TI', 'Tata Kelola TI'),
        ('Audit Sistem', 'Audit Sistem')
    ], validators=[DataRequired(message='Pilih minimal satu tag')])

    foto = FileField('Foto Cover (Opsional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message='Format file harus JPG, JPEG, PNG, atau GIF')
    ])
    deskripsi_singkat = TextAreaField('Deskripsi Singkat', validators=[
        DataRequired(message='Deskripsi singkat harus diisi'),
        Length(min=10, max=2000, message='Deskripsi harus antara 10-2000 karakter')
    ])
    submit = SubmitField('Update Buku')

class AIGenerateForm(FlaskForm):
    foto = FileField('Upload Gambar Buku', validators=[
        DataRequired(message='Gambar buku harus diupload'),
        FileAllowed(['jpg', 'jpeg', 'png'], message='Format file harus JPG, JPEG, atau PNG')
    ])
    submit = SubmitField('Analisis dengan AI')