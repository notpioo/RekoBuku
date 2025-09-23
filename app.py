from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from functools import wraps
import os
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
# Require SESSION_SECRET to be set for security
if not os.environ.get('SESSION_SECRET'):
    raise RuntimeError('SESSION_SECRET environment variable must be set')
app.secret_key = os.environ.get('SESSION_SECRET')

# CSRF Protection
csrf = CSRFProtect(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Silakan masuk untuk mengakses halaman ini.'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.get(user_id)

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Import models and forms
from app.models.user import User
from app.models.book import Book
from app.forms.auth import LoginForm, RegisterForm
from app.forms.book import BookForm, EditBookForm
from app.forms.user import UserForm, EditUserForm

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        # Check if input is email or name
        user = User.get_by_email(form.email.data)
        if not user:
            # Try to find by name
            users = User.get_all()
            for u in users:
                if u.nama is not None and form.email.data and u.nama.lower() == form.email.data.lower():
                    user = u
                    break

        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Berhasil masuk!', 'success')
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            elif user.is_admin():
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Email/nama atau password salah', 'danger')

    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User.create(
            nama=form.nama.data,
            email=form.email.data,
            password=form.password.data
        )
        flash('Pendaftaran berhasil! Silakan masuk.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar', 'info')
    return redirect(url_for('home'))

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = len(User.get_all())
    total_books = len(Book.get_all())
    admin_users = [u for u in User.get_all() if u.is_admin()]
    regular_users = [u for u in User.get_all() if u.is_pengguna()]

    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_books=total_books,
                         admin_users=len(admin_users),
                         regular_users=len(regular_users))

@app.route('/admin/books')
@login_required
@admin_required
def admin_books():
    books = Book.get_all()
    return render_template('admin/books.html', books=books)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/nlp')
@login_required
@admin_required
def admin_nlp():
    return render_template('admin/nlp.html')

@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    return render_template('admin/settings.html')

# Book Management Routes
@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        foto_path = None
        if form.foto.data:
            # Create upload folder if it doesn't exist
            upload_folder = 'static/uploads/books'
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save the file
            filename = secure_filename(form.foto.data.filename)
            foto_full_path = os.path.join(upload_folder, filename)
            form.foto.data.save(foto_full_path)
            # Store the web-accessible path (with /static/ prefix)
            foto_path = f"/static/uploads/books/{filename}"

        Book.create(
            judul=form.judul.data,
            penulis=form.penulis.data,
            tag=form.tag.data,
            foto=foto_path,
            deskripsi_singkat=form.deskripsi_singkat.data
        )
        flash('Buku berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_books'))
    return render_template('admin/book_form.html', form=form, title='Tambah Buku Baru')

