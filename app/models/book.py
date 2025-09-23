import json
import os
import random

class Book:
    def __init__(self, id, judul, penulis, tag, foto, deskripsi_singkat):
        self.id = id
        self.judul = judul
        self.penulis = penulis
        self.tag = tag
        self.foto = foto
        self.deskripsi_singkat = deskripsi_singkat

        # Backward compatibility properties
        self.title = judul
        self.author = penulis
        self.genre = tag
        self.cover_image = foto
        self.description = deskripsi_singkat

    @staticmethod
    def get_books_file():
        return 'data/books.json'

    @classmethod
    def get_all(cls):
        if not os.path.exists(cls.get_books_file()):
            return []
        with open(cls.get_books_file(), 'r', encoding='utf-8') as f:
            books_data = json.load(f)
            books = []
            for book_data in books_data:
                # Handle both old and new data structure
                if 'judul' in book_data:
                    # New structure
                    books.append(cls(
                        id=book_data['id'],
                        judul=book_data['judul'],
                        penulis=book_data['penulis'],
                        tag=book_data['tag'],
                        foto=book_data['foto'],
                        deskripsi_singkat=book_data['deskripsi_singkat']
                    ))
                else:
                    # Old structure - convert to new
                    books.append(cls(
                        id=book_data['id'],
                        judul=book_data['title'],
                        penulis=book_data['author'],
                        tag=book_data['genre'],
                        foto=book_data['cover_image'],
                        deskripsi_singkat=book_data['description']
                    ))
            return books

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
    def get_by_genre(cls, tags, exclude_ids=None):
        if exclude_ids is None:
            exclude_ids = []
        books = cls.get_all()
        filtered_books = []
        for book in books:
            if book.id not in exclude_ids:
                # Check if any of the book's tags match the requested tags
                if any(tag in book.tag for tag in tags):
                    filtered_books.append(book)
        return filtered_books

    @classmethod
    def get_recommendations_for_user(cls, user):
        if not user.favorites:
            # If no favorites, return random books
            return cls.get_random(6)

        # Get favorite books and extract tags
        favorite_tags = set()
        for fav_id in user.favorites:
            book = cls.get(fav_id)
            if book:
                favorite_tags.update(book.tag)

        if not favorite_tags:
            return cls.get_random(6)

        # Get books that match favorite tags (excluding already favorited)
        recommended_books = cls.get_by_genre(list(favorite_tags), exclude_ids=user.favorites)

        # If we don't have enough recommendations, add some random books
        if len(recommended_books) < 6:
            random_books = cls.get_random(6 - len(recommended_books))
            for book in random_books:
                if book.id not in user.favorites and book not in recommended_books:
                    recommended_books.append(book)

        # Shuffle and limit to 6
        random.shuffle(recommended_books)
        return recommended_books[:6]

    def save(self):
        """Save or update the book in the JSON file"""
        books = Book.get_all()
        # Update existing book or add new book
        for i, book in enumerate(books):
            if book.id == self.id:
                books[i] = self
                break
        else:
            books.append(self)

        # Save to file
        books_data = []
        for book in books:
            books_data.append({
                'id': book.id,
                'judul': book.judul,
                'penulis': book.penulis,
                'tag': book.tag,
                'foto': book.foto,
                'deskripsi_singkat': book.deskripsi_singkat
            })

        with open(self.get_books_file(), 'w', encoding='utf-8') as f:
            json.dump(books_data, f, indent=2, ensure_ascii=False)

    @classmethod
    def create(cls, judul, penulis, tag, foto, deskripsi_singkat):
        """Create a new book and save it"""
        # Generate new ID
        books = cls.get_all()
        max_id = 0
        for book in books:
            try:
                book_id = int(book.id)
                if book_id > max_id:
                    max_id = book_id
            except ValueError:
                pass

        new_id = str(max_id + 1)

        book = cls(
            id=new_id,
            judul=judul,
            penulis=penulis,
            tag=tag,
            foto=foto,
            deskripsi_singkat=deskripsi_singkat
        )
        book.save()
        return book

    def update(self, judul, penulis, tag, foto, deskripsi_singkat):
        """Update book details and save"""
        self.judul = judul
        self.penulis = penulis
        self.tag = tag
        self.foto = foto
        self.deskripsi_singkat = deskripsi_singkat

        # Update backward compatibility properties
        self.title = judul
        self.author = penulis
        self.genre = tag
        self.cover_image = foto
        self.description = deskripsi_singkat

        self.save()

    @classmethod
    def delete(cls, book_id):
        """Delete a book by ID"""
        books = cls.get_all()
        books = [book for book in books if book.id != book_id]

        # Save updated list
        books_data = []
        for book in books:
            books_data.append({
                'id': book.id,
                'judul': book.judul,
                'penulis': book.penulis,
                'tag': book.tag,
                'foto': book.foto,
                'deskripsi_singkat': book.deskripsi_singkat
            })

        with open(cls.get_books_file(), 'w', encoding='utf-8') as f:
            json.dump(books_data, f, indent=2, ensure_ascii=False)

        return True