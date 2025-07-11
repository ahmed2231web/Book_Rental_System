# Book Rental System API

A complete Django REST API for managing book rentals with user authentication, book catalog management, and rental tracking.

## 🚀 Features

- **User Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (Admin/User)
  - Email-based login
  - User registration and profile management

- **Book Management**
  - CRUD operations for books
  - Advanced search and filtering
  - Inventory tracking (total and available copies)
  - ISBN validation

- **Rental Management**
  - Book rental and return system
  - Rental history tracking
  - Overdue detection
  - Rental period customization

- **Admin Features**
  - Dashboard statistics
  - User management
  - Complete rental oversight

- **API Documentation**
  - Auto-generated Swagger/OpenAPI documentation
  - Interactive API explorer

## 📋 Requirements

- Python 3.8+
- Django 5.2+
- PostgreSQL (for production) or SQLite (for development)
- All dependencies listed in `requirements.txt`

## ⚙️ Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd "Book Rental System"

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the project root:

```env
# Django settings
SECRET_KEY=your-super-secret-key-here
DEBUG=True

# Database settings (PostgreSQL)
USE_POSTGRESQL=true
DATABASE_NAME=book_rental_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# For development, you can use SQLite instead:
# USE_POSTGRESQL=false
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create sample data (optional)
python manage.py populate_data

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## 📚 API Documentation

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **Raw Schema**: `http://localhost:8000/api/schema/`

## 🔑 Authentication

The API uses JWT (JSON Web Tokens) for authentication. All endpoints except registration and login require authentication.

### Sample Users (after running populate_data)

- **Admin**: `admin@bookrental.com` / `admin123`
- **Users**: `user1@example.com` to `user5@example.com` / `password123`

## 📖 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register/` | User registration | No |
| POST | `/api/v1/auth/login/` | User login | No |
| POST | `/api/v1/auth/logout/` | User logout | Yes |
| POST | `/api/v1/auth/refresh/` | Refresh JWT token | No |
| GET/PATCH | `/api/v1/auth/profile/` | Get/Update user profile | Yes |

### Book Endpoints

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| GET | `/api/v1/books/` | List books (with search/filter) | Yes | No |
| POST | `/api/v1/books/` | Create book | Yes | Yes |
| GET | `/api/v1/books/{id}/` | Get book details | Yes | No |
| PATCH | `/api/v1/books/{id}/` | Update book | Yes | Yes |
| DELETE | `/api/v1/books/{id}/` | Delete book | Yes | Yes |

### Rental Endpoints

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| GET | `/api/v1/rentals/` | List rentals | Yes | No* |
| POST | `/api/v1/rentals/create/` | Rent a book | Yes | No |
| GET | `/api/v1/rentals/{id}/` | Get rental details | Yes | No* |
| POST | `/api/v1/rentals/return/` | Return a book | Yes | No |
| GET | `/api/v1/rentals/my/` | Get user's rentals | Yes | No |

*Users see only their own rentals, admins see all rentals.

### Admin Endpoints

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| GET | `/api/v1/users/` | List all users | Yes | Yes |
| GET | `/api/v1/users/{id}/` | Get user details | Yes | Yes |
| GET | `/api/v1/dashboard/stats/` | Dashboard statistics | Yes | Yes |

## 🧪 Testing with Postman

### 1. Setup Environment Variables

Create a Postman environment with these variables:
- `base_url`: `http://localhost:8000/api/v1`
- `access_token`: (will be set automatically after login)

### 2. Authentication Flow

#### Register a New User
```http
POST {{base_url}}/auth/register/
Content-Type: application/json

{
    "email": "newuser@example.com",
    "username": "newuser",
    "first_name": "New",
    "last_name": "User",
    "password": "securepass123",
    "password_confirm": "securepass123"
}
```

#### Login
```http
POST {{base_url}}/auth/login/
Content-Type: application/json

{
    "email": "user1@example.com",
    "password": "password123"
}
```

**Response**: Save the `access` token to your environment variable `access_token`.

### 3. Book Operations