@app.route('/admin/books/edit/<book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    book = Book.get(book_id)
    if not book:
        flash('Buku tidak ditemukan', 'error')
        return redirect(url_for('admin_books'))

    form = EditBookForm(obj=book) # Use EditBookForm here
    if form.validate_on_submit():
        foto_path = book.foto # Keep existing photo if not updated
        if form.foto.data:
            # Create upload folder if it doesn't exist
            upload_folder = 'static/uploads/books'
            os.makedirs(upload_folder, exist_ok=True)

            # Save the new file
            filename = secure_filename(form.foto.data.filename)
            foto_full_path = os.path.join(upload_folder, filename)
            form.foto.data.save(foto_full_path)
            # Store the web-accessible path (with /static/ prefix)
            foto_path = f"/static/uploads/books/{filename}"
        
        book.update(
            judul=form.judul.data,
            penulis=form.penulis.data,
            tag=form.tag.data,
            foto=foto_path,
            deskripsi_singkat=form.deskripsi_singkat.data
        )
        flash('Buku berhasil diupdate!', 'success')
        return redirect(url_for('admin_books'))

    # Pre-populate form with current book data
    if request.method == 'GET':
        form.judul.data = book.judul
        form.penulis.data = book.penulis
        form.tag.data = book.tag
        # form.foto.data = book.foto # No need to set foto.data for EditBookForm
        form.deskripsi_singkat.data = book.deskripsi_singkat

    return render_template('admin/book_form.html', form=form, title='Edit Buku', book=book)

@app.route('/admin/books/delete/<book_id>', methods=['POST'])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.get(book_id)
    if not book:
        return jsonify({'error': 'Buku tidak ditemukan'}), 404

    Book.delete(book_id)
    flash('Buku berhasil dihapus!', 'success')
    return jsonify({'success': True, 'message': 'Buku berhasil dihapus!'})

# User Management Routes
@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        User.create(
            nama=form.nama.data,
            email=form.email.data,
            password=form.password.data
        )
        # Update role if it's not the default
        if form.role.data != 'pengguna':
            user = User.get_by_email(form.email.data)
            if user:
                user.role = form.role.data
                user.save()
        
        flash('Pengguna berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/user_form.html', form=form, title='Tambah Pengguna Baru')

@app.route('/admin/users/edit/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.get(user_id)
    if not user:
        flash('Pengguna tidak ditemukan', 'error')
        return redirect(url_for('admin_users'))

    form = EditUserForm(original_email=user.email)
    if form.validate_on_submit():
        password = form.password.data if form.password.data else None
        user.update(
            nama=form.nama.data,
            email=form.email.data,
            role=form.role.data,
            password=password
        )
        flash('Pengguna berhasil diupdate!', 'success')
        return redirect(url_for('admin_users'))

    # Pre-populate form with current user data
    if request.method == 'GET':
        form.nama.data = user.nama
        form.email.data = user.email
        form.role.data = user.role

    return render_template('admin/user_form.html', form=form, title='Edit Pengguna', user=user)

@app.route('/admin/users/delete/<user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.get(user_id)
    if not user:
        return jsonify({'error': 'Pengguna tidak ditemukan'}), 404
    
    # Prevent deleting admin users
    if user.is_admin():
        return jsonify({'error': 'Tidak dapat menghapus pengguna admin'}), 403
    
    # Prevent self-deletion
    if user.id == current_user.id:
        return jsonify({'error': 'Tidak dapat menghapus akun sendiri'}), 403

    User.delete(user_id)
    flash('Pengguna berhasil dihapus!', 'success')
    return jsonify({'success': True, 'message': 'Pengguna berhasil dihapus!'})

@app.route('/')
def home():
    # Get quick recommendations (random books) - limit to 7 for mobile scroll
    quick_recommendations = Book.get_random(7)

    # Get personalized recommendations - limit to 7 for mobile scroll
    if current_user.is_authenticated:
        personal_recommendations = Book.get_recommendations_for_user(current_user)[:7]
    else:
        personal_recommendations = Book.get_random(7)

    return render_template('home.html', 
                         quick_recommendations=quick_recommendations,
                         personal_recommendations=personal_recommendations)

@app.route('/jelajah')
@login_required
def jelajah():
    books = Book.get_all()
    return render_template('jelajah.html', books=books)

@app.route('/profil')
@login_required
def profil():
    # Get user's favorite books
    favorite_books = []
    for book_id in current_user.favorites:
        book = Book.get(book_id)
        if book:
            favorite_books.append(book)

    return render_template('profil.html', favorite_books=favorite_books)

@app.route('/book/<book_id>')
def book_detail(book_id):
    book = Book.get(book_id)
    if not book:
        flash('Buku tidak ditemukan', 'error')
        return redirect(url_for('home'))

    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = current_user.is_favorite(book_id)

    return render_template('book_detail.html', book=book, is_favorite=is_favorite)

@app.route('/toggle_favorite/<book_id>', methods=['POST'])
@login_required
def toggle_favorite(book_id):
    book = Book.get(book_id)
    if not book:
        return jsonify({'error': 'Buku tidak ditemukan'}), 404

    if current_user.is_favorite(book_id):
        current_user.remove_favorite(book_id)
        message = 'Buku dihapus dari favorit'
        is_favorite = False
    else:
        current_user.add_favorite(book_id)
        message = 'Buku ditambahkan ke favorit'
        is_favorite = True

    return jsonify({
        'message': message,
        'is_favorite': is_favorite
    })

def is_safe_url(target):
    """Check if the target URL is safe for redirects (prevents open redirect attacks)"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

if __name__ == '__main__':
    # Use debug mode only in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)