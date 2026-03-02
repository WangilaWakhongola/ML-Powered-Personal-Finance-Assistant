# ML-Powered Personal Finance Assistant - Setup Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15 (for local development)
- Plaid API credentials ([Get them here](https://plaid.com))
- OpenAI API key ([Optional](https://platform.openai.com/))

## Quick Start with Docker

### 1. Clone Repository

```bash
git clone <repository-url>
cd ml-finance-assistant
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
```

### 3. Start Services

```bash
docker-compose up --build
```

### 4. Create Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 5. Access Applications

| Service | URL |
|---------|-----|
| **Web App** | http://localhost:3000 |
| **API** | http://localhost:8000/api/ |
| **API Docs** | http://localhost:8000/api/schema/swagger/ |
| **Admin** | http://localhost:8000/admin/ |

## Local Development Setup

### Backend

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database**
```bash
# Update DATABASE_URL in .env
export DATABASE_URL=postgresql://user:password@localhost:5432/ml_finance
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

### Frontend (React)

1. **Install dependencies**
```bash
cd frontend-web
npm install
```

2. **Configure environment**
```bash
# Create .env.local
echo "VITE_API_URL=http://localhost:8000/api" > .env.local
echo "VITE_PLAID_CLIENT_ID=your-client-id" >> .env.local
```

3. **Start development server**
```bash
npm run dev
```

### Mobile (React Native)

1. **Install Expo CLI**
```bash
npm install -g expo-cli
```

2. **Install dependencies**
```bash
cd frontend-mobile
npm install
```

3. **Start Expo server**
```bash
npm start
```

## Database Setup

### With Docker
Database automatically initializes when running `docker-compose up`.

### Local PostgreSQL

1. **Create database**
```bash
createdb ml_finance
createuser ml_finance_user
```

2. **Grant privileges**
```bash
psql -U postgres -d ml_finance -c "ALTER ROLE ml_finance_user WITH PASSWORD 'password';"
psql -U postgres -d ml_finance -c "GRANT ALL PRIVILEGES ON DATABASE ml_finance TO ml_finance_user;"
```

3. **Run migrations**
```bash
python manage.py migrate
```

## Training ML Models

### Expense Categorizer

```bash
python ml-models/training/train_categorizer.py \
  --data data/transactions.csv \
  --output backend/ml_models/trained_models/categorizer.pkl
```

### Spending Predictor

```bash
python ml-models/training/train_predictor.py \
  --data data/transactions.csv \
  --output backend/ml_models/trained_models/predictor.pkl
```

## Testing

### Backend Tests
```bash
python manage.py test
# or with coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests
```bash
npm test
```

## Plaid Integration

1. **Get API credentials** at https://plaid.com
2. **Add to .env**
```
PLAID_CLIENT_ID=your-client-id
PLAID_SECRET=your-secret
PLAID_ENV=sandbox  # or development, production
```

3. **Update frontend .env.local**
```
VITE_PLAID_CLIENT_ID=your-client-id
```

## OpenAI Integration (Optional)

1. **Get API key** at https://platform.openai.com
2. **Add to .env**
```
OPENAI_API_KEY=sk-...
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify credentials in .env
docker-compose logs db
```

### Docker Issues
```bash
# Rebuild everything
docker-compose down -v
docker-compose up --build

# Check service status
docker-compose ps
```

### Frontend Issues
```bash
# Clear cache
cd frontend-web
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Development Commands

### Using Makefile
```bash
make help              # Show all commands
make up               # Start all services
make test             # Run all tests
make lint             # Check code quality
make format           # Auto-format code
make migrate          # Run migrations
make db-reset         # Reset database
```

### Without Makefile

```bash
# Start services
docker-compose up

# Logs
docker-compose logs -f backend

# Shell
docker-compose exec backend python manage.py shell

# Create migrations
docker-compose exec backend python manage.py makemigrations

# Database backup
docker-compose exec db pg_dump -U postgres ml_finance > backup.sql

# Database restore
docker-compose exec -T db psql -U postgres ml_finance < backup.sql
```

## Code Quality

### Backend
```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Check imports
isort backend/
```

### Frontend
```bash
# Lint
npm run lint

# Format
npm run format
```

## Performance Optimization

### Caching
- Redis is configured for caching
- Set `CACHE_TIMEOUT` in settings

### Database Indexing
- Migrations include important indexes
- Monitor slow queries in logs

### ML Model Caching
- Models are cached in Redis
- Update interval configurable

## Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Enable `HTTPS` in production
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable 2FA for admin panel
- [ ] Regular security updates

## Deployment

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for production deployment guides.

## Support

- 📖 [Full Documentation](./docs/)
- 🐛 [Report Issues](https://github.com/yourusername/ml-finance-assistant/issues)
- 💬 [Discussions](https://github.com/yourusername/ml-finance-assistant/discussions)
