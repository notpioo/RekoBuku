
import json
import logging
import os
from typing import List, Dict, Any, Tuple, Optional
from io import BytesIO
from PIL import Image

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
    
    def detect_book_region(self, image_data: bytes, mime_type: str = "image/jpeg") -> Optional[Tuple[int, int, int, int]]:
        """
        Mendeteksi area/region buku dalam gambar menggunakan Gemini Vision
        
        Args:
            image_data: Binary data dari gambar
            mime_type: MIME type dari gambar
            
        Returns:
            Tuple (x, y, width, height) dalam persentase (0-100), atau None jika gagal
        """
        try:
            import base64
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Buat prompt untuk mendeteksi buku
            prompt = """
            Analisis gambar ini dan deteksi area cover buku.
            
            INSTRUKSI:
            1. Identifikasi lokasi cover buku dalam gambar
            2. Tentukan bounding box (kotak pembatas) untuk cover buku
            3. Berikan koordinat dalam PERSENTASE (0-100) dari ukuran gambar
            
            Format koordinat:
            - x: posisi kiri bounding box dari kiri gambar (%)
            - y: posisi atas bounding box dari atas gambar (%)
            - width: lebar bounding box (%)
            - height: tinggi bounding box (%)
            
            Contoh: Jika buku di tengah gambar mengambil 60% lebar dan 80% tinggi:
            {"x": 20, "y": 10, "width": 60, "height": 80}
            
            WAJIB BERIKAN RESPONS DALAM FORMAT JSON:
            {
                "found": true/false,
                "x": 0-100,
                "y": 0-100,
                "width": 0-100,
                "height": 0-100,
                "confidence": 0.0-1.0
            }
            
            Jika tidak ada buku yang terdeteksi, set "found": false
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type=mime_type
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            
            if response.text:
                result = json.loads(response.text)
                
                if result.get('found') and result.get('confidence', 0) > 0.5:
                    return (
                        int(result['x']),
                        int(result['y']),
                        int(result['width']),
                        int(result['height'])
                    )
            
            return None
                
        except Exception as e:
            logging.error(f"Error detecting book region: {str(e)}")
            return None
    
    def auto_crop_book(self, image_data: bytes, mime_type: str = "image/jpeg") -> Tuple[bytes, str]:
        """
        Auto-crop gambar ke area buku saja
        
        Args:
            image_data: Binary data dari gambar original
            mime_type: MIME type dari gambar
            
        Returns:
            Tuple (cropped_image_data, mime_type)
        """
        try:
            # Deteksi region buku
            region = self.detect_book_region(image_data, mime_type)
            
            # Jika tidak terdeteksi, return gambar original
            if region is None:
                logging.info("Book region not detected, using original image")
                return image_data, mime_type
            
            x_pct, y_pct, width_pct, height_pct = region
            
            # Load gambar dengan Pillow
            img = Image.open(BytesIO(image_data))
            img_width, img_height = img.size
            
            # Konversi persentase ke pixel
            x = int(img_width * x_pct / 100)
            y = int(img_height * y_pct / 100)
            width = int(img_width * width_pct / 100)
            height = int(img_height * height_pct / 100)
            
            # Crop dengan margin 2% untuk safety
            margin_x = int(width * 0.02)
            margin_y = int(height * 0.02)
            
            left = max(0, x - margin_x)
            top = max(0, y - margin_y)
            right = min(img_width, x + width + margin_x)
            bottom = min(img_height, y + height + margin_y)
            
            # Crop gambar
            cropped_img = img.crop((left, top, right, bottom))
            
            # Convert ke bytes
            output = BytesIO()
            img_format = 'JPEG' if mime_type == 'image/jpeg' else 'PNG'
            cropped_img.save(output, format=img_format, quality=95)
            cropped_data = output.getvalue()
            
            logging.info(f"Image cropped from {img.size} to {cropped_img.size}")
            return cropped_data, mime_type
            
        except Exception as e:
            logging.error(f"Error auto-cropping image: {str(e)}")
            # Return original jika gagal
            return image_data, mime_type
    
    def extract_book_info_from_image(self, image_data: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        Menggunakan Gemini Vision untuk mengekstrak informasi buku dari gambar
        
        Args:
            image_data: Binary data dari gambar buku
            mime_type: MIME type dari gambar (default: image/jpeg)
            
        Returns:
            Dictionary dengan informasi buku yang diekstrak
        """
        try:
            import base64
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Buat prompt untuk Gemini Vision
            # Daftar tag yang tersedia
            available_tags = [
                'Algoritma', 'Struktur Data', 'Pemrograman', 'Basis Data',
                'Kecerdasan Buatan', 'Pembelajaran Mesin', 'Sistem Operasi',
                'Jaringan Komputer', 'Keamanan Informatika', 'Komputasi Awan',
                'Data Science', 'Sistem Tertanam', 'Rekayasa Perangkat Lunak',
                'Manajemen Proyek', 'Manajemen Sumber Daya Manusia', 'Akuntansi',
                'Keuangan', 'Analisis Bisnis', 'Bisnis Digital', 'Pemasaran',
                'Ekonomi Mikro/Makro', 'Perilaku Organisasi', 'Audit Internal',
                'Teknik Lingkungan', 'Teknik Pertambangan', 'Teknik Elektro',
                'Teknik Mesin', 'Sistem Proses', 'Kontrol Otomatis', 'Robotika',
                'Arsitektur Komputer', 'Sistem Terdistribusi', 'Komputasi Paralel',
                'Pemrograman Web', 'Pemrograman Mobile', 'Internet of Things (IoT)',
                'Cloud Native', 'Containerization', 'Microservices', 'API Development',
                'Testing & QA', 'Code Review', 'Version Control', 'Dokumentasi Teknis',
                'Manajemen Database', 'Data Warehousing', 'Business Intelligence',
                'Visualisasi Data', 'Statistika Terapan', 'Riset Operasi', 'Optimasi',
                'Simulasi Sistem', 'Pemodelan Matematika', 'Kriptografi', 'Forensik Digital',
                'Etika Teknologi', 'Hukum Siber', 'Manajemen Risiko TI', 'Tata Kelola TI',
                'Audit Sistem'
            ]
            
            tags_list = ', '.join(available_tags)
            
            prompt = f"""
            Analisis gambar buku ini dengan sangat teliti dan ekstrak informasi berikut:
            
            INSTRUKSI:
            1. Baca dan identifikasi JUDUL BUKU dengan akurat (perhatikan huruf besar/kecil)
            2. Identifikasi NAMA PENULIS dengan lengkap
            3. Pilih 2-4 TAG yang PALING SESUAI dari daftar berikut:
               {tags_list}
               
               Pilih tag berdasarkan:
               - Topik utama buku yang terlihat dari judul dan cover
               - Kategori/bidang ilmu yang paling relevan
               - HANYA gunakan tag dari daftar di atas, JANGAN buat tag baru
               - Pilih tag yang paling spesifik dan sesuai
               
            4. Buat DESKRIPSI LENGKAP (MINIMAL 1300 KARAKTER) yang FOKUS pada topik utama buku:
               
               - Jelaskan apa topik utama buku ini secara detail
               - Apa saja yang dibahas dalam buku (konsep, metode, pembahasan)
               - Siapa target pembaca yang cocok (level, latar belakang)
               - Apa manfaat atau skill yang didapat setelah membaca
               - Bagaimana buku ini bisa diterapkan dalam praktik
            
            PENTING:
            - Jika ada teks dalam bahasa Indonesia, pertahankan bahasa Indonesia
            - Jika teks dalam bahasa Inggris, pertahankan bahasa Inggris
            - Pastikan judul dan penulis PERSIS seperti yang tertulis di buku
            - Tag HARUS dipilih dari daftar yang tersedia, jangan buat tag baru
            - Deskripsi HARUS MINIMAL 1300 KARAKTER (bukan kata), lebih panjang lebih baik
            - Fokus pada TOPIK UTAMA buku, bukan hal-hal umum
            - Gunakan bahasa yang informatif, profesional, dan menarik
            - Jelaskan secara DETAIL dan RELEVAN dengan isi buku
            - Hindari kalimat yang terlalu umum atau klise
            - Buat deskripsi dalam 1-2 paragraf yang padat informasi
            
            WAJIB BERIKAN RESPONS DALAM FORMAT JSON INI:
            {{
                "judul": "Judul Buku Lengkap",
                "penulis": "Nama Penulis Lengkap",
                "tag": ["Tag1", "Tag2", "Tag3"],
                "deskripsi_singkat": "Deskripsi singkat yang informatif tentang buku ini..."
            }}
            
            Jika gambar tidak jelas atau tidak bisa dibaca, berikan respons dengan field "error".
            """
            
            # Call Gemini Vision API
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(
                        data=image_data,
                        mime_type=mime_type
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2  # Lower temperature for more accurate extraction
                )
            )
            
            if response.text:
                try:
                    result = json.loads(response.text)
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to parse Gemini JSON response: {str(e)}")
                    return {"error": "AI memberikan respons yang tidak valid. Silakan coba lagi."}
                
                # Validate the result
                if 'error' in result:
                    return {"error": result.get('error', 'Tidak dapat membaca informasi dari gambar')}
                
                # Ensure all required fields are present
                required_fields = ['judul', 'penulis', 'tag', 'deskripsi_singkat']
                for field in required_fields:
                    if field not in result or not result[field]:
                        return {"error": f"Informasi {field} tidak dapat diekstrak dari gambar"}
                
                # Ensure tag is a list
                if isinstance(result['tag'], str):
                    result['tag'] = [result['tag']]
                
                logging.info(f"Successfully extracted book info: {result.get('judul', 'Unknown')}")
                return result
            else:
                return {"error": "Tidak ada respons dari AI"}
                
        except Exception as e:
            logging.error(f"Error in image analysis: {str(e)}")
            return {"error": f"Terjadi kesalahan saat menganalisis gambar: {str(e)}"}
    
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
