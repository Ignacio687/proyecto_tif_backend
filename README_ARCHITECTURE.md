# TIF Backend API

A FastAPI-based backend service for a conversational AI assistant with Google OAuth authentication and user-specific conversation management.

## Architecture Overview

The application follows a clean architecture pattern with clear separation of responsibilities:

### 📁 Project Structure

```
app/
├── api/                    # API Controllers (REST endpoints)
│   ├── auth_controller.py     # Authentication endpoints
│   └── assistant_controller.py # Assistant interaction endpoints
├── models/                 # Data Models
│   ├── entities.py            # Database entities (Beanie ODM)
│   └── dtos.py               # Data Transfer Objects
├── repositories/           # Data Access Layer
│   ├── interfaces.py         # Repository interfaces
│   ├── user_repository.py    # User data operations
│   ├── conversation_repository.py # Conversation data operations
│   └── key_context_repository.py # Key context data operations
├── services/              # Business Logic Layer
│   ├── interfaces.py         # Service interfaces
│   ├── auth_service.py       # Authentication business logic
│   ├── assistant_service.py  # Assistant business logic
│   └── gemini_service.py     # Gemini AI integration
├── config.py             # Configuration settings
├── database.py           # Database initialization
├── dependencies.py       # Dependency injection container
├── logger.py            # Logging configuration
└── main.py              # Application entry point
```

## 🚀 Features

### Authentication
- **Google OAuth 2.0** integration for user authentication
- **JWT access/refresh token** system with configurable lifespans
- **Email registration and login** with verification codes
- **Password reset** functionality with secure codes
- **Token refresh** endpoint for seamless authentication
- Secure endpoint protection with bearer token authentication

### AI Assistant
- **Gemini AI** integration for intelligent conversations
- **User-specific conversation history** with pagination (20 conversations)
- **Long-term memory** with summarized context for personalized interactions
- **Context priority management** to maintain relevant information (30 contexts max)

### Data Management
- **MongoDB** with Beanie ODM for async operations
- **User isolation** - each user has their own conversation history and context
- **Scalable data models** with proper indexing for performance

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11+
- MongoDB instance (local or cloud)
- Google Cloud Project with OAuth 2.0 credentials
- Gemini API key

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=tif_db

# AI Service
GEMINI_API_KEY=your_gemini_api_key_here

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_SECONDS=3600
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here

# Application
LOG_LEVEL=INFO
DEBUG=False
```

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd proyecto_tif_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/google` - Authenticate with Google OAuth token
- `POST /api/v1/auth/register` - Register with email and username
- `POST /api/v1/auth/login` - Login with email/username and password
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token
- `POST /api/v1/auth/verify-token` - Verify JWT token
- `POST /api/v1/auth/verify-email` - Verify email with code
- `POST /api/v1/auth/resend-verification` - Resend verification code
- `POST /api/v1/auth/request-password-reset` - Request password reset
- `POST /api/v1/auth/confirm-password-reset` - Confirm password reset

#### Assistant
- `POST /api/v1/assistant` - Send message to assistant (requires authentication)
- `GET /api/v1/conversations` - Get conversation history (requires authentication)

## 🏗️ Architecture Patterns

### Dependency Injection
The application uses a dependency injection container (`app/dependencies.py`) to manage service instances and their dependencies. This promotes loose coupling, makes testing easier, and ensures singleton behavior for database connections.

### Repository Pattern
Data access is abstracted through repository interfaces, making it easy to swap data sources or add caching layers without changing business logic.

### Service Layer
Business logic is encapsulated in service classes, separating concerns from API controllers and data access.

### DTO (Data Transfer Objects)
Clear separation between internal data models (entities) and external API contracts (DTOs).

## 🔐 Security Features

- **JWT Access/Refresh Token** system with configurable lifespans
  - Access tokens: 3600 seconds (1 hour) by default
  - Refresh tokens: 7 days by default
- **Google OAuth 2.0** integration for secure user authentication
- **Email verification** for registration security
- **Password hashing** with PBKDF2-HMAC-SHA256 and salt
- **User isolation** - all data is user-specific
- **Input validation** with Pydantic models
- **Error handling** with sanitized error messages in production
- **Token type validation** (access vs refresh tokens)

## 🎯 User-Specific Features

### Conversation Management
- Each user has their own conversation history
- Pagination support for large conversation lists (20 conversations per fetch)
- Automatic conversation saving with metadata

### Intelligent Context Management
- **Long-term memory** through summarized context (30 contexts max)
- **Priority-based** context retention (1-100 scale)
- **Automatic context updates** based on AI recommendations
- **Context size limits** to maintain performance

### Personalization
- AI assistant remembers user preferences and information
- Context-aware responses based on conversation history
- Friendly, personalized interaction style

## 🚀 Deployment

### Docker Support
```bash
# Build the image
docker build -t tif-backend .

# Run the container
docker run -p 8000:8000 --env-file .env tif-backend
```

### Production Considerations
- Set `DEBUG=False` in production
- Use a strong `JWT_SECRET`
- Configure proper MongoDB replica sets for high availability
- Set up proper logging and monitoring
- Use HTTPS in production
- Configure CORS settings appropriately

## 🧪 Development

### Code Quality
- **Type hints** throughout the codebase
- **Async/await** pattern for database operations
- **Error handling** with proper logging
- **Modular design** with clear separation of concerns
- **Dependency injection** for better testability and loose coupling
- **Interface-based architecture** for maintainability

### Future Enhancements
- Unit and integration tests
- API rate limiting
- Caching layer for improved performance
- WebSocket support for real-time conversations
- Admin dashboard for user management
- Analytics and conversation insights
