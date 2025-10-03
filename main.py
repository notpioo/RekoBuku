# Load environment variables from .env file (optional - for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from application import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)