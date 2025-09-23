from dotenv import load_dotenv
from app import app

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)