#### List Books with Search
```http
GET {{base_url}}/books/?search=Harry&genre=fantasy&available_only=true
Authorization: Bearer {{access_token}}
```

#### Create Book (Admin Only)
```http
POST {{base_url}}/books/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "title": "New Amazing Book",
    "author": "Famous Author",
    "isbn": "9781234567890",
    "publication_date": "2023-01-01",
    "genre": "fiction",
    "description": "An amazing new book",
    "total_copies": 5,
    "available_copies": 5
}
```

### 4. Rental Operations

#### Rent a Book
```http
POST {{base_url}}/rentals/create/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "book": "book-uuid-here",
    "rental_period_days": 14
}
```

#### Return a Book
```http
POST {{base_url}}/rentals/return/
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
    "rental_id": "rental-uuid-here"
}
```

#### Get My Rentals
```http
GET {{base_url}}/rentals/my/
Authorization: Bearer {{access_token}}
```

## 🔍 Search & Filtering

### Book Search Parameters

- `search`: Search in title, author, description, or ISBN
- `genre`: Filter by genre (fiction, non_fiction, mystery, etc.)
- `author`: Filter by author name (partial match)
- `title`: Filter by title (partial match)
- `publication_year`: Filter by publication year
- `publication_year_gte`: Books published after or in this year
- `publication_year_lte`: Books published before or in this year
- `available_only`: Show only available books (true/false)
- `isbn`: Filter by ISBN (partial match)

### Rental Search Parameters

- `status`: Filter by rental status (active, returned, overdue)
- `user_email`: Filter by user email (admin only)
- `book_title`: Filter by book title
- `book_author`: Filter by book author
- `overdue_only`: Show only overdue rentals (true/false)
- `rented_after`: Rentals created after this date
- `rented_before`: Rentals created before this date

## 📊 Sample API Calls for Testing

### Complete User Journey

1. **Register** → `POST /auth/register/`
2. **Login** → `POST /auth/login/` (get JWT token)
3. **Browse Books** → `GET /books/?available_only=true`
4. **Search Books** → `GET /books/?search=Harry Potter`
5. **Rent a Book** → `POST /rentals/create/`
6. **View My Rentals** → `GET /rentals/my/`
7. **Return a Book** → `POST /rentals/return/`

### Admin Journey

1. **Login as Admin** → `POST /auth/login/`
2. **View Dashboard** → `GET /dashboard/stats/`
3. **Add New Book** → `POST /books/`
4. **View All Users** → `GET /users/`
5. **View All Rentals** → `GET /rentals/`

## 🏗️ Architecture

### Models

- **CustomUser**: Extended Django user with email login and role-based access
- **Book**: Book catalog with inventory tracking
- **Rental**: Rental records with status tracking

### Key Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Permissions**: Separate permissions for users and admins
- **Comprehensive Validation**: Input validation and business logic enforcement
- **Query Optimization**: Database query optimization with select_related
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test api.tests.AuthenticationTests

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🛠️ Development

### Project Structure

```
Book Rental System/
├── api/                    # Main API app
│   ├── models.py          # Database models
│   ├── serializers.py     # API serializers
│   ├── views.py           # API views
│   ├── permissions.py     # Custom permissions
│   ├── filters.py         # Search filters
│   ├── authentication.py  # Custom auth backend
│   └── tests.py           # Test suite
├── book_rental_project/   # Django project settings
└── requirements.txt       # Dependencies
```

### Adding New Features

1. Update models in `api/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Add serializers in `api/serializers.py`
4. Create views in `api/views.py`
5. Update URLs in `api/urls.py`
6. Add tests in `api/tests.py`
7. Run tests: `python manage.py test`

## 🚀 Deployment

For production deployment:

1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Set up proper SECRET_KEY
4. Configure static files serving
5. Set up proper CORS headers if needed
6. Use a production WSGI server (gunicorn, uwsgi)

## 📄 License

This project is for educational purposes.

---

**Happy coding! 🎉**

For questions or issues, please refer to the API documentation at `/api/docs/` when the server is running. 