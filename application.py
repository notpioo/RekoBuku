from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from functools import wraps
import os
import logging
import re
from urllib.parse import urlparse, urljoin

# Load environment variables from .env file (optional - for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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

# Utility functions for book cover management
def generate_clean_filename(book_title, file_extension):
    """Generate a clean filename from book title"""
    clean_title = re.sub(r'[^\w\s-]', '', book_title.lower())
    clean_title = re.sub(r'[\s]+', '_', clean_title)
    clean_title = clean_title[:50]
    return f"{clean_title}.{file_extension}"

def delete_cover_file(foto_path):
    """Delete a cover file if it exists"""
    if not foto_path:
        return
    try:
        file_path = foto_path[1:] if foto_path.startswith('/') else foto_path
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted cover file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to delete cover file {foto_path}: {str(e)}")

def save_book_cover(image_file, book_title):
    """Save book cover with clean filename based on book title"""
    upload_folder = 'static/uploads/books'
    os.makedirs(upload_folder, exist_ok=True)

    filename = image_file.filename.lower()
    file_ext = filename.rsplit('.', 1)[1] if '.' in filename else 'jpg'

    clean_filename = generate_clean_filename(book_title, file_ext)
    foto_full_path = os.path.join(upload_folder, clean_filename)

    image_file.save(foto_full_path)

    return f"/static/uploads/books/{clean_filename}"

def cleanup_temp_files():
    """Clean up temporary preview files that are older than 1 hour"""
    upload_folder = 'static/uploads/books'
    if not os.path.exists(upload_folder):
        return

    import time
    current_time = time.time()
    for filename in os.listdir(upload_folder):
        if filename.startswith('temp_preview_') or filename.startswith('camera_capture_'):
            filepath = os.path.join(upload_folder, filename)
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > 3600:
                try:
                    os.remove(filepath)
                    logging.info(f"Cleaned up temp file: {filepath}")
                except Exception as e:
                    logging.error(f"Failed to clean up temp file {filepath}: {str(e)}")

# Apply maintenance check to all routes
@app.before_request
def check_maintenance():
    # Always allow access to static files and specific auth routes
    if request.endpoint == 'static' or request.endpoint is None:
        return None

    # Always allow access to authentication routes regardless of maintenance mode
    if request.endpoint in ['login', 'register'] or \
       request.path in ['/login', '/register']:
        return None

    # Always allow access to maintenance page
    if request.endpoint == 'maintenance_page' or request.path == '/maintenance':
        return None

    # Skip maintenance check for admin users
    if current_user.is_authenticated and current_user.is_admin():
        return None

    # Check if maintenance mode is enabled for all other routes
    if Settings.is_maintenance_mode():
        return render_template('maintenance.html'), 503

# Import models and forms
from app.models.user import User
from app.models.book import Book
from app.models.settings import Settings
try:
    from app.services.gemini_service import GeminiBookRecommendationService
except ImportError:
    GeminiBookRecommendationService = None
from app.forms.auth import LoginForm, RegisterForm
from app.forms.book import BookForm, EditBookForm, AIGenerateForm
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
    cleanup_temp_files()

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
    # Get current API key from environment
    current_api_key = os.environ.get('GEMINI_API_KEY', '')
    # Mask API key for security (show only last 8 characters)
    if current_api_key:
        masked_key = '*' * (len(current_api_key) - 8) + current_api_key[-8:] if len(current_api_key) > 8 else current_api_key
    else:
        masked_key = ''
    
    return render_template('admin/nlp.html', current_api_key=masked_key)

@app.route('/admin/update-api-key', methods=['POST'])
@login_required
@admin_required
def admin_update_api_key():
    api_key = request.form.get('api_key', '').strip()
    
    if not api_key:
        flash('API Key tidak boleh kosong!', 'danger')
        return redirect(url_for('admin_nlp'))
    
    try:
        # Update environment variable
        os.environ['GEMINI_API_KEY'] = api_key
        
        # Save to .env file for persistence
        env_file_path = '.env'
        env_lines = []
        
        # Read existing .env file
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add GEMINI_API_KEY
        key_found = False
        for i, line in enumerate(env_lines):
            if line.startswith('GEMINI_API_KEY='):
                env_lines[i] = f'GEMINI_API_KEY={api_key}\n'
                key_found = True
                break
        
        if not key_found:
            env_lines.append(f'GEMINI_API_KEY={api_key}\n')
        
        # Write back to .env file
        with open(env_file_path, 'w') as f:
            f.writelines(env_lines)
        
        flash('API Key berhasil diupdate dan disimpan!', 'success')
    except Exception as e:
        flash(f'Gagal menyimpan API Key: {str(e)}', 'danger')
    
    return redirect(url_for('admin_nlp'))

