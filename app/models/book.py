import json
import os
import random

class Book:
    def __init__(self, id, title, author, genre, cover_image, description):
        self.id = id
        self.title = title
        self.author = author
        self.genre = genre
        self.cover_image = cover_image
        self.description = description
    
    @staticmethod
    def get_books_file():
        return 'data/books.json'
    
    @classmethod
    def get_all(cls):
        if not os.path.exists(cls.get_books_file()):
            return []
        with open(cls.get_books_file(), 'r', encoding='utf-8') as f:
            books_data = json.load(f)
            return [cls(**book_data) for book_data in books_data]
    
    @classmethod
    def get(cls, book_id):
        books = cls.get_all()
        for book in books:
            if book.id == book_id:
                return book
        return None
    
    @classmethod
    def get_random(cls, count=6):
        books = cls.get_all()
        if len(books) <= count:
            return books
        return random.sample(books, count)
    
    @classmethod
    def get_by_genre(cls, genres, exclude_ids=None):
        if exclude_ids is None:
            exclude_ids = []
        books = cls.get_all()
        filtered_books = []
        for book in books:
            if book.id not in exclude_ids:
                # Check if any of the book's genres match the requested genres
                if any(genre in book.genre for genre in genres):
                    filtered_books.append(book)
        return filtered_books
    
    @classmethod
    def get_recommendations_for_user(cls, user):
        if not user.favorites:
            # If no favorites, return random books
            return cls.get_random(6)
        
        # Get favorite books and extract genres
        favorite_genres = set()
        for fav_id in user.favorites:
            book = cls.get(fav_id)
            if book:
                favorite_genres.update(book.genre)
        
        if not favorite_genres:
            return cls.get_random(6)
        
        # Get books that match favorite genres (excluding already favorited)
        recommended_books = cls.get_by_genre(list(favorite_genres), exclude_ids=user.favorites)
        
        # If we don't have enough recommendations, add some random books
        if len(recommended_books) < 6:
            random_books = cls.get_random(6 - len(recommended_books))
            for book in random_books:
                if book.id not in user.favorites and book not in recommended_books:
                    recommended_books.append(book)
        
        # Shuffle and limit to 6
        random.shuffle(recommended_books)
        return recommended_books[:6]