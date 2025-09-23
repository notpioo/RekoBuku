
import json
import logging
import os
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("Google GenAI not available")

class GeminiBookRecommendationService:
    def __init__(self):
        if not GENAI_AVAILABLE:
            raise ValueError("Google GenAI library is not available")
            
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.0-flash-exp"  # Use experimental model
            logging.info("Gemini client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini client: {str(e)}")
    
    def get_book_recommendations(self, user_query: str, available_books: List[Dict]) -> Dict[str, Any]:
        """
        Menggunakan Gemini untuk memberikan rekomendasi buku berdasarkan pertanyaan pengguna
        """
        try:
            # Format daftar buku yang tersedia
            books_list = self._format_books_for_prompt(available_books)
            
            # Buat prompt yang lebih detail untuk Gemini
            prompt = f"""
            Kamu adalah asisten ahli rekomendasi buku yang sangat pintar dalam menganalisis kebutuhan pembaca.

            PERTANYAAN PENGGUNA: "{user_query}"

            DAFTAR BUKU YANG TERSEDIA:
            {books_list}

            INSTRUKSI ANALISIS:
            1. Analisis pertanyaan pengguna dengan cermat untuk memahami:
               - Genre yang diinginkan (romance, thriller, motivasi, dll)
               - Mood atau suasana hati (ringan, serius, menghibur, dll)
               - Target pembaca (anak muda, dewasa, remaja, dll)
               - Tema spesifik (petualangan, cinta, bisnis, self-improvement, dll)
               
            2. Untuk setiap buku, cocokkan dengan pertanyaan berdasarkan:
               - JUDUL: Apakah judul mencerminkan tema yang dicari?
               - TAG/GENRE: Apakah genre sesuai dengan yang diminta?
               - DESKRIPSI: Apakah deskripsi menjelaskan konten yang relevan?
               
            3. Berikan skor relevansi 0.0-1.0 berdasarkan seberapa cocok buku dengan pertanyaan
            
            4. Pilih 3-6 buku dengan skor tertinggi (minimal 0.6)

            CONTOH PENALARAN:
            - Jika user cari "buku motivasi untuk anak muda" → cari tag "Motivasi", "Self-Help" dan deskripsi yang menyebutkan "inspirasi", "semangat", dll
            - Jika user cari "novel romance ringan" → cari tag "Romance", "Fiction" dan deskripsi yang tidak terlalu drama/berat
            - Jika user cari "buku tentang algoritma" → cari judul/deskripsi yang menyebutkan "algoritma", "programming", "komputer"

            WAJIB BERIKAN RESPONS DALAM FORMAT JSON INI:
            {{
                "recommended_books": [
                    {{
                        "id": "book_id",
                        "relevance_score": 0.95,
                        "reason": "Penjelasan detail mengapa buku ini cocok berdasarkan judul/tag/deskripsi yang sesuai dengan permintaan user"
                    }}
                ],
                "explanation": "Penjelasan umum tentang kriteria pencarian dan mengapa rekomendasi ini dipilih"
            }}
            
            PENTING: Hanya rekomendasikan buku yang benar-benar relevan dengan pertanyaan. Jangan memaksa merekomendasikan jika tidak ada yang cocok.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3  # Lower temperature for more consistent results
                )
            )
            
            if response.text:
                result = json.loads(response.text)
                # Filter books with relevance score >= 0.6
                if 'recommended_books' in result:
                    filtered_books = [
                        book for book in result['recommended_books'] 
                        if book.get('relevance_score', 0) >= 0.6
                    ]
                    result['recommended_books'] = filtered_books
                return result
            else:
                return {"error": "Tidak ada respons dari AI"}
                
        except Exception as e:
            logging.error(f"Error in Gemini recommendation: {str(e)}")
            return {"error": "Layanan AI rekomendasi sedang tidak tersedia. Silakan coba lagi nanti."}
    
    def find_similar_books(self, target_book: Dict, available_books: List[Dict], limit: int = 4) -> List[Dict]:
        """
        Mencari buku-buku yang mirip dengan buku target menggunakan Gemini
        """
        try:
            # Format buku target dan daftar buku
            target_info = f"""
            BUKU TARGET:
            - Judul: {target_book.get('judul', '')}
            - Penulis: {target_book.get('penulis', '')}
            - Tag/Genre: {target_book.get('tag', [])}
            - Deskripsi: {target_book.get('deskripsi_singkat', '')}
            """
            
            books_list = self._format_books_for_prompt([book for book in available_books if book.get('id') != target_book.get('id')])
            
            prompt = f"""
            {target_info}
            
            DAFTAR BUKU YANG TERSEDIA:
            {books_list}
            
            INSTRUKSI:
            Cari {limit} buku yang paling mirip dengan buku target berdasarkan:
            1. GENRE/TAG yang sama atau serupa
            2. TEMA yang mirip dari deskripsi
            3. GAYA atau SUASANA cerita yang sejenis
            
            Berikan skor kemiripan 0.0-1.0 dan alasan yang jelas.
            
            FORMAT RESPONS JSON:
            {{
                "similar_books": [
                    {{
                        "id": "book_id",
                        "similarity_score": 0.85,
                        "reason": "Alasan kemiripan berdasarkan genre/tema/gaya"
                    }}
                ]
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            if response.text:
                result = json.loads(response.text)
                return result.get("similar_books", [])
            else:
                return []
                
        except Exception as e:
            logging.error(f"Error finding similar books: {str(e)}")
            return []
    
    def _format_books_for_prompt(self, books: List[Dict]) -> str:
        """
        Format daftar buku untuk prompt Gemini dengan informasi lengkap
        """
        formatted_books = []
        for i, book in enumerate(books, 1):
            book_info = f"""
{i}. ID: {book.get('id', '')}
   Judul: "{book.get('judul', '')}"
   Penulis: {book.get('penulis', '')}
   Tag/Genre: {book.get('tag', [])}
   Deskripsi: "{book.get('deskripsi_singkat', '')}"
            """.strip()
            formatted_books.append(book_info)
        
        return "\n\n".join(formatted_books)
