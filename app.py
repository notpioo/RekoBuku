from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# CSRF Protection
csrf = CSRFProtect(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
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
                if u.nama and u.nama.lower() == form.email.data.lower():
                    user = u
                    break
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Berhasil masuk!', 'success')
            next_page = request.args.get('next')
            if next_page:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)