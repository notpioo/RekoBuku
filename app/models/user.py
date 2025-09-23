import json
import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(UserMixin):
    def __init__(self, id, nama, email, password_hash, favorites=None, profile_image=None, role='pengguna'):
        self.id = id
        self.nama = nama
        self.email = email
        self.password_hash = password_hash
        self.favorites = favorites or []
        self.profile_image = profile_image or 'https://via.placeholder.com/40x40/6b7280/ffffff?text=User'
        self.role = role
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_users_file():
        return 'data/users.json'
    
    @classmethod
    def get_all(cls):
        if not os.path.exists(cls.get_users_file()):
            return []
        with open(cls.get_users_file(), 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            return [cls(**user_data) for user_data in users_data]
    
    @classmethod
    def get(cls, user_id):
        users = cls.get_all()
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    @classmethod
    def get_by_email(cls, email):
        users = cls.get_all()
        for user in users:
            if user.email == email:
                return user
        return None
    
    def save(self):
        users = User.get_all()
        # Update existing user or add new user
        for i, user in enumerate(users):
            if user.id == self.id:
                users[i] = self
                break
        else:
            users.append(self)
        
        # Save to file
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'nama': user.nama,
                'email': user.email,
                'password_hash': user.password_hash,
                'favorites': user.favorites,
                'profile_image': user.profile_image,
                'role': getattr(user, 'role', 'pengguna')
            })
        
        with open(self.get_users_file(), 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def create(cls, nama, email, password):
        password_hash = generate_password_hash(password)
        user = cls(
            id=str(uuid.uuid4()),
            nama=nama,
            email=email,
            password_hash=password_hash
        )
        user.save()
        return user
    
    def add_favorite(self, book_id):
        if book_id not in self.favorites:
            self.favorites.append(book_id)
            self.save()
    
    def remove_favorite(self, book_id):
        if book_id in self.favorites:
            self.favorites.remove(book_id)
            self.save()
    
    def is_favorite(self, book_id):
        return book_id in self.favorites
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_pengguna(self):
        return self.role == 'pengguna'