# RekoBuku - Personal Book Recommendation System

## Overview

RekoBuku is a Flask-based web application that provides personalized book recommendations to users. The system allows users to browse a curated collection of Indonesian books, add favorites, and receive tailored recommendations based on their preferences. The application features user authentication, book discovery, and personal profile management with a clean, responsive interface built using Bootstrap.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 for responsive design and components
- **Styling**: Custom CSS with CSS variables for consistent theming
- **JavaScript**: Vanilla JavaScript for interactive features like favorite toggling
- **Icons**: Font Awesome for consistent iconography

### Backend Architecture
- **Framework**: Flask with modular structure using blueprints pattern
- **Authentication**: Flask-Login for session management and user authentication
- **Security**: Flask-WTF with CSRF protection for form security
- **Forms**: WTForms for form validation and rendering
- **Password Security**: Werkzeug for password hashing and verification

### Data Storage Solutions
- **User Data**: JSON file-based storage (`data/users.json`) for user profiles and authentication
- **Book Data**: JSON file-based storage (`data/books.json`) for book catalog and metadata
- **File Structure**: Simple file-based persistence suitable for small to medium datasets
- **Data Models**: Python classes with static methods for data access and manipulation

### Authentication and Authorization
- **Session Management**: Flask-Login with secure session handling
- **Password Hashing**: Werkzeug's secure password hashing
- **User Registration**: Email-based registration with validation
- **Login Methods**: Supports both email and username login
- **Access Control**: Login-required decorators for protected routes

### Application Structure
- **MVC Pattern**: Separation of models, views (templates), and controllers (routes)
- **Modular Design**: Organized into packages for models, forms, and templates
- **Static Assets**: Separate directories for CSS, JavaScript, and images
- **Template Inheritance**: Base template system for consistent layout

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and pre-built components
- **Font Awesome 6**: Icon library for user interface elements
- **CDN Delivery**: External CDN links for Bootstrap and Font Awesome resources

### Python Packages
- **Flask**: Core web framework for routing and request handling
- **Flask-Login**: User session management and authentication
- **Flask-WTF**: CSRF protection and form handling integration
- **WTForms**: Form validation, rendering, and data processing
- **Werkzeug**: Password hashing utilities and security functions

### Development Dependencies
- **Environment Variables**: Configuration through environment variables for security
- **JSON Processing**: Built-in Python JSON library for data persistence
- **UUID Generation**: Python UUID library for unique identifier generation
- **OS Module**: File system operations for data file management

### Static Resources
- **Placeholder Images**: Via.placeholder.com for book cover placeholders
- **Google Fonts**: Inter font family for typography (referenced in CSS)
- **Local Assets**: Custom CSS and JavaScript files served from static directory

## Project Status

### Replit Environment Setup (October 2025)
✅ **Successfully Migrated to Replit**: The application has been successfully configured to run in the Replit environment.

**Setup Changes:**
- Renamed `app.py` to `application.py` to avoid naming conflict with the `app/` package directory
- Updated `main.py` to import from `application` module
- Made dotenv dependency optional for Replit environment (uses Replit secrets instead)
- Configured workflow to use gunicorn on port 5000 with webview output
- Set up deployment configuration for autoscale deployment
- Added comprehensive .gitignore for Python projects

**Environment Variables Required:**
- `SESSION_SECRET`: Required for Flask session management (already configured in Replit)
- `GEMINI_API_KEY`: Optional - Required only if using AI-powered book recommendations

**Running the Application:**
- The app runs automatically via the configured workflow using gunicorn
- Access the app through the Replit webview
- Production-ready deployment configured for autoscale

### Implementation Complete (September 2025)
✅ **Fully Functional Web Application**: RekoBuku is now complete and running successfully on port 5000

**Key Features Implemented:**
- Three main navigation pages (Home, Jelajah, Profil) with proper access control
- Custom authentication system with login/register forms
- Book recommendation engine with quick and personalized recommendations
- AI-powered book recommendations using Google Gemini (optional)
- **AI Generate Feature**: Admin panel tool that uses Gemini Vision API to automatically extract book information (title, author, tags, description) from uploaded book cover images, eliminating manual data entry
- AJAX-powered favorite book system with CSRF protection
- Modern responsive UI with Bootstrap 5 and Font Awesome 6 icons
- JSON-based local database for users and books
- Security features including password hashing and session management
- Admin panel for managing books, users, and settings
- Maintenance mode feature for admin control

**Technical Highlights:**
- Modular Flask application structure with separate models, forms, and services
- Complete template system with base template inheritance
- Custom CSS styling with responsive design
- JavaScript functionality for interactive features
- Proper error handling and user feedback systems
- File upload support for book covers
- Gemini Vision integration with automatic MIME type detection (JPEG, PNG, GIF)
- Robust JSON parsing with error handling for AI responses
- Image preprocessing with imghdr for accurate format detection
- Temporary preview image system with correct file extensions