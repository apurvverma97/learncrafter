# LearnCrafter MVP

Interactive Content Generator System MVP - A modular, scalable platform for generating interactive learning content using LLMs.

## Architecture Overview

LearnCrafter MVP follows **SOLID principles** with a clean, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│                  Services Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Database  │ │     LLM     │ │ Validation  │           │
│  │   Service   │ │   Service   │ │   Service   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                  Models Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Schemas   │ │   Enums     │ │ Validation  │           │
│  │   (Pydantic)│ │   (Topics,  │ │   Rules     │           │
│  │             │ │   Levels)   │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                  Database Layer (Supabase)                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Courses   │ │   Modules   │ │  Concepts   │           │
│  │   Table     │ │   Table     │ │   Table     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## SOLID Principles Implementation

### 1. **Single Responsibility Principle (SRP)**
- Each service has one responsibility:
  - `DatabaseService`: Only database operations
  - `LLMService`: Only AI content generation
  - `ValidationService`: Only content validation
  - `PromptService`: Only prompt generation
  - `CourseService`: Handles AI-powered course content and structure generation

### 2. **Open/Closed Principle (OCP)**
- Services are open for extension, closed for modification
- New LLM providers can be added without changing existing code
- New validation rules can be added without modifying core validation logic

### 3. **Liskov Substitution Principle (LSP)**
- All services implement consistent interfaces
- Database operations are interchangeable
- LLM services follow the same contract

### 4. **Interface Segregation Principle (ISP)**
- API routes are separated by resource type
- Each route module handles only its specific resource
- Clean, focused interfaces for each service

### 5. **Dependency Inversion Principle (DIP)**
- High-level modules (API) depend on abstractions (services)
- Services are injected, not hardcoded
- Easy to swap implementations (e.g., different LLM providers)

## Database Schema

### Normalized Design
```
Courses (1) → (N) Modules (1) → (N) Concepts
```

### Tables
1. **courses**: Top-level course container
2. **modules**: Course subdivisions
3. **concepts**: Individual learning units with generated content

### Key Features
- UUID primary keys
- Cascading deletes
- Order indexing for sequences
- Array fields for learning objectives and prerequisites
- Row Level Security (RLS) policies
- Automatic timestamp management

## API Endpoints

### Course Management
- `POST /api/v1/courses/` - Create course
- `GET /api/v1/courses/` - List courses (with pagination/filtering)
- `GET /api/v1/courses/{id}` - Get specific course
- `PUT /api/v1/courses/{id}` - Update course
- `DELETE /api/v1/courses/{id}` - Delete course
- `GET /api/v1/courses/{id}/full` - Get course with nested modules/concepts

### Module Management
- `POST /api/v1/modules/` - Create module
- `GET /api/v1/modules/{id}` - Get specific module
- `PUT /api/v1/modules/{id}` - Update module
- `DELETE /api/v1/modules/{id}` - Delete module
- `GET /api/v1/modules/{id}/concepts` - Get module with concepts

### Concept Management
- `POST /api/v1/concepts/` - Create concept (auto-generates content)
- `GET /api/v1/concepts/{id}` - Get specific concept
- `PUT /api/v1/concepts/{id}` - Update concept metadata
- `DELETE /api/v1/concepts/{id}` - Delete concept
- `POST /api/v1/concepts/generate` - Generate content without storage
- `POST /api/v1/concepts/{id}/regenerate` - Regenerate concept content
- `POST /api/v1/concepts/{id}/validate` - Validate concept content

### Utility Endpoints
- `GET /health` - Health check
- `GET /topics` - Available course topics
- `GET /levels` - Available course levels

## Content Generation Pipeline

### 1. Prompt Generation
- Context-aware prompt building
- Learning objective integration
- Prerequisite consideration
- Level-specific instructions

### 2. LLM Integration
- OpenAI GPT-4 support
- Async API calls
- Error handling and retries
- Token management

### 3. Content Validation
- HTML structure validation
- JavaScript security scanning
- CSS validation
- Resource loading verification
- XSS prevention

### 4. Storage
- Supabase PostgreSQL
- Content versioning
- Metadata management
- Cascading relationships

## Security Features

### Content Security
- HTML tag whitelisting
- JavaScript AST analysis
- Dangerous pattern detection
- XSS prevention measures
- External resource validation

### API Security
- CORS configuration
- Input validation (Pydantic)
- Error message sanitization
- Rate limiting preparation
- Authentication ready

### Database Security
- Row Level Security (RLS)
- Connection encryption
- Query parameterization
- Access control policies

## Setup Instructions

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd learncrafter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create `.env` file:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Application Configuration
DEBUG=false
```

### 3. Database Setup
1. Create Supabase project
2. Run `database/schema.sql` in Supabase SQL editor
3. Update environment variables with your Supabase credentials

### 4. Run Application
```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Create a Course
```bash
curl -X POST "http://localhost:8000/api/v1/courses/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Programming",
    "description": "Learn Python from scratch",
    "topic": "programming",
    "level": "beginner"
  }'
```

### Create a Module
```bash
curl -X POST "http://localhost:8000/api/v1/modules/" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "course-uuid",
    "title": "Variables and Data Types",
    "description": "Understanding Python variables",
    "order_index": 1
  }'
```

### Create a Concept (Auto-generates content)
```bash
curl -X POST "http://localhost:8000/api/v1/concepts/" \
  -H "Content-Type: application/json" \
  -d '{
    "module_id": "module-uuid",
    "title": "String Variables",
    "description": "Working with text in Python",
    "order_index": 1,
    "learning_objectives": ["Understand string creation", "Learn string methods"],
    "prerequisites": ["Basic Python syntax"]
  }'
```

## Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Test Coverage
- Unit tests for each service
- Integration tests for API endpoints
- Security validation tests
- Content generation tests

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```env
DEBUG=false
SUPABASE_URL=your_production_supabase_url
SUPABASE_KEY=your_production_supabase_key
OPENAI_API_KEY=your_production_openai_key
```

## Performance Considerations

### Optimization Features
- Async request handling
- Database connection pooling
- Efficient query indexing
- Content caching preparation
- Pagination support

### Monitoring
- Health check endpoints
- Structured logging
- Error tracking
- Performance metrics preparation

## Future Enhancements

### Phase 2 Features
- Multiple LLM providers (Claude, Ollama)
- User authentication and authorization
- Content versioning and history
- Advanced validation rules
- Admin interface

### Phase 3 Features
- Analytics and usage tracking
- Content templates and themes
- Batch content generation
- Advanced security features
- Performance optimization

## Contributing

1. Follow SOLID principles
2. Write comprehensive tests
3. Update documentation
4. Use conventional commit messages
5. Ensure code quality and security

## License

MIT License - see LICENSE file for details.

## Support

For questions and support, please open an issue in the repository. 