@app.route('/admin/ai-generate', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_ai_generate():
    form = AIGenerateForm()
    extracted_data = None
    preview_image = None

    if form.validate_on_submit():
        try:
            # Check if Gemini service is available
            if GeminiBookRecommendationService is None:
                flash('Layanan AI tidak tersedia. Pastikan GEMINI_API_KEY sudah diatur.', 'danger')
                return redirect(url_for('admin_ai_generate'))

            # Read image data
            image_file = form.foto.data
            image_data = image_file.read()

            # Detect MIME type and file extension
            import imghdr
            import time

            # Determine image type
            image_type = imghdr.what(None, h=image_data)
            if image_type is None:
                flash('Format gambar tidak valid!', 'danger')
                return redirect(url_for('admin_ai_generate'))

            # Map image type to MIME type and extension
            mime_type_map = {
                'jpeg': ('image/jpeg', 'jpg'),
                'jpg': ('image/jpeg', 'jpg'),
                'png': ('image/png', 'png'),
                'gif': ('image/gif', 'gif')
            }

            if image_type not in mime_type_map:
                flash(f'Format gambar {image_type} tidak didukung!', 'danger')
                return redirect(url_for('admin_ai_generate'))

            mime_type, file_ext = mime_type_map[image_type]

            # Save temporary preview image with correct extension
            upload_folder = 'static/uploads/books'
            os.makedirs(upload_folder, exist_ok=True)

            filename = f"temp_preview_{int(time.time())}.{file_ext}"
            preview_path = os.path.join(upload_folder, filename)

            # Save original image for preview
            with open(preview_path, 'wb') as f:
                f.write(image_data)

            preview_image = f"/static/uploads/books/{filename}"

            # Initialize Gemini service and extract book information
            gemini_service = GeminiBookRecommendationService()
            result = gemini_service.extract_book_info_from_image(image_data, mime_type=mime_type)

            if 'error' in result:
                flash(f'Gagal menganalisis gambar: {result["error"]}', 'danger')
            else:
                extracted_data = result
                flash('Informasi buku berhasil diekstrak! Silakan periksa dan edit jika perlu.', 'success')

        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return render_template('admin/ai_generate.html', 
                         form=form, 
                         extracted_data=extracted_data,
                         preview_image=preview_image)

@app.route('/admin/ai-generate/upload-cropped', methods=['POST'])
@login_required
@admin_required
def upload_cropped_image():
    """Upload cropped image and return new path"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if not file:
            return jsonify({'success': False, 'error': 'Empty file'}), 400

        # Get old temp preview path if provided
        old_preview_path = request.form.get('old_preview_path')

        # DELETE old temp_preview or cropped_image file FIRST, BEFORE saving new file
        if old_preview_path:
            # Clean up the path
            old_file_path = old_preview_path.replace('/static/', 'static/')
            if old_file_path.startswith('/'):
                old_file_path = old_file_path[1:]

            # Check if file exists and is a temp file
            if os.path.exists(old_file_path):
                if 'temp_preview_' in old_file_path or 'cropped_image_' in old_file_path:
                    try:
                        os.remove(old_file_path)
                        logging.info(f"✅ DELETED old temp file BEFORE saving new crop: {old_file_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to delete old temp file: {str(e)}")
                else:
                    logging.warning(f"⚠️ Skipping deletion - not a temp file: {old_file_path}")
            else:
                logging.warning(f"⚠️ File not found for deletion: {old_file_path}")

        # NOW save the new cropped file
        import time
        upload_folder = 'static/uploads/books'
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"cropped_image_{int(time.time())}.jpg"
        filepath = os.path.join(upload_folder, filename)

        file.save(filepath)
        logging.info(f"✅ Saved new cropped image: {filepath}")

        return jsonify({
            'success': True,
            'path': f"/static/uploads/books/{filename}"
        })
    except Exception as e:
        logging.error(f"❌ Error in upload_cropped_image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/ai-generate/save', methods=['POST'])
@login_required
@admin_required
def admin_ai_generate_save():
    """Save the AI-extracted book data"""
    try:
        judul = request.form.get('judul')
        penulis = request.form.get('penulis')
        tag = request.form.getlist('tag')
        deskripsi_singkat = request.form.get('deskripsi_singkat')
        temp_foto = request.form.get('foto')

        if not all([judul, penulis, tag, deskripsi_singkat]):
            flash('Semua field harus diisi!', 'danger')
            return redirect(url_for('admin_ai_generate'))

        foto_path = None
        if temp_foto:
            temp_file_path = temp_foto[1:] if temp_foto.startswith('/') else temp_foto
            if os.path.exists(temp_file_path):
                file_ext = temp_foto.rsplit('.', 1)[1] if '.' in temp_foto else 'jpg'
                clean_filename = generate_clean_filename(judul, file_ext)
                new_path = f"static/uploads/books/{clean_filename}"

                os.rename(temp_file_path, new_path)
                foto_path = f"/static/uploads/books/{clean_filename}"

        Book.create(
            judul=judul,
            penulis=penulis,
            tag=tag,
            foto=foto_path,
            deskripsi_singkat=deskripsi_singkat
        )

        flash('Buku berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_books'))

    except Exception as e:
        flash(f'Gagal menyimpan buku: {str(e)}', 'danger')
        return redirect(url_for('admin_ai_generate'))

@app.route('/admin/regenerate-book-info', methods=['POST'])
@login_required
@admin_required
def regenerate_book_info():
    """Regenerate book info from existing cover image"""
    try:
        # Check if Gemini service is available
        if GeminiBookRecommendationService is None:
            return jsonify({'error': 'Layanan AI tidak tersedia. Pastikan GEMINI_API_KEY sudah diatur.'}), 503

        # Get image path from request
        data = request.get_json()
        if not data or 'foto_path' not in data:
            return jsonify({'error': 'Path gambar tidak ditemukan'}), 400

        foto_path = data['foto_path']

        # Remove leading slash if exists and construct full path
        if foto_path.startswith('/'):
            foto_path = foto_path[1:]

        # Read image file
        try:
            with open(foto_path, 'rb') as f:
                image_data = f.read()
        except FileNotFoundError:
            return jsonify({'error': 'File gambar tidak ditemukan di server'}), 404
        except Exception as e:
            return jsonify({'error': f'Gagal membaca file gambar: {str(e)}'}), 500

        # Detect MIME type
        import imghdr
        image_type = imghdr.what(None, h=image_data)
        if image_type is None:
            return jsonify({'error': 'Format gambar tidak valid'}), 400

        # Map image type to MIME type
        mime_type_map = {
            'jpeg': 'image/jpeg',
            'jpg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }

        if image_type not in mime_type_map:
            return jsonify({'error': f'Format gambar {image_type} tidak didukung'}), 400

        mime_type = mime_type_map[image_type]

        # Initialize Gemini service
        gemini_service = GeminiBookRecommendationService()

        # Extract book information
        result = gemini_service.extract_book_info_from_image(image_data, mime_type=mime_type)

        if 'error' in result:
            return jsonify({'error': result['error']}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    if request.method == 'POST':
        # Handle recommendation settings update (check this first)
        if 'quick_count' in request.form and 'personal_count' in request.form:
            try:
                quick_count = int(request.form.get('quick_count', 7))
                personal_count = int(request.form.get('personal_count', 7))
                Settings.update_recommendations_count(quick_count, personal_count)
                flash('Pengaturan rekomendasi berhasil diupdate!', 'success')
            except ValueError:
                flash('Nilai pengaturan rekomendasi tidak valid!', 'danger')
            return redirect(url_for('admin_settings'))

        # Handle maintenance mode toggle
        else:
            maintenance_mode = 'maintenance_mode' in request.form
            Settings.set_maintenance_mode(maintenance_mode)

            action = 'diaktifkan' if maintenance_mode else 'dinonaktifkan'
            flash(f'Mode maintenance berhasil {action}!', 'success')
            return redirect(url_for('admin_settings'))

    maintenance_status = Settings.is_maintenance_mode()
    quick_count = Settings.get_quick_recommendations_count()
    personal_count = Settings.get_personal_recommendations_count()

    return render_template('admin/settings.html', 
                         maintenance_status=maintenance_status,
                         quick_count=quick_count,
                         personal_count=personal_count)

# Book Management Routes
@app.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        foto_path = None
        if form.foto.data and hasattr(form.foto.data, 'filename') and form.foto.data.filename:
            foto_path = save_book_cover(form.foto.data, form.judul.data)

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

    form = EditBookForm(obj=book)
    if form.validate_on_submit():
        foto_path = book.foto
        old_foto_path = book.foto

        if form.foto.data and hasattr(form.foto.data, 'filename') and form.foto.data.filename:
            delete_cover_file(old_foto_path)
            foto_path = save_book_cover(form.foto.data, form.judul.data)

        book.update(
            judul=form.judul.data,
            penulis=form.penulis.data,
            tag=form.tag.data,
            foto=foto_path,
            deskripsi_singkat=form.deskripsi_singkat.data
        )
        flash('Buku berhasil diupdate!', 'success')
        return redirect(url_for('admin_books'))

    if request.method == 'GET':
        form.judul.data = book.judul
        form.penulis.data = book.penulis
        form.tag.data = book.tag
        form.deskripsi_singkat.data = book.deskripsi_singkat

    return render_template('admin/book_form.html', form=form, title='Edit Buku', book=book)

@app.route('/admin/books/delete/<book_id>', methods=['POST'])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.get(book_id)
    if not book:
        return jsonify({'error': 'Buku tidak ditemukan'}), 404

    delete_cover_file(book.foto)
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
    # Get quick recommendations using settings
    quick_count = Settings.get_quick_recommendations_count()
    quick_recommendations = Book.get_random(quick_count)

    # Get personalized recommendations using settings
    personal_count = Settings.get_personal_recommendations_count()
    if current_user.is_authenticated:
        personal_recommendations = Book.get_recommendations_for_user(current_user)[:personal_count]
    else:
        personal_recommendations = Book.get_random(personal_count)

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

@app.route('/maintenance')
def maintenance_page():
    """Dedicated maintenance page route"""
    return render_template('maintenance.html'), 503

@app.route('/nlp-recommendation', methods=['POST'])
@login_required
def nlp_recommendation():
    """Handle NLP book recommendation requests"""
    import logging

    try:
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            logging.error("No query found in request")
            return jsonify({"error": "Query tidak ditemukan"}), 400

        user_query = data['query'].strip()
        if not user_query:
            logging.error("Empty query provided")
            return jsonify({"error": "Query tidak boleh kosong"}), 400

        logging.info(f"Processing NLP query: {user_query}")

        # Get all available books
        all_books = Book.get_all()
        if not all_books:
            logging.error("No books available")
            return jsonify({"error": "Belum ada buku tersedia"}), 404

        logging.info(f"Found {len(all_books)} books in database")

        # Convert books to dict format for Gemini
        books_data = []
        for book in all_books:
            books_data.append({
                'id': book.id,
                'judul': book.judul,
                'penulis': book.penulis,
                'tag': book.tag,
                'deskripsi_singkat': book.deskripsi_singkat
            })

        # Check if Gemini service is available
        try:
            gemini_service = GeminiBookRecommendationService()
            logging.info("Gemini service initialized successfully")
        except Exception as init_error:
            logging.error(f"Failed to initialize Gemini service: {str(init_error)}")
            # Return user-friendly error message
            return jsonify({
                "error": "Layanan AI rekomendasi sedang tidak tersedia. Silakan coba lagi dalam beberapa saat."
            }), 503

        # Get recommendations from Gemini
        logging.info("Getting recommendations from Gemini...")
        recommendation_result = gemini_service.get_book_recommendations(user_query, books_data)

        if 'error' in recommendation_result:
            logging.error(f"Gemini returned error: {recommendation_result['error']}")
            return jsonify({
                "error": "Layanan AI mengalami gangguan. Silakan coba dengan kata kunci yang berbeda atau coba lagi nanti."
            }), 503

        # Process recommended books
        recommended_books = []
        reasons = {}

        if 'recommended_books' in recommendation_result:
            logging.info(f"Found {len(recommendation_result['recommended_books'])} recommendations")
            for rec in recommendation_result['recommended_books']:
                book_id = rec.get('id')
                book = Book.get(book_id)
                if book:
                    book_dict = {
                        'id': book.id,
                        'judul': book.judul,
                        'penulis': book.penulis,
                        'tag': book.tag,
                        'foto': book.foto,
                        'deskripsi_singkat': book.deskripsi_singkat,
                        'is_favorite': current_user.is_favorite(book.id) if current_user.is_authenticated else False
                    }
                    recommended_books.append(book_dict)
                    reasons[book.id] = rec.get('reason', '')

        # Get similar books for the first recommended book
        similar_books = []
        if recommended_books:
            first_book_dict = {
                'id': recommended_books[0]['id'],
                'judul': recommended_books[0]['judul'],
                'penulis': recommended_books[0]['penulis'],
                'tag': recommended_books[0]['tag'],
                'deskripsi_singkat': recommended_books[0]['deskripsi_singkat']
            }

            similar_results = gemini_service.find_similar_books(first_book_dict, books_data, limit=3)

            for sim in similar_results:
                book_id = sim.get('id')
                book = Book.get(book_id)
                if book:
                    similar_books.append({
                        'id': book.id,
                        'judul': book.judul,
                        'penulis': book.penulis,
                        'tag': book.tag,
                        'foto': book.foto,
                        'deskripsi_singkat': book.deskripsi_singkat,
                        'is_favorite': current_user.is_favorite(book.id) if current_user.is_authenticated else False
                    })

        logging.info("Successfully processed NLP recommendation")
        response_data = {
            'books': recommended_books,
            'reasons': reasons,
            'explanation': recommendation_result.get('explanation', 'Berikut adalah rekomendasi buku berdasarkan pertanyaan Anda:'),
            'similar_books': similar_books
        }
        logging.info(f"Response data: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Unexpected error in NLP recommendation: {str(e)}")
        return jsonify({"error": f"Terjadi kesalahan yang tidak terduga: {str(e)}"}), 500